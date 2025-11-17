# Missing Job Roles AI Agent 🤖

An intelligent system that analyzes organizational structure to identify missing job roles using multi-agent AI workflow powered by LangChain and LangGraph.

**Developed for: One Development, Dubai**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Why This Technology Stack?](#why-this-technology-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)

---

## 🎯 Overview

This system addresses a critical HR challenge: **identifying missing job roles** in an organization that should be filled to improve efficiency, reduce bottlenecks, and support business growth.

### The Problem

Traditional HR analysis relies on manual review and gut feelings. This system uses AI to:
- Analyze organizational structure for inefficiencies
- Identify responsibility gaps
- Detect workload imbalances
- Find skills gaps
- Generate actionable, prioritized recommendations

### Key Features

- ✅ **Multi-Agent AI Analysis**: 5 specialized agents analyze different dimensions
- ✅ **Django REST API**: Production-ready backend integration
- ✅ **MySQL Integration**: Connects to existing HR databases
- ✅ **Realistic Sample Data**: Built-in data generator for testing
- ✅ **Explainable AI**: Every recommendation includes detailed justification
- ✅ **Priority-Based**: Recommendations ranked by business impact

---

## 🚀 Why This Technology Stack?

### Initial Approach vs. Refined Solution

**Initial Idea**: Use RAG (Retrieval Augmented Generation) with prompt engineering.

**Problem**: RAG is designed for **document retrieval**, not structured data analysis (even though we might use unstructered data for example job descriptions documents , pdfs). Our problem requires:
- Multi-dimensional reasoning
- Structured data processing (tables, not documents for now)
- Synthesis of multiple analyses
- Comparative logic

**Better Solution**: **LangGraph Multi-Agent Workflow**

### Technology Justification

#### 1. **LangGraph** (Not Basic LangChain)

**Why LangGraph?**
- ✅ **Stateful Workflows**: Maintains context across 5 analysis stages
- ✅ **Agent Orchestration**: Coordinates multiple specialized agents
- ✅ **Sequential Processing**: Each agent builds on previous findings
- ✅ **Error Handling**: Robust execution with failure recovery
- ✅ **Scalable**: Easy to add more agents (e.g., budget analysis, industry benchmarking)

**Why Not Basic LangChain?**
- Basic chains are too simple for multi-step reasoning
- Need state management between agents
- Require conditional logic based on intermediate results

#### 2. **Django REST Framework**

**Why Django?**
- ✅ Already used by the company (easy integration)
- ✅ Mature ORM for database operations
- ✅ Built-in admin interface for data management
- ✅ Production-ready security features
- ✅ Excellent REST API support

#### 3. **MySQL**

**Why MySQL?**
- ✅ Company's existing database(assumption)
- ✅ Reliable for HR data storage
- ✅ Django ORM handles all SQL complexity

#### 4. **Python 3.10+**

**Why Python?**
- ✅ Best ecosystem for AI/ML
- ✅ LangChain/LangGraph native support
- ✅ Django compatibility
- ✅ Easy to maintain and extend

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Django REST API                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Job Roles   │  │  Employees   │  │  Analysis    │     │
│  │  Endpoint    │  │  Endpoint    │  │  Endpoint    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. Org Structure Analyzer Agent                      │  │
│  │    - Span of control issues                           │  │
│  │    - Missing management layers                        │  │
│  │    - Reporting bottlenecks                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Responsibility Coverage Analyzer                   │  │
│  │    - Critical function gaps                           │  │
│  │    - Overlap detection                                │  │
│  │    - Department-specific needs                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. Workload & Capacity Analyzer                       │  │
│  │    - Overloaded employees                             │  │
│  │    - Understaffed roles                               │  │
│  │    - Single points of failure                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 4. Skills Gap Analyzer                                │  │
│  │    - Missing critical skills                          │  │
│  │    - Emerging technology needs                        │  │
│  │    - Skills concentration risk                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 5. Synthesizer Agent                                  │  │
│  │    - Combines all analyses                            │  │
│  │    - Prioritizes recommendations                      │  │
│  │    - Generates actionable output                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  MySQL Database                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  job_roles   │  │  employees   │  │analysis_runs │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐                                           │
│  │missing_roles │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### Multi-Agent Workflow

Each agent is specialized and processes data sequentially:

1. **Org Structure Agent**: Analyzes hierarchy, reporting structure, management layers
2. **Responsibility Agent**: Checks if critical business functions are covered
3. **Workload Agent**: Identifies capacity constraints and overload
4. **Skills Agent**: Finds missing competencies and skill gaps
5. **Synthesizer**: Combines findings into prioritized recommendations

**Why Sequential, Not Parallel?**
- Later agents benefit from earlier insights
- Synthesizer needs all analyses complete
- More coherent final recommendations

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- MySQL 5.7+ or 8.0+
- OpenAI API key (or Anthropic Claude API key)

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd "C:\Users\Walid\OneDrive\Desktop\Missing Job Roles Agent"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

**Required Configuration**:

```env
# Django
SECRET_KEY=your-secret-key-here-generate-one
DEBUG=True

# Database (use your MySQL credentials)
DB_NAME=hr_database
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=localhost
DB_PORT=3306

# AI Provider (use one)
OPENAI_API_KEY=sk-your-openai-api-key
# OR
# ANTHROPIC_API_KEY=sk-ant-your-claude-api-key

LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

### Step 3: Setup Database

```bash
# Create MySQL database (in MySQL client)
CREATE DATABASE hr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run Django migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Step 4: Generate Sample Data

```bash
# Generate medium-sized company data (50-150 employees)
python manage.py generate_sample_data --size medium

# Options:
# --size small    : 20-50 employees
# --size medium   : 50-150 employees (default)
# --size large    : 150+ employees

# Optional: Export data
python manage.py generate_sample_data --size medium --export-json --export-sql
```

### Step 5: Run the Server

```bash
python manage.py runserver
```

Server will start at: `http://127.0.0.1:8000/`

---

## 🎮 Usage

### Option 1: Django Admin Interface

1. Go to `http://127.0.0.1:8000/admin`
2. Login with superuser credentials
3. Browse Job Roles and Employees
4. View Analysis Runs and Recommendations

### Option 2: REST API

#### Trigger Analysis

```bash
# Analyze all departments
curl -X POST http://127.0.0.1:8000/api/analysis-runs/trigger/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Analyze specific departments
curl -X POST http://127.0.0.1:8000/api/analysis-runs/trigger/ \
  -H "Content-Type: application/json" \
  -d '{"departments": ["Engineering", "Product"]}'
```

#### View Results

```bash
# Get latest analysis
curl http://127.0.0.1:8000/api/analysis-runs/latest/

# Get all analysis runs
curl http://127.0.0.1:8000/api/analysis-runs/

# Get specific analysis by ID
curl http://127.0.0.1:8000/api/analysis-runs/1/

# Get just recommendations
curl http://127.0.0.1:8000/api/missing-roles/by_priority/
```

### Option 3: Python Script

```python
import requests

# Trigger analysis
response = requests.post('http://127.0.0.1:8000/api/analysis-runs/trigger/')
analysis = response.json()

print(f"Analysis Run ID: {analysis['id']}")
print(f"Status: {analysis['status']}")
print(f"Found {len(analysis['recommendations'])} missing roles")

# Display recommendations
for rec in analysis['recommendations']:
    print(f"\n{rec['recommended_role_title']} ({rec['priority']})")
    print(f"  Department: {rec['department']}")
    print(f"  Why: {rec['justification']}")
```

---

## 📚 API Documentation

### Base URL

```
http://127.0.0.1:8000/api/
```

### Endpoints

#### 1. Job Roles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/job-roles/` | List all job roles |
| GET | `/api/job-roles/{id}/` | Get specific role |
| GET | `/api/job-roles/by_department/` | Roles grouped by department |
| GET | `/api/job-roles/statistics/` | Overall statistics |

#### 2. Employees

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/` | List all employees |
| GET | `/api/employees/{id}/` | Get specific employee |
| GET | `/api/employees/workload_stats/` | Workload statistics |

#### 3. Analysis Runs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analysis-runs/` | List all analysis runs |
| GET | `/api/analysis-runs/{id}/` | Get specific run details |
| GET | `/api/analysis-runs/latest/` | Get most recent analysis |
| POST | `/api/analysis-runs/trigger/` | **Start new analysis** |
| GET | `/api/analysis-runs/{id}/recommendations/` | Get recommendations only |

**Trigger Analysis Body**:
```json
{
  "departments": ["Engineering", "Product"],  // Optional
  "include_benchmark": false  // Optional (future feature)
}
```

#### 4. Missing Roles

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/missing-roles/` | List all recommendations |
| GET | `/api/missing-roles/{id}/` | Get specific recommendation |
| GET | `/api/missing-roles/by_priority/` | Grouped by priority |
| GET | `/api/missing-roles/by_department/` | Grouped by department |

### Response Examples

#### Analysis Run Result

```json
{
  "id": 1,
  "run_date": "2025-11-16T14:30:00Z",
  "status": "completed",
  "total_roles_analyzed": 28,
  "total_employees_analyzed": 95,
  "departments_analyzed": ["Engineering", "Product", "Marketing"],
  "execution_time_seconds": 45.2,
  "missing_roles": [
    {
      "id": 1,
      "recommended_role_title": "QA Engineer",
      "department": "Engineering",
      "level": "mid",
      "gap_type": "responsibility",
      "justification": "Currently no dedicated QA role. Developers doing own testing leads to quality issues and slower delivery.",
      "expected_impact": "Improved product quality, faster release cycles, 40% reduction in production bugs",
      "priority": "critical",
      "recommended_headcount": 2,
      "estimated_timeline": "Immediate",
      "required_skills": ["Test Automation", "Selenium", "API Testing", "CI/CD"],
      "responsibilities": ["Create test plans", "Automate testing", "Bug tracking", "Quality metrics"]
    }
  ]
}
```

---

## 📁 Project Structure

```
Missing Job Roles Agent/
├── missing_roles_project/          # Django project settings
│   ├── settings.py                 # Configuration
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI application
│
├── roles_analyzer/                 # Main Django app
│   ├── models.py                   # Database models
│   ├── views.py                    # REST API views
│   ├── serializers.py              # DRF serializers
│   ├── urls.py                     # API routing
│   ├── admin.py                    # Admin interface config
│   ├── data_generator.py           # Sample data generator
│   │
│   ├── ai_agents/                  # LangGraph AI system
│   │   ├── workflow.py             # LangGraph orchestration
│   │   ├── agents.py               # Individual agents
│   │   ├── state.py                # Shared state definition
│   │   └── llm_factory.py          # LLM provider factory
│   │
│   └── management/commands/        # Django commands
│       └── generate_sample_data.py # Data generation command
│
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── manage.py                       # Django management
└── README.md                       # This file
```

---

## ⚙️ How It Works

### The Analysis Process

1. **Data Collection**
   - Load job roles from MySQL database
   - Load employee data with workload status
   - Extract skills, responsibilities, reporting structure

2. **Multi-Agent Analysis** (Sequential)

   **Agent 1: Org Structure Analyzer**
   - Builds organizational hierarchy tree
   - Identifies span of control issues (managers with too many reports)
   - Finds missing management layers
   - Detects flat structures in large departments

   **Agent 2: Responsibility Coverage Analyzer**
   - Maps all responsibilities to roles
   - Identifies critical business functions (HR, Finance, IT, etc.)
   - Checks coverage of standard functions
   - Finds responsibility gaps and overlaps

   **Agent 3: Workload & Capacity Analyzer**
   - Calculates workload distribution
   - Identifies overloaded employees (>20% indicates problems)
   - Finds single points of failure
   - Determines if gaps need new roles vs. more headcount

   **Agent 4: Skills Gap Analyzer**
   - Compares required vs. available skills
   - Identifies missing critical competencies
   - Detects emerging skill needs (AI, Cloud, Data, etc.)
   - Recommends roles to fill skill gaps

   **Agent 5: Synthesizer**
   - Combines all analyses
   - Removes duplicates and overlaps
   - Prioritizes by business impact
   - Generates structured recommendations with justifications

3. **Result Storage**
   - Save analysis run to database
   - Create MissingRole records
   - Store detailed findings for each agent
   - Track execution metrics

4. **API Response**
   - Return prioritized recommendations
   - Include justifications and evidence
   - Provide actionable timeline
   - List required skills and responsibilities

### Why This Approach Works

✅ **Explainable**: Every recommendation has clear reasoning  
✅ **Comprehensive**: Analyzes multiple dimensions (structure, workload, skills)  
✅ **Data-Driven**: Based on actual org data, not assumptions  
✅ **Actionable**: Specific roles with priority and timeline  
✅ **Scalable**: Easy to add more analysis agents  

---

## 🎯 Expected Results

When running on the generated sample data, the AI should identify:

### Engineering Department
- **QA Engineer** (Critical): No dedicated testing role
- **Data Engineer** (High): No data pipeline management
- **Security Engineer** (High): Ad-hoc security approach

### Product Department
- **Product Analyst** (High): No data-driven product decisions
- **UX Researcher** (Medium): Limited user research

### Marketing Department
- **SEO Specialist** (Critical): Declining organic traffic
- **Social Media Manager** (High): Inconsistent social presence
- **Growth Hacker** (Medium): No systematic growth experiments

### HR Department
- **L&D Specialist** (High): No structured training programs
- **HR Business Partner** (Medium): Reactive HR, not strategic

### Sales Department
- **Sales Operations** (High): Manual processes, no automation
- **Business Development** (Medium): No partnership focus

---

## 🔮 Future Enhancements

### Planned Features

1. **Industry Benchmarking** (RAG Integration)
   - Compare against industry standards
   - Use RAG to retrieve relevant benchmark data
   - Incorporate best practices from similar companies

2. **Budget Constraints**
   - Factor in hiring budget
   - Prioritize based on cost-benefit
   - Phased hiring recommendations

3. **Predictive Analysis**
   - Forecast future needs based on growth
   - Identify roles needed in 6-12 months
   - Proactive workforce planning

4. **Real-time Integration**
   - Connect to HRIS systems
   - Automated periodic analysis
   - Change detection and alerts

5. **Custom Rules Engine**
   - Allow HR to define custom criteria
   - Company-specific gap indicators
   - Configurable priority weights

---

## 🤔 Common Questions

### Q: Why not use RAG?

**A**: RAG is for document retrieval. Our problem is structured data analysis requiring multi-step reasoning. RAG could be useful later for industry benchmarking with external reports, but not for core analysis.

### Q: Can I use Claude instead of GPT-4?

**A**: Yes! Just set in `.env`:
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
LLM_MODEL=claude-3-5-sonnet-20241022
```

### Q: How accurate are the recommendations?

**A**: Accuracy depends on data quality. The AI provides reasoning, but HR should validate recommendations. This is a decision-support tool, not a replacement for human judgment.

### Q: How long does analysis take?

**A**: Typically 30-60 seconds for 50-150 employee org. Time depends on:
- Number of roles/employees
- LLM response time
- Network latency

### Q: Can I analyze just one department?

**A**: Yes! Use the `departments` parameter:
```json
{"departments": ["Engineering"]}
```

### Q: How much does it cost to run?

**A**: Depends on LLM provider and usage:
- GPT-4: ~$0.10-0.30 per analysis run
- GPT-3.5-Turbo: ~$0.01-0.05 per run
- Claude: ~$0.08-0.24 per run

---

## 📞 Support

For questions or issues:
- Review this README
- Check API documentation
- Inspect Django admin interface
- Review analysis run error messages

---

## 📄 License

This project was developed as a technical assessment for One Development, Dubai.

---

## ✅ Summary

This system demonstrates:
- ✅ Deep understanding of when to use specific AI tools (LangGraph vs. RAG)
- ✅ Production-ready Django REST API architecture
- ✅ Multi-agent AI system design
- ✅ Practical problem-solving for HR analytics
- ✅ Clear documentation and explainability
- ✅ Integration with existing tech stack (Django, MySQL)

**Key Insight**: Not every AI problem needs RAG. Structured data analysis requires reasoning workflows (LangGraph), not document retrieval (RAG).

