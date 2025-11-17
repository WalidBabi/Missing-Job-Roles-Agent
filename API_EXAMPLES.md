# API Usage Examples

Complete examples for interacting with the Missing Job Roles AI Agent API.

## Table of Contents

- [Setup](#setup)
- [Basic Examples](#basic-examples)
- [Advanced Examples](#advanced-examples)
- [Python Client Examples](#python-client-examples)
- [JavaScript Examples](#javascript-examples)

---

## Setup

Base URL: `http://127.0.0.1:8000/api/`

All examples assume the server is running locally.

---

## Basic Examples

### 1. Get Organization Statistics

```bash
curl http://127.0.0.1:8000/api/job-roles/statistics/
```

**Response:**
```json
{
  "total_roles": 28,
  "total_headcount": 95,
  "total_departments": 8,
  "departments": [
    "Engineering",
    "Product",
    "Marketing",
    "Sales",
    "Human Resources",
    "Finance",
    "Customer Support",
    "Operations"
  ]
}
```

### 2. View All Job Roles

```bash
curl http://127.0.0.1:8000/api/job-roles/
```

### 3. Get Workload Statistics

```bash
curl http://127.0.0.1:8000/api/employees/workload_stats/
```

**Response:**
```json
{
  "total_employees": 95,
  "by_status": {
    "overloaded": 24,
    "normal": 57,
    "underutilized": 14
  },
  "by_department": {
    "Engineering": {
      "total": 35,
      "overloaded": 9
    },
    "Product": {
      "total": 12,
      "overloaded": 3
    }
  }
}
```

---

## Advanced Examples

### 4. Trigger Full Organization Analysis

```bash
curl -X POST http://127.0.0.1:8000/api/analysis-runs/trigger/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "id": 1,
  "run_date": "2025-11-16T14:30:00Z",
  "status": "completed",
  "total_roles_analyzed": 28,
  "total_employees_analyzed": 95,
  "departments_analyzed": ["Engineering", "Product", "Marketing", "Sales", "Human Resources", "Finance", "Customer Support", "Operations"],
  "execution_time_seconds": 45.2,
  "org_structure_gaps": "Analysis shows...",
  "responsibility_gaps": "Critical gaps found...",
  "workload_gaps": "High overload in...",
  "skills_gaps": "Missing skills include...",
  "recommendations": [
    {
      "role_title": "QA Engineer",
      "department": "Engineering",
      "level": "mid",
      "gap_type": "responsibility",
      "justification": "Currently no dedicated QA role...",
      "expected_impact": "Improved product quality...",
      "priority": "critical",
      "recommended_headcount": 2,
      "estimated_timeline": "Immediate",
      "required_skills": ["Test Automation", "Selenium", "API Testing"],
      "responsibilities": ["Create test plans", "Automate testing"]
    }
  ],
  "missing_roles": [...]
}
```

### 5. Analyze Specific Departments Only

```bash
curl -X POST http://127.0.0.1:8000/api/analysis-runs/trigger/ \
  -H "Content-Type: application/json" \
  -d '{
    "departments": ["Engineering", "Product"]
  }'
```

### 6. Get Latest Analysis

```bash
curl http://127.0.0.1:8000/api/analysis-runs/latest/
```

### 7. Get Missing Roles by Priority

```bash
curl http://127.0.0.1:8000/api/missing-roles/by_priority/
```

**Response:**
```json
{
  "critical": [
    {
      "id": 1,
      "recommended_role_title": "QA Engineer",
      "department": "Engineering",
      "level": "mid",
      "gap_type": "responsibility",
      "justification": "...",
      "expected_impact": "...",
      "priority": "critical",
      "recommended_headcount": 2,
      "estimated_timeline": "Immediate",
      "required_skills": [...],
      "responsibilities": [...]
    }
  ],
  "high": [...],
  "medium": [...],
  "low": [...]
}
```

### 8. Get Missing Roles by Department

```bash
curl http://127.0.0.1:8000/api/missing-roles/by_department/
```

### 9. View Job Roles by Department

```bash
curl http://127.0.0.1:8000/api/job-roles/by_department/
```

---

## Python Client Examples

### Example 1: Basic Analysis Workflow

```python
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def run_analysis():
    """Trigger analysis and wait for completion"""
    
    # Trigger analysis
    print("Starting analysis...")
    response = requests.post(f"{BASE_URL}/analysis-runs/trigger/")
    
    if response.status_code != 201:
        print(f"Error: {response.text}")
        return None
    
    analysis = response.json()
    analysis_id = analysis['id']
    print(f"Analysis started (ID: {analysis_id})")
    print(f"Status: {analysis['status']}")
    print(f"Execution time: {analysis['execution_time_seconds']}s")
    
    return analysis

def display_recommendations(analysis):
    """Display recommendations in readable format"""
    
    recommendations = analysis.get('missing_roles', [])
    
    if not recommendations:
        print("No missing roles identified!")
        return
    
    print(f"\n{'='*60}")
    print(f"FOUND {len(recommendations)} MISSING ROLES")
    print(f"{'='*60}\n")
    
    # Group by priority
    by_priority = {}
    for rec in recommendations:
        priority = rec['priority']
        if priority not in by_priority:
            by_priority[priority] = []
        by_priority[priority].append(rec)
    
    # Display
    for priority in ['critical', 'high', 'medium', 'low']:
        if priority not in by_priority:
            continue
        
        print(f"\n🔴 {priority.upper()} PRIORITY")
        print("-" * 60)
        
        for rec in by_priority[priority]:
            print(f"\n{rec['recommended_role_title']}")
            print(f"  Department: {rec['department']}")
            print(f"  Level: {rec['level']}")
            print(f"  Headcount: {rec['recommended_headcount']}")
            print(f"  Timeline: {rec['estimated_timeline']}")
            print(f"  Why: {rec['justification'][:100]}...")
            print(f"  Impact: {rec['expected_impact'][:100]}...")

# Run
if __name__ == "__main__":
    analysis = run_analysis()
    if analysis:
        display_recommendations(analysis)
```

### Example 2: Analyze Specific Department

```python
import requests

def analyze_engineering_only():
    """Analyze only Engineering department"""
    
    response = requests.post(
        "http://127.0.0.1:8000/api/analysis-runs/trigger/",
        json={"departments": ["Engineering"]}
    )
    
    analysis = response.json()
    
    print(f"Analyzed {analysis['total_roles_analyzed']} roles")
    print(f"Found {len(analysis['missing_roles'])} missing roles")
    
    for role in analysis['missing_roles']:
        print(f"\n- {role['recommended_role_title']} ({role['priority']})")

analyze_engineering_only()
```

### Example 3: Compare Multiple Analysis Runs

```python
import requests

def compare_analyses():
    """Compare results from multiple analysis runs"""
    
    response = requests.get("http://127.0.0.1:8000/api/analysis-runs/")
    runs = response.json()['results']
    
    print(f"Total Analysis Runs: {len(runs)}")
    
    for run in runs[:5]:  # Last 5 runs
        print(f"\nRun {run['id']} - {run['run_date']}")
        print(f"  Status: {run['status']}")
        print(f"  Execution: {run['execution_time_seconds']}s")
        print(f"  Missing roles: {run['missing_roles_count']}")

compare_analyses()
```

### Example 4: Export Recommendations to CSV

```python
import requests
import csv

def export_to_csv(filename="recommendations.csv"):
    """Export all missing role recommendations to CSV"""
    
    response = requests.get("http://127.0.0.1:8000/api/missing-roles/")
    recommendations = response.json()['results']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Role Title', 'Department', 'Priority', 'Headcount',
            'Timeline', 'Gap Type', 'Justification', 'Impact'
        ])
        
        # Data
        for rec in recommendations:
            writer.writerow([
                rec['recommended_role_title'],
                rec['department'],
                rec['priority'],
                rec['recommended_headcount'],
                rec['estimated_timeline'],
                rec['gap_type'],
                rec['justification'],
                rec['expected_impact']
            ])
    
    print(f"Exported {len(recommendations)} recommendations to {filename}")

export_to_csv()
```

---

## JavaScript Examples

### Example 1: Fetch Analysis Results

```javascript
async function getLatestAnalysis() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/analysis-runs/latest/');
    const data = await response.json();
    
    console.log(`Analysis Run ${data.id}`);
    console.log(`Status: ${data.status}`);
    console.log(`Found ${data.missing_roles.length} missing roles`);
    
    // Display recommendations
    data.missing_roles.forEach(role => {
      console.log(`\n${role.recommended_role_title} (${role.priority})`);
      console.log(`  Department: ${role.department}`);
      console.log(`  Why: ${role.justification.substring(0, 100)}...`);
    });
    
  } catch (error) {
    console.error('Error:', error);
  }
}

getLatestAnalysis();
```

### Example 2: Trigger Analysis with Progress

```javascript
async function triggerAnalysis(departments = []) {
  try {
    console.log('Triggering analysis...');
    
    const response = await fetch('http://127.0.0.1:8000/api/analysis-runs/trigger/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ departments })
    });
    
    const data = await response.json();
    
    if (response.status === 201) {
      console.log('✅ Analysis completed!');
      console.log(`Execution time: ${data.execution_time_seconds}s`);
      console.log(`Recommendations: ${data.missing_roles.length}`);
      return data;
    } else {
      console.error('❌ Analysis failed:', data.error);
      return null;
    }
    
  } catch (error) {
    console.error('Error:', error);
    return null;
  }
}

// Run for all departments
triggerAnalysis();

// Or specific departments
triggerAnalysis(['Engineering', 'Product']);
```

### Example 3: Display Recommendations in UI

```javascript
async function displayRecommendations() {
  const response = await fetch('http://127.0.0.1:8000/api/missing-roles/by_priority/');
  const data = await response.json();
  
  const container = document.getElementById('recommendations');
  
  ['critical', 'high', 'medium', 'low'].forEach(priority => {
    if (!data[priority] || data[priority].length === 0) return;
    
    const section = document.createElement('div');
    section.className = `priority-${priority}`;
    section.innerHTML = `<h2>${priority.toUpperCase()} Priority</h2>`;
    
    data[priority].forEach(role => {
      const card = document.createElement('div');
      card.className = 'role-card';
      card.innerHTML = `
        <h3>${role.recommended_role_title}</h3>
        <p><strong>Department:</strong> ${role.department}</p>
        <p><strong>Headcount:</strong> ${role.recommended_headcount}</p>
        <p><strong>Timeline:</strong> ${role.estimated_timeline}</p>
        <p><strong>Why needed:</strong> ${role.justification}</p>
        <p><strong>Expected impact:</strong> ${role.expected_impact}</p>
        <p><strong>Skills:</strong> ${role.required_skills.join(', ')}</p>
      `;
      section.appendChild(card);
    });
    
    container.appendChild(section);
  });
}

displayRecommendations();
```

---

## Testing the API

### Quick Test Script

Save as `test_api.py`:

```python
#!/usr/bin/env python3
import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def test_connection():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/job-roles/statistics/")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print("❌ Server responded with error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False

def test_data_exists():
    """Check if sample data is loaded"""
    response = requests.get(f"{BASE_URL}/job-roles/")
    data = response.json()
    
    if data['count'] > 0:
        print(f"✅ Found {data['count']} job roles")
        return True
    else:
        print("❌ No data found. Run: python manage.py generate_sample_data")
        return False

def test_analysis():
    """Test analysis workflow"""
    print("\nTesting analysis workflow...")
    
    response = requests.post(f"{BASE_URL}/analysis-runs/trigger/")
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Analysis completed in {data['execution_time_seconds']}s")
        print(f"✅ Found {len(data['missing_roles'])} missing roles")
        return True
    else:
        print(f"❌ Analysis failed: {response.text}")
        return False

if __name__ == "__main__":
    print("Testing Missing Job Roles AI Agent API\n")
    
    if not test_connection():
        sys.exit(1)
    
    if not test_data_exists():
        sys.exit(1)
    
    if not test_analysis():
        sys.exit(1)
    
    print("\n✅ All tests passed!")
```

Run with:
```bash
python test_api.py
```

---

## Error Handling

### Common Errors

**1. Connection Refused**
```json
{
  "error": "Connection refused"
}
```
**Solution**: Make sure Django server is running (`python manage.py runserver`)

**2. No Data**
```json
{
  "count": 0,
  "results": []
}
```
**Solution**: Generate sample data (`python manage.py generate_sample_data`)

**3. API Key Missing**
```json
{
  "error": "OPENAI_API_KEY not configured"
}
```
**Solution**: Add API key to `.env` file

**4. Analysis Failed**
```json
{
  "status": "failed",
  "error_message": "Error details..."
}
```
**Solution**: Check Django logs for detailed error messages

---

## Rate Limiting and Performance

- Each analysis takes 30-60 seconds (LLM processing time)
- Multiple sequential analyses: wait for completion before triggering next
- Cost per analysis: ~$0.10-0.30 with GPT-4
- Database queries are optimized with `select_related` and `prefetch_related`

---

## Next Steps

- Integrate with frontend (React/Vue)
- Add real-time updates with WebSockets
- Implement caching for frequently accessed data
- Add authentication and authorization
- Deploy to production environment

