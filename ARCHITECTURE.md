# Architecture Deep Dive

Technical architecture documentation for the Missing Job Roles AI Agent system.

## System Overview

This document explains the technical decisions, architecture patterns, and implementation details.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│  - REST API Endpoints (Django REST Framework)           │
│  - Django Admin Interface                               │
│  - API Documentation                                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   Business Logic Layer                   │
│  - ViewSets (API Controllers)                           │
│  - Serializers (Data Validation)                        │
│  - Analysis Orchestration                               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   AI Processing Layer                    │
│  - LangGraph Workflow Engine                            │
│  - Multi-Agent System (5 Agents)                        │
│  - LLM Integration (OpenAI/Anthropic)                   │
│  - State Management                                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Access Layer                      │
│  - Django ORM                                           │
│  - MySQL Database                                       │
│  - Models (JobRole, Employee, AnalysisRun)              │
└─────────────────────────────────────────────────────────┘
```

---

## Multi-Agent Workflow Design

### Why Multi-Agent Instead of Single Prompt?

**Single Prompt Approach** (What we DON'T do):
```python
# ❌ Too simplistic
prompt = "Analyze this organization and find missing roles"
response = llm(prompt)
```

**Problems:**
- Too much complexity in one prompt
- No structured reasoning
- Hard to debug
- Poor quality outputs
- Can't track which analysis dimension found what

**Multi-Agent Approach** (What we DO):
```python
# ✅ Structured reasoning
workflow = [
    org_structure_analyzer,    # Focuses on hierarchy
    responsibility_analyzer,   # Focuses on coverage
    workload_analyzer,        # Focuses on capacity
    skills_analyzer,          # Focuses on competencies
    synthesizer               # Combines findings
]
```

**Benefits:**
- ✅ Specialized expertise per agent
- ✅ Structured, debuggable workflow
- ✅ Better quality per dimension
- ✅ Traceable reasoning
- ✅ Each agent builds on previous findings

### Agent Communication Pattern

```
┌──────────────────────────────────────────────────────┐
│              Shared State (TypedDict)                 │
│  - job_roles: List[Dict]                             │
│  - employees: List[Dict]                             │
│  - org_structure_analysis: str                       │
│  - responsibility_analysis: str                      │
│  - workload_analysis: str                            │
│  - skills_analysis: str                              │
│  - recommendations: List[Dict]                       │
└──────────────────────────────────────────────────────┘
         ↓              ↓              ↓
    Agent 1        Agent 2        Agent 3
    Reads &        Reads &        Reads &
    Writes         Writes         Writes
```

**Key Pattern**: Each agent:
1. Reads current state (including previous agent outputs)
2. Performs specialized analysis
3. Writes findings to state
4. Passes state to next agent

---

## LangGraph Workflow Implementation

### Why LangGraph Over LangChain Chains?

| Feature | LangChain Chains | LangGraph |
|---------|------------------|-----------|
| State Management | No built-in state | ✅ Persistent state |
| Conditional Logic | Limited | ✅ Full control |
| Cycles/Loops | Difficult | ✅ Native support |
| Agent Coordination | Manual | ✅ Built-in |
| Debugging | Harder | ✅ Easier (graph visualization) |
| Complexity | Simple tasks | ✅ Complex workflows |

### Graph Structure

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AnalysisState)

# Linear workflow (could be conditional in future)
workflow.set_entry_point("org_structure")
workflow.add_edge("org_structure", "responsibilities")
workflow.add_edge("responsibilities", "workload")
workflow.add_edge("workload", "skills")
workflow.add_edge("skills", "synthesize")
workflow.add_edge("synthesize", END)
```

**Why Sequential, Not Parallel?**

We could parallelize agents 1-4, but sequential is better because:
- Later agents benefit from earlier insights
- More coherent narrative
- Synthesizer needs all analyses complete
- Better reasoning quality

**Future Enhancement**: Add conditional routing:
```python
def should_deep_dive(state):
    """Decide if specific analysis needs deeper investigation"""
    if state['org_structure_analysis'].contains('critical'):
        return "deep_dive_org"
    return "continue"

workflow.add_conditional_edges("org_structure", should_deep_dive)
```

---

## Database Schema Design

### Core Tables

#### 1. job_roles
```sql
CREATE TABLE job_roles (
    role_id VARCHAR(50) PRIMARY KEY,
    role_title VARCHAR(200),
    department VARCHAR(100),
    level VARCHAR(20),
    responsibilities JSON,          -- Array of strings
    required_skills JSON,           -- Array of strings
    reports_to VARCHAR(50),         -- FK to role_id (self-reference)
    current_headcount INT,
    team_size INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_department (department),
    INDEX idx_level (level)
);
```

#### 2. employees
```sql
CREATE TABLE employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(255),
    role_id VARCHAR(50),            -- FK to job_roles
    department VARCHAR(100),
    hire_date DATE,
    workload_status VARCHAR(20),    -- 'underutilized', 'normal', 'overloaded'
    skills JSON,                    -- Array of strings
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES job_roles(role_id),
    INDEX idx_department (department),
    INDEX idx_workload (workload_status)
);
```

#### 3. analysis_runs
```sql
CREATE TABLE analysis_runs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20),             -- 'pending', 'running', 'completed', 'failed'
    total_roles_analyzed INT,
    total_employees_analyzed INT,
    departments_analyzed JSON,
    execution_time_seconds FLOAT,
    error_message TEXT,
    
    -- Agent findings
    org_structure_gaps TEXT,
    responsibility_gaps TEXT,
    workload_gaps TEXT,
    skills_gaps TEXT,
    
    -- Final output
    recommendations JSON,           -- Array of recommendation objects
    
    INDEX idx_status (status),
    INDEX idx_run_date (run_date)
);
```

#### 4. missing_roles
```sql
CREATE TABLE missing_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_run_id INT,            -- FK to analysis_runs
    recommended_role_title VARCHAR(200),
    department VARCHAR(100),
    level VARCHAR(20),
    gap_type VARCHAR(100),          -- 'structural', 'skills', 'workload', 'responsibility'
    justification TEXT,
    expected_impact TEXT,
    priority VARCHAR(20),           -- 'critical', 'high', 'medium', 'low'
    recommended_headcount INT,
    estimated_timeline VARCHAR(100),
    required_skills JSON,
    responsibilities JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(id),
    INDEX idx_priority (priority),
    INDEX idx_department (department)
);
```

### Design Decisions

**Why JSON fields instead of separate tables?**

We use JSON for `responsibilities` and `skills` because:
- ✅ Variable length lists (not fixed schema)
- ✅ Read-heavy workload (rarely need to query individual skills)
- ✅ Simpler schema
- ✅ Better for AI processing (already in list format)

**Trade-off**: Can't easily query "all roles requiring Python skill" without full table scan. If needed later, can add a separate `role_skills` junction table.

**Why duplicate `department` in employees table?**

Denormalization for performance:
- ✅ Avoid JOIN on every employee query
- ✅ Department rarely changes
- ✅ Makes workload queries much faster

---

## API Design Patterns

### REST API Structure

Following REST best practices:

```
/api/job-roles/                   # Collection
/api/job-roles/{id}/              # Individual resource
/api/job-roles/statistics/        # Collection action
/api/job-roles/by_department/     # Collection action

/api/analysis-runs/trigger/       # RPC-style action (POST)
/api/analysis-runs/latest/        # Collection filter
```

### ViewSet Organization

```python
class AnalysisRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    READ-ONLY viewset because analysis runs shouldn't be edited manually
    Only creation via 'trigger' action
    """
    
    @action(detail=False, methods=['post'])
    def trigger(self, request):
        """Custom action for starting analysis (RPC pattern)"""
        pass
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """Get sub-resource"""
        pass
```

**Design Choice**: Read-only for analysis results because:
- Analysis should be immutable once complete
- Only system creates/updates (not users)
- Maintains data integrity
- Audit trail preserved

---

## AI Integration Architecture

### LLM Provider Abstraction

```python
# llm_factory.py
def get_llm(temperature=None):
    """Factory pattern for LLM creation"""
    provider = settings.AI_CONFIG['PROVIDER']
    
    if provider == 'openai':
        return ChatOpenAI(...)
    elif provider == 'anthropic':
        return ChatAnthropic(...)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

**Benefits**:
- ✅ Easy to switch providers
- ✅ Centralized configuration
- ✅ Testable (can mock)
- ✅ Environment-based configuration

### Prompt Engineering Strategy

Each agent has carefully crafted system prompts:

```python
system_prompt = """You are an [EXPERT TYPE] specializing in [DOMAIN].

Analyze [SPECIFIC ASPECT] for:

1. [CRITERION 1]
2. [CRITERION 2]
3. [CRITERION 3]

Common patterns to look for:
- [PATTERN 1]
- [PATTERN 2]

Provide specific, actionable findings with evidence."""
```

**Key Principles**:
1. **Role Definition**: "You are an X expert"
2. **Specific Task**: Clear what to analyze
3. **Structured Criteria**: Numbered list of what to check
4. **Examples**: Common patterns to recognize
5. **Output Format**: What structure to return

### Temperature Settings

```python
org_structure_analyzer: temperature=0.1  # Analytical, factual
responsibility_analyzer: temperature=0.1  # Analytical, factual
workload_analyzer: temperature=0.1       # Analytical, factual
skills_analyzer: temperature=0.1         # Analytical, factual
synthesizer: temperature=0.3             # Slightly creative for synthesis
```

**Rationale**:
- Low temp (0.1) for factual analysis
- Higher temp (0.3) for creative synthesis
- Never too high (no randomness wanted)

---

## Performance Optimizations

### Database Query Optimization

```python
# ❌ Bad: N+1 queries
for employee in Employee.objects.all():
    print(employee.role.role_title)  # Each access hits DB

# ✅ Good: Single query with JOIN
employees = Employee.objects.select_related('role')
for employee in employees:
    print(employee.role.role_title)  # Already loaded
```

**Optimizations Applied**:
1. `select_related` for foreign keys
2. `prefetch_related` for reverse relations
3. Indexing on commonly queried fields
4. Denormalization where appropriate

### AI Processing Optimization

**Batch Data Preparation**:
```python
# Prepare all data once before workflow
job_roles = list(JobRole.objects.all().values())
employees = list(Employee.objects.all().values())

# Pass to workflow (no more DB calls during AI processing)
result = run_analysis(job_roles, employees, departments)
```

**Benefits**:
- ✅ No database calls during AI processing
- ✅ Consistent snapshot of data
- ✅ Faster execution
- ✅ Predictable performance

---

## Error Handling Strategy

### Graceful Degradation

```python
try:
    chain = prompt | llm
    response = chain.invoke(data)
    return {"analysis": response.content}
except Exception as e:
    # Don't fail entire workflow
    return {
        "analysis": f"Error: {str(e)}",
        "error": str(e)
    }
```

**Pattern**: Each agent handles its own errors, workflow continues.

### Analysis Run Status Tracking

```python
analysis_run.status = 'running'
try:
    result = run_analysis(...)
    analysis_run.status = 'completed'
except Exception as e:
    analysis_run.status = 'failed'
    analysis_run.error_message = str(e)
finally:
    analysis_run.save()
```

**Benefit**: User always knows what happened, even on failure.

---

## Security Considerations

### API Security (Current)

- ✅ CORS configuration for frontend
- ✅ Django CSRF protection
- ✅ Environment variable for secrets
- ✅ No hardcoded API keys

### Production Recommendations

For production deployment, add:

1. **Authentication**:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

2. **Rate Limiting**:
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/day',
        'user': '100/day'
    }
}
```

3. **Input Validation**:
- Already using DRF serializers (validates all inputs)
- JSON fields validated against schema

4. **SQL Injection Protection**:
- Using Django ORM (parameterized queries)
- Never raw SQL with user input

---

## Testing Strategy

### Unit Tests (Recommended)

```python
# tests/test_agents.py
def test_org_structure_analyzer():
    state = {
        'job_roles': [...],
        'employees': [...],
        # ...
    }
    result = org_structure_analyzer(state)
    assert 'org_structure_analysis' in result
    assert result['org_structure_analysis'] is not None
```

### Integration Tests

```python
# tests/test_workflow.py
def test_full_workflow():
    result = run_analysis(job_roles, employees, departments)
    assert result['success'] == True
    assert len(result['recommendations']) > 0
```

### API Tests

```python
# tests/test_api.py
def test_trigger_analysis():
    response = client.post('/api/analysis-runs/trigger/')
    assert response.status_code == 201
    assert 'recommendations' in response.json()
```

---

## Scalability Considerations

### Current Capacity

- **Throughput**: 1-2 analyses per minute (LLM rate limit)
- **Data Size**: Handles orgs up to 500 employees comfortably
- **Concurrent Users**: Limited by Django single-threaded dev server

### Scaling Strategies

**Horizontal Scaling**:
```
Load Balancer
    ↓
Django Instance 1  ←→  Redis (Task Queue)
Django Instance 2  ←→  Celery Workers
Django Instance 3  ←→  MySQL (Read Replicas)
```

**Async Processing**:
```python
# Use Celery for long-running tasks
@celery_app.task
def run_analysis_async(job_roles, employees, departments):
    return run_analysis(job_roles, employees, departments)

# API returns immediately
@action(detail=False, methods=['post'])
def trigger(self, request):
    task = run_analysis_async.delay(...)
    return Response({'task_id': task.id}, status=202)
```

---

## Future Architecture Enhancements

### 1. Caching Layer

```python
# Cache expensive queries
from django.core.cache import cache

def get_org_statistics():
    key = 'org_statistics'
    result = cache.get(key)
    
    if not result:
        result = calculate_statistics()
        cache.set(key, result, timeout=3600)  # 1 hour
    
    return result
```

### 2. Real-time Updates (WebSockets)

```python
# Send progress updates during analysis
async def run_analysis_with_updates(websocket):
    await websocket.send_json({"status": "Starting org structure analysis..."})
    org_result = org_structure_analyzer(state)
    
    await websocket.send_json({"status": "Starting responsibility analysis..."})
    # ...
```

### 3. Industry Benchmarking (RAG Integration)

```python
# Add RAG agent for external knowledge
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

def benchmark_analyzer(state):
    """Uses RAG to retrieve industry standards"""
    vectorstore = Chroma(...)
    
    query = f"Standard roles for {state['company_size']} in {state['industry']}"
    docs = vectorstore.similarity_search(query)
    
    # Compare against retrieved benchmarks
    # ...
```

---

## Deployment Architecture

### Development
```
localhost:8000 (Django dev server)
localhost:3306 (MySQL)
```

### Production (Recommended)

```
┌─────────────────────────────────────────┐
│         Cloud Provider (AWS/GCP)         │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  Load Balancer│    │  CloudFront  │  │
│  └──────────────┘    └──────────────┘  │
│         ↓                   ↓           │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  ECS/EKS     │    │   S3 Static  │  │
│  │  (Django)    │    │   Files      │  │
│  └──────────────┘    └──────────────┘  │
│         ↓                               │
│  ┌──────────────┐    ┌──────────────┐  │
│  │  RDS MySQL   │    │  Redis Cache │  │
│  └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────┘
```

---

## Conclusion

This architecture balances:
- ✅ **Correctness**: Multi-agent system produces better analysis
- ✅ **Maintainability**: Clean separation of concerns
- ✅ **Scalability**: Can handle growth with known patterns
- ✅ **Performance**: Optimized queries and data flow
- ✅ **Reliability**: Error handling and status tracking

**Key Insight**: Using the right tool for the job (LangGraph for multi-step reasoning, not RAG for document retrieval) leads to better architecture.

