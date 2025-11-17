"""
Conversational chatbot for HR that uses the multi-agent system
"""
from typing import Dict, List, Optional
from langchain.prompts import ChatPromptTemplate
from .ai_agents.llm_factory import get_llm
from .models import JobRole, Employee, AnalysisRun, MissingRole
from .ai_agents import run_analysis
import json


class HRChatbot:
    """
    Conversational chatbot that intelligently uses the multi-agent system
    """
    
    def __init__(self):
        self.llm = get_llm(temperature=0.3)
        self.conversation_history = []
    
    def _get_context_data(self) -> Dict:
        """Get current organizational context"""
        total_roles = JobRole.objects.count()
        total_employees = Employee.objects.count()
        departments = list(JobRole.objects.values_list('department', flat=True).distinct())
        
        latest_analysis = AnalysisRun.objects.filter(status='completed').order_by('-run_date').first()
        missing_roles_count = 0
        if latest_analysis:
            missing_roles_count = latest_analysis.missing_roles.count()
        
        return {
            'total_roles': total_roles,
            'total_employees': total_employees,
            'departments': departments,
            'latest_analysis_date': latest_analysis.run_date.isoformat() if latest_analysis else None,
            'missing_roles_count': missing_roles_count,
        }
    
    def _should_trigger_analysis(self, user_message: str):
        """
        Determine if user message requires running a new analysis
        Returns: (should_trigger, departments_to_analyze)
        """
        trigger_keywords = [
            'analyze', 'analysis', 'run analysis', 'check', 'find missing',
            'what roles', 'what are we missing', 'identify gaps', 'recommendations'
        ]
        
        user_lower = user_message.lower()
        
        # Check if user wants to trigger analysis
        should_trigger = any(keyword in user_lower for keyword in trigger_keywords)
        
        # Extract department mentions
        departments = []
        context = self._get_context_data()
        for dept in context['departments']:
            if dept.lower() in user_lower:
                departments.append(dept)
        
        return should_trigger, departments if departments else None
    
    def _get_latest_recommendations(self, department: Optional[str] = None) -> List[Dict]:
        """Get latest missing role recommendations"""
        latest_analysis = AnalysisRun.objects.filter(status='completed').order_by('-run_date').first()
        
        if not latest_analysis:
            return []
        
        missing_roles = latest_analysis.missing_roles.all()
        if department:
            missing_roles = missing_roles.filter(department=department)
        
        return [
            {
                'role_title': mr.recommended_role_title,
                'department': mr.department,
                'priority': mr.priority,
                'justification': mr.justification,
                'expected_impact': mr.expected_impact,
            }
            for mr in missing_roles[:10]  # Limit to top 10
        ]
    
    def _format_recommendations_for_chat(self, recommendations: List[Dict]) -> str:
        """Format recommendations in a conversational way"""
        if not recommendations:
            return "No missing roles have been identified yet. Would you like me to run an analysis?"
        
        response = f"I found {len(recommendations)} recommended missing roles:\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            priority_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(rec['priority'], '⚪')
            
            response += f"{priority_emoji} **{rec['role_title']}** ({rec['department']}) - {rec['priority'].upper()} priority\n"
            response += f"   Why: {rec['justification'][:150]}...\n\n"
        
        return response
    
    def chat(self, user_message: str, conversation_id: Optional[str] = None) -> Dict:
        """
        Main chat method - handles user messages intelligently
        
        Args:
            user_message: User's question/message
            conversation_id: Optional conversation ID for context
        
        Returns:
            Dictionary with response and metadata
        """
        context = self._get_context_data()
        should_trigger, departments = self._should_trigger_analysis(user_message)
        
        # If user wants to trigger analysis, do it
        if should_trigger:
            return self._handle_analysis_request(user_message, departments)
        
        # Otherwise, provide conversational response
        return self._handle_conversational_query(user_message, context)
    
    def _handle_analysis_request(self, user_message: str, departments: Optional[List[str]]) -> Dict:
        """Handle requests to run analysis"""
        try:
            # Get data for analysis
            if departments:
                job_roles_qs = JobRole.objects.filter(department__in=departments)
                employees_qs = Employee.objects.filter(department__in=departments)
            else:
                job_roles_qs = JobRole.objects.all()
                employees_qs = Employee.objects.all()
            
            job_roles = [
                {
                    'role_id': role.role_id,
                    'role_title': role.role_title,
                    'department': role.department,
                    'level': role.level,
                    'responsibilities': role.responsibilities,
                    'required_skills': role.required_skills,
                    'reports_to': role.reports_to,
                    'current_headcount': role.current_headcount,
                    'team_size': role.team_size,
                }
                for role in job_roles_qs
            ]
            
            employees = [
                {
                    'employee_id': emp.employee_id,
                    'name': emp.name,
                    'role_id': emp.role.role_id,
                    'department': emp.department,
                    'workload_status': emp.workload_status,
                    'skills': emp.skills,
                }
                for emp in employees_qs
            ]
            
            dept_list = list(job_roles_qs.values_list('department', flat=True).distinct())
            
            # Retrieve previous recommendations to avoid duplicates
            previous_recommendations = []
            previous_runs = AnalysisRun.objects.filter(
                status='completed'
            ).order_by('-run_date')[:5]  # Get last 5 completed runs
            
            for prev_run in previous_runs:
                prev_missing_roles = prev_run.missing_roles.all()
                for mr in prev_missing_roles:
                    previous_recommendations.append({
                        'role_title': mr.recommended_role_title,
                        'department': mr.department,
                        'level': mr.level,
                        'gap_type': mr.gap_type,
                        'justification': mr.justification,
                        'expected_impact': mr.expected_impact,
                        'priority': mr.priority,
                        'recommended_headcount': mr.recommended_headcount,
                        'estimated_timeline': mr.estimated_timeline,
                        'required_skills': mr.required_skills,
                        'responsibilities': mr.responsibilities,
                    })
            
            # Run analysis
            result = run_analysis(
                job_roles=job_roles,
                employees=employees,
                departments=dept_list,
                previous_recommendations=previous_recommendations
            )
            
            if result['success']:
                recommendations = result.get('recommendations', [])
                
                # Save to database
                analysis_run = AnalysisRun.objects.create(
                    status='completed',
                    total_roles_analyzed=len(job_roles),
                    total_employees_analyzed=len(employees),
                    departments_analyzed=dept_list,
                    recommendations=recommendations,
                )
                
                for rec in recommendations:
                    MissingRole.objects.create(
                        analysis_run=analysis_run,
                        recommended_role_title=rec.get('role_title', 'Unknown'),
                        department=rec.get('department', 'Unknown'),
                        level=rec.get('level', 'mid'),
                        gap_type=rec.get('gap_type', 'unknown'),
                        justification=rec.get('justification', ''),
                        expected_impact=rec.get('expected_impact', ''),
                        priority=rec.get('priority', 'medium'),
                        recommended_headcount=rec.get('recommended_headcount', 1),
                        estimated_timeline=rec.get('estimated_timeline', ''),
                        required_skills=rec.get('required_skills', []),
                        responsibilities=rec.get('responsibilities', []),
                    )
                
                response_text = f"✅ Analysis complete! I analyzed {len(job_roles)} roles and {len(employees)} employees.\n\n"
                
                if recommendations:
                    response_text += f"I found **{len(recommendations)} missing roles** that you should consider:\n\n"
                    for i, rec in enumerate(recommendations[:5], 1):
                        priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡'}.get(rec.get('priority', 'medium'), '⚪')
                        response_text += f"{priority_emoji} **{rec.get('role_title', 'Unknown')}** ({rec.get('department', 'Unknown')}) - {rec.get('priority', 'medium').upper()}\n"
                        response_text += f"   {rec.get('justification', '')[:120]}...\n\n"
                    
                    if len(recommendations) > 5:
                        response_text += f"\n_...and {len(recommendations) - 5} more. Check the Analysis page for full details._"
                else:
                    response_text += "Great news! Your organization structure looks healthy - no critical gaps identified."
                
                return {
                    'response': response_text,
                    'triggered_analysis': True,
                    'recommendations_count': len(recommendations),
                    'analysis_id': analysis_run.id,
                }
            else:
                return {
                    'response': "❌ I encountered an error while running the analysis. Please try again or check the system logs.",
                    'triggered_analysis': False,
                    'error': result.get('error'),
                }
        
        except Exception as e:
            return {
                'response': f"❌ Sorry, I encountered an error: {str(e)}",
                'triggered_analysis': False,
                'error': str(e),
            }
    
    def _handle_conversational_query(self, user_message: str, context: Dict) -> Dict:
        """Handle general conversational queries"""
        # Get latest recommendations for context
        latest_recommendations = self._get_latest_recommendations()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful HR assistant chatbot for an organization. You help HR professionals understand their organizational structure, identify missing roles, and get insights about their workforce.

You have access to:
- Organizational data: {total_roles} job roles, {total_employees} employees across {departments_count} departments
- Latest analysis results: {missing_roles_count} missing roles identified
- Departments: {departments}

When users ask about missing roles or recommendations, reference the latest analysis results if available.
Be conversational, friendly, and professional. Provide specific, actionable insights.
If asked about specific departments or roles, be detailed and helpful.

If the user wants to run a new analysis, tell them to use phrases like "run analysis" or "analyze organization"."""),
            ("user", "{user_message}")
        ])
        
        departments_str = ", ".join(context['departments'])
        recommendations_context = ""
        if latest_recommendations:
            recommendations_context = "\n\nLatest Recommendations:\n"
            for rec in latest_recommendations[:3]:
                recommendations_context += f"- {rec['role_title']} ({rec['department']}) - {rec['priority']} priority\n"
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_message": user_message + recommendations_context,
            "total_roles": context['total_roles'],
            "total_employees": context['total_employees'],
            "departments_count": len(context['departments']),
            "departments": departments_str,
            "missing_roles_count": context['missing_roles_count'],
        })
        
        return {
            'response': response.content,
            'triggered_analysis': False,
        }

