# Frontend Setup Guide

## 🎨 React Frontend for Missing Job Roles AI

A modern, professional React dashboard for HR teams to interact with the AI agent.

---

## ✅ What Was Created

### Components
- **Dashboard.jsx** - Main dashboard with statistics and metrics
- **Analysis.jsx** - Trigger AI analysis and view recommendations
- **JobRoles.jsx** - Browse all job roles by department
- **Navbar.jsx** - Navigation bar with routing

### Features
- 📊 Real-time organizational statistics
- 🚀 One-click AI analysis trigger
- 📋 Detailed recommendations with priorities
- 🎯 Department and priority filtering
- 💅 Beautiful, responsive UI with Tailwind CSS
- 🔄 Real-time updates and loading states

---

## 🚀 Quick Start

### Step 1: Create Environment File

```bash
cd frontend
```

Create a `.env` file:
```env
VITE_API_URL=http://127.0.0.1:8000/api
```

### Step 2: Make Sure Backend is Running

In the main project directory:
```bash
# Activate venv
venv\Scripts\activate

# Start Django server
python manage.py runserver
```

### Step 3: Start Frontend

In a new terminal:
```bash
cd frontend
npm run dev
```

The frontend will open at: **http://localhost:5173**

---

## 📸 What You'll See

### Dashboard
- Organization statistics (roles, employees, departments)
- Workload distribution chart
- Overloaded employee percentage
- Quick action buttons

### AI Analysis Page
- Department selector (analyze all or specific departments)
- "Run AI Analysis" button
- Real-time analysis progress (30-60 seconds)
- Detailed recommendations with:
  - Priority badges (Critical/High/Medium/Low)
  - Department and headcount info
  - Justification and expected impact
  - Required skills list
  - Timeline for hiring

### Job Roles Page
- All roles grouped by department
- Department filter dropdown
- Search by role title
- Each role shows: level, headcount, team size, skills

---

## 🎯 Usage Flow

1. **Open Dashboard**
   - See org overview
   - Check overloaded employees percentage

2. **Run Analysis**
   - Click "AI Analysis" in navbar
   - Optionally select departments
   - Click "Run AI Analysis"
   - Wait for results (30-60 seconds)

3. **View Recommendations**
   - See prioritized missing roles
   - Read justifications
   - View expected impact
   - Check required skills

4. **Browse Roles**
   - Navigate to "Job Roles"
   - Filter by department
   - Search specific roles

---

## 🛠️ Technical Details

### Tech Stack
- React 18 with Vite
- Tailwind CSS for styling
- React Router for navigation
- Axios for API calls

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx
│   │   ├── Analysis.jsx
│   │   ├── JobRoles.jsx
│   │   └── Navbar.jsx
│   ├── services/
│   │   └── api.js          # API service layer
│   ├── App.jsx             # Main app with routing
│   ├── main.jsx
│   └── index.css
├── public/
├── index.html
├── package.json
└── tailwind.config.js
```

### API Endpoints Used
- `GET /api/job-roles/statistics/` - Dashboard stats
- `GET /api/employees/workload_stats/` - Workload data
- `GET /api/job-roles/by_department/` - All roles grouped
- `POST /api/analysis-runs/trigger/` - Start analysis
- `GET /api/analysis-runs/latest/` - Latest results
- `GET /api/analysis-runs/` - Analysis history

---

## 🎨 Design Features

### Color Scheme
- **Blue**: Primary actions, AI analysis
- **Green**: Success states, normal workload
- **Red**: Alerts, overloaded employees, critical priority
- **Orange**: High priority
- **Yellow**: Medium priority
- **Purple**: Secondary actions

### Responsive Design
- Mobile-friendly (375px+)
- Tablet optimized (768px+)
- Desktop full experience (1024px+)

### UX Features
- Loading spinners during API calls
- Hover effects on interactive elements
- Smooth transitions
- Clear visual hierarchy
- Intuitive navigation

---

## 🔧 Customization

### Change API URL
Edit `frontend/.env`:
```env
VITE_API_URL=https://your-api-domain.com/api
```

### Modify Colors
Edit `frontend/tailwind.config.js` to customize the theme.

### Add New Pages
1. Create component in `src/components/`
2. Add route in `App.jsx`
3. Add navigation link in `Navbar.jsx`

---

## 📦 Build for Production

```bash
cd frontend
npm run build
```

This creates optimized files in `frontend/dist/` ready for deployment.

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
```bash
npm run build
# Upload dist/ folder to Netlify
```

---

## 🐛 Troubleshooting

### Frontend won't start
- Make sure you ran `npm install`
- Check Node.js version (18+ required)

### API errors
- Ensure Django backend is running
- Check `.env` has correct API URL
- Verify CORS is configured in Django

### Analysis takes too long
- Normal! Multi-agent LLM processing takes 30-60 seconds
- Check Django console for progress

### No data showing
- Run `python manage.py generate_sample_data`
- Refresh the page

---

## 🎓 For Your Interview

### What to Demonstrate

1. **Dashboard Overview**
   - "Here's the main dashboard showing our org statistics"
   - "We have 32 roles and 98 employees across 8 departments"
   - "You can see 25% of employees are overloaded"

2. **Trigger Analysis**
   - "I can analyze all departments or select specific ones"
   - "The multi-agent AI system runs for 30-60 seconds"
   - "It uses 5 specialized agents to analyze different dimensions"

3. **View Recommendations**
   - "Here are the missing roles sorted by priority"
   - "Each has a clear justification and expected impact"
   - "We can see required skills and hiring timeline"

4. **Browse Roles**
   - "I can filter by department and search"
   - "Each role shows headcount and required skills"

### Key Points to Mention

- ✅ **Modern React Architecture**: Component-based, reusable
- ✅ **Professional UI**: Tailwind CSS, responsive design
- ✅ **Real-time Updates**: Live data from Django API
- ✅ **User-Friendly**: Intuitive navigation, clear feedback
- ✅ **Production-Ready**: Optimized builds, error handling

---

## 📝 Summary

The frontend provides a **complete, professional interface** for HR teams to:
- Monitor organizational health
- Run AI-powered gap analysis
- Review prioritized recommendations
- Browse current job roles

**Total Development Time**: Added to existing backend (which took 2 days)

**Ready for Production**: Yes, with proper environment configuration

**Impressive Factor**: High - shows full-stack capability and modern UI/UX skills

---

**Your complete HR Analytics system is now ready to demonstrate! 🎉**

