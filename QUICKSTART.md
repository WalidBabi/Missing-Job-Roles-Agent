# Quick Start Guide

Get the Missing Job Roles AI Agent running in 10 minutes!

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] MySQL 5.7+ or 8.0+ installed and running
- [ ] OpenAI API key (or Anthropic Claude key)
- [ ] Git (optional, for version control)

---

## Step-by-Step Setup

### Step 1: Open Terminal in Project Directory

```bash
cd "C:\Users\Walid\OneDrive\Desktop\Missing Job Roles Agent"
```

### Step 2: Run Setup Script (Windows)

```bash
setup.bat
```

Or manually:

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example configuration
copy .env.example .env

# Edit with your settings
notepad .env
```

**Minimum required settings:**

```env
SECRET_KEY=your-random-secret-key-here
DEBUG=True

# Database
DB_NAME=hr_database
DB_USER=root
DB_PASSWORD=YourMySQLPassword
DB_HOST=localhost
DB_PORT=3306

# AI Provider
OPENAI_API_KEY=sk-your-openai-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
```

### Step 4: Create MySQL Database

Open MySQL client and run:

```sql
CREATE DATABASE hr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or use command line:

```bash
mysql -u root -p -e "CREATE DATABASE hr_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Step 5: Run Django Migrations

```bash
python manage.py migrate
```

You should see:

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, roles_analyzer
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying roles_analyzer.0001_initial... OK
```

### Step 6: Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

Follow prompts to create username, email, and password.

### Step 7: Generate Sample Data

```bash
python manage.py generate_sample_data --size medium
```

This creates:
- ~28 job roles across 8 departments
- ~95 employees with realistic data
- Workload indicators (some overloaded to trigger recommendations)

### Step 8: Start the Server

```bash
python manage.py runserver
```

Server starts at: **http://127.0.0.1:8000/**

---

## Test the Installation

### Option 1: Browser

Open your browser and go to:

- **API Root**: http://127.0.0.1:8000/api/
- **Admin**: http://127.0.0.1:8000/admin/
- **Job Roles**: http://127.0.0.1:8000/api/job-roles/
- **Statistics**: http://127.0.0.1:8000/api/job-roles/statistics/

### Option 2: Command Line

Open a new terminal (keep server running) and test:

```bash
# Get organization statistics
curl http://127.0.0.1:8000/api/job-roles/statistics/

# Trigger analysis (this will take 30-60 seconds)
curl -X POST http://127.0.0.1:8000/api/analysis-runs/trigger/ -H "Content-Type: application/json" -d "{}"

# View latest results
curl http://127.0.0.1:8000/api/analysis-runs/latest/
```

### Option 3: Python Script

Create `test_quick.py`:

```python
import requests

BASE = "http://127.0.0.1:8000/api"

# Check connection
print("Testing connection...")
response = requests.get(f"{BASE}/job-roles/statistics/")
print(f"✓ Server is running: {response.json()}")

# Trigger analysis
print("\nStarting analysis (this takes ~30-60 seconds)...")
response = requests.post(f"{BASE}/analysis-runs/trigger/")
result = response.json()

print(f"\n✓ Analysis complete!")
print(f"Found {len(result['missing_roles'])} missing roles:")

for role in result['missing_roles'][:5]:  # Show first 5
    print(f"\n  • {role['recommended_role_title']} ({role['priority']})")
    print(f"    Department: {role['department']}")
    print(f"    Why: {role['justification'][:100]}...")
```

Run it:

```bash
python test_quick.py
```

---

## Expected Output

When analysis completes, you should see recommendations like:

```json
{
  "id": 1,
  "status": "completed",
  "execution_time_seconds": 45.2,
  "missing_roles": [
    {
      "recommended_role_title": "QA Engineer",
      "department": "Engineering",
      "priority": "critical",
      "justification": "No dedicated QA role exists. Developers doing own testing leads to quality issues...",
      "expected_impact": "Improved product quality, 40% reduction in bugs, faster releases",
      "recommended_headcount": 2,
      "estimated_timeline": "Immediate"
    },
    {
      "recommended_role_title": "Data Engineer",
      "department": "Engineering",
      "priority": "high",
      "justification": "No data pipeline management. Ad-hoc data processes are inefficient...",
      "expected_impact": "Automated data pipelines, better analytics capabilities",
      "recommended_headcount": 1,
      "estimated_timeline": "3 months"
    }
    // ... more recommendations
  ]
}
```

---

## Troubleshooting

### Problem: "Connection refused"

**Solution**: Make sure MySQL is running:

```bash
# Windows
net start MySQL80

# Check if running
mysql -u root -p -e "SELECT 1;"
```

### Problem: "OPENAI_API_KEY not configured"

**Solution**: Add your API key to `.env` file:

```env
OPENAI_API_KEY=sk-your-actual-key-here
```

### Problem: "No module named 'langchain'"

**Solution**: Install dependencies:

```bash
pip install -r requirements.txt
```

### Problem: "Table doesn't exist"

**Solution**: Run migrations:

```bash
python manage.py migrate
```

### Problem: "No data found"

**Solution**: Generate sample data:

```bash
python manage.py generate_sample_data
```

### Problem: Analysis takes forever

**Solution**: This is normal! LLM processing takes 30-60 seconds. Watch the console output:

```
🔍 Running Organizational Structure Analysis...
🔍 Running Responsibility Coverage Analysis...
🔍 Running Workload & Capacity Analysis...
🔍 Running Skills Gap Analysis...
🔍 Synthesizing Final Recommendations...
✅ Analysis Complete!
```

---

## What's Next?

### Explore the System

1. **Django Admin Interface**:
   - Go to http://127.0.0.1:8000/admin/
   - Login with superuser credentials
   - Browse job roles, employees, and analysis results

2. **API Exploration**:
   - See `API_EXAMPLES.md` for complete API documentation
   - Try different endpoints
   - Filter by department, priority, etc.

3. **Run Multiple Analyses**:
   - Analyze specific departments
   - Compare results over time
   - Export recommendations

### Customize the System

1. **Add Your Own Data**:
   - Import from your Excel file
   - Connect to your MySQL database
   - See README.md for data format

2. **Modify Agents**:
   - Edit `roles_analyzer/ai_agents/agents.py`
   - Customize prompts for your industry
   - Add new analysis dimensions

3. **Integrate with Frontend**:
   - Use API endpoints in React/Vue app
   - See `API_EXAMPLES.md` for JavaScript examples
   - Build custom dashboards

---

## Quick Reference

### Common Commands

```bash
# Start server
python manage.py runserver

# Generate data
python manage.py generate_sample_data --size medium

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Django shell (for debugging)
python manage.py shell
```

### Key URLs

- **API Root**: http://127.0.0.1:8000/api/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Trigger Analysis**: POST http://127.0.0.1:8000/api/analysis-runs/trigger/
- **Latest Results**: http://127.0.0.1:8000/api/analysis-runs/latest/

### File Locations

- **Settings**: `missing_roles_project/settings.py`
- **Models**: `roles_analyzer/models.py`
- **AI Agents**: `roles_analyzer/ai_agents/`
- **API Views**: `roles_analyzer/views.py`
- **Environment**: `.env`

---

## Success!

You now have a working AI-powered HR analytics system!

🎯 **Your system can now**:
- Analyze organizational structure
- Identify missing job roles
- Provide actionable recommendations
- Explain its reasoning

📚 **Read more**:
- `README.md` - Complete documentation
- `API_EXAMPLES.md` - API usage examples
- `ARCHITECTURE.md` - Technical deep dive

---

## Get Help

If you're stuck:

1. Check the troubleshooting section above
2. Review the detailed README.md
3. Look at API_EXAMPLES.md for working code
4. Check Django logs for errors

**Remember**: This is a sophisticated AI system. The first run will download models and may take longer. Subsequent runs will be faster!

---

**Congratulations! 🎉 You're ready to identify missing job roles with AI!**

