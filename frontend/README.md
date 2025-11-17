# Missing Job Roles AI - Frontend

React frontend for the HR Analytics AI system.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend Django server running on `http://127.0.0.1:8000`

### Installation

```bash
npm install
```

### Configuration

Copy `.env.example` to `.env` and configure:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 📋 Features

- **Dashboard**: View organizational statistics and metrics
- **AI Analysis**: Trigger multi-agent analysis to identify missing roles
- **Job Roles**: Browse all positions by department
- **Real-time Updates**: Get analysis results with detailed recommendations
- **Priority Filtering**: Sort recommendations by priority (Critical, High, Medium, Low)
- **Department Filtering**: Focus on specific departments

## 🎨 Tech Stack

- React 18
- Vite
- Tailwind CSS
- React Router
- Axios

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx       # Main dashboard
│   │   ├── Analysis.jsx        # AI analysis interface
│   │   ├── JobRoles.jsx        # Job roles listing
│   │   └── Navbar.jsx          # Navigation bar
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── App.jsx                 # Main app with routing
│   ├── main.jsx                # Entry point
│   └── index.css               # Tailwind styles
├── public/
├── index.html
└── package.json
```

## 🔌 API Integration

The frontend connects to the Django REST API at the configured `VITE_API_URL`.

Available endpoints:
- `GET /job-roles/` - List all job roles
- `GET /job-roles/statistics/` - Get org statistics
- `GET /employees/workload_stats/` - Get workload distribution
- `POST /analysis-runs/trigger/` - Trigger new analysis
- `GET /analysis-runs/latest/` - Get latest analysis results
- `GET /missing-roles/by_priority/` - Get recommendations by priority

## 🎯 Usage

1. **View Dashboard**: See organization overview and metrics
2. **Run Analysis**: 
   - Navigate to "AI Analysis"
   - Optionally select specific departments
   - Click "Run AI Analysis"
   - Wait 30-60 seconds for results
3. **View Recommendations**: See prioritized missing role recommendations with detailed justifications
4. **Browse Roles**: Explore existing job roles filtered by department

## 🚀 Deployment

### Using Vercel

```bash
npm install -g vercel
vercel
```

### Using Netlify

```bash
npm install -g netlify-cli
npm run build
netlify deploy --prod --dir=dist
```

### Environment Variables for Production

Make sure to set:
```
VITE_API_URL=https://your-api-domain.com/api
```

## 📝 Notes

- Ensure CORS is properly configured in Django backend
- The backend must be running for the frontend to work
- Analysis takes 30-60 seconds due to multi-agent LLM processing

