"""
Django REST Framework Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count
import time

from .models import JobRole, Employee, AnalysisRun, MissingRole, Conversation, ConversationMessage
from .serializers import (
    JobRoleSerializer, 
    EmployeeSerializer,
    AnalysisRunSerializer,
    AnalysisRunListSerializer,
    MissingRoleSerializer,
    TriggerAnalysisSerializer,
    ConversationSerializer,
    ConversationDetailSerializer
)
from .ai_agents import run_analysis
from .chatbot import HRChatbot
from rest_framework.decorators import api_view


def find_role_in_tree(node, role_id):
    """Helper function to check if a role exists in a tree"""
    if node['role_id'] == role_id:
        return True
    for child in node.get('children', []):
        if find_role_in_tree(child, role_id):
            return True
    return False


class JobRoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing job roles
    
    list: Get all job roles
    retrieve: Get a specific job role by ID
    """
    queryset = JobRole.objects.all()
    serializer_class = JobRoleSerializer
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get job roles grouped by department"""
        departments = JobRole.objects.values('department').annotate(
            role_count=Count('role_id')
        ).order_by('department')
        
        result = {}
        for dept_data in departments:
            dept = dept_data['department']
            roles = JobRole.objects.filter(department=dept)
            result[dept] = JobRoleSerializer(roles, many=True).data
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall job role statistics"""
        total_roles = JobRole.objects.count()
        total_headcount = sum(role.current_headcount for role in JobRole.objects.all())
        departments = JobRole.objects.values_list('department', flat=True).distinct()
        
        return Response({
            'total_roles': total_roles,
            'total_headcount': total_headcount,
            'total_departments': len(departments),
            'departments': list(departments),
        })
    
    @action(detail=False, methods=['get'])
    def org_chart(self, request):
        """Get organizational chart data (hierarchical structure)"""
        from collections import defaultdict
        
        # Get all roles
        all_roles = JobRole.objects.all()
        
        # Build role map
        role_map = {}
        for role in all_roles:
            role_data = {
                'role_id': role.role_id,
                'role_title': role.role_title,
                'department': role.department,
                'level': role.level,
                'current_headcount': role.current_headcount,
                'team_size': role.team_size,
                'reports_to': role.reports_to,
                'children': []
            }
            role_map[role.role_id] = role_data
        
        # Build tree structure - connect children to parents
        root_roles = []
        for role in all_roles:
            role_data = role_map[role.role_id]
            if role.reports_to and role.reports_to in role_map:
                # This role has a parent
                parent = role_map[role.reports_to]
                parent['children'].append(role_data)
            else:
                # This is a root role (no parent)
                root_roles.append(role_data)
        
        # Group roles by department
        # Include: root roles + managers with children (even if they report to someone)
        org_by_dept = defaultdict(list)
        
        # First, add root roles grouped by department
        for role_data in root_roles:
            dept = role_data['department']
            org_by_dept[dept].append(role_data)
        
        # Also include all manager-level roles in each department
        # These are important to show even if they report to someone outside the department
        for role in all_roles:
            role_data = role_map[role.role_id]
            dept = role_data['department']
            
            # Include all manager-level roles (manager, lead, director, vp, c_level)
            # These are key organizational roles that should be visible
            is_leader = role.level in ['manager', 'lead', 'director', 'vp', 'c_level']
            
            if is_leader:
                # Check if it's already in the tree for this department
                found = False
                for dept_role in org_by_dept[dept]:
                    if find_role_in_tree(dept_role, role.role_id):
                        found = True
                        break
                
                # If not found, add it as a root node for this department
                # This ensures managers show up even if they report to someone else
                if not found:
                    org_by_dept[dept].append(role_data)
        
        # Also include any orphaned roles (roles that should have parents but don't)
        for role in all_roles:
            role_data = role_map[role.role_id]
            # If this role has a reports_to but wasn't added as a child, it's orphaned
            if role.reports_to and role.reports_to not in role_map:
                dept = role_data['department']
                # Check if it's already in the tree
                found = False
                for dept_roles in org_by_dept.values():
                    for r in dept_roles:
                        if find_role_in_tree(r, role.role_id):
                            found = True
                            break
                    if found:
                        break
                if not found:
                    org_by_dept[dept].append(role_data)
        
        return Response({
            'hierarchy': dict(org_by_dept),
            'departments': list(org_by_dept.keys()),
        })


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing employees
    
    list: Get all employees
    retrieve: Get a specific employee by ID
    """
    queryset = Employee.objects.all().select_related('role')
    serializer_class = EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def workload_stats(self, request):
        """
        Get workload statistics.
        
        Workload status is calculated based on:
        - Responsibilities per person = (number of role responsibilities) / (headcount in role)
        - Team size factor = additional points for managers with many direct reports
        - Workload score = responsibilities_per_person + team_size_factor
        
        Thresholds:
        - Overloaded: score >= 8
        - Normal: 3 < score < 8
        - Underutilized: score <= 3
        
        Use POST /employees/recalculate_workload/ to recalculate based on current data.
        """
        total = Employee.objects.count()
        
        stats = {
            'total_employees': total,
            'by_status': {
                'overloaded': Employee.objects.filter(workload_status='overloaded').count(),
                'normal': Employee.objects.filter(workload_status='normal').count(),
                'underutilized': Employee.objects.filter(workload_status='underutilized').count(),
            },
            'by_department': {},
            'calculation_method': {
                'formula': 'workload_score = (responsibilities / headcount) + team_size_factor',
                'thresholds': {
                    'overloaded': 'score >= 8',
                    'normal': '3 < score < 8',
                    'underutilized': 'score <= 3'
                },
                'team_size_factors': {
                    '1-3 reports': 0,
                    '4-7 reports': 2,
                    '8+ reports': 5
                }
            }
        }
        
        departments = Employee.objects.values_list('department', flat=True).distinct()
        for dept in departments:
            dept_employees = Employee.objects.filter(department=dept)
            stats['by_department'][dept] = {
                'total': dept_employees.count(),
                'overloaded': dept_employees.filter(workload_status='overloaded').count(),
            }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def recalculate_workload(self, request):
        """
        Recalculate workload status for all employees based on actual metrics.
        This updates workload_status based on:
        - Responsibilities per person in the role
        - Team size (for managers)
        - Headcount in the role
        """
        employees = Employee.objects.select_related('role').all()
        updated_count = 0
        
        for employee in employees:
            old_status = employee.workload_status
            employee.update_workload_status()
            if employee.workload_status != old_status:
                updated_count += 1
        
        return Response({
            'message': f'Recalculated workload status for {employees.count()} employees',
            'updated_count': updated_count,
            'total_employees': employees.count(),
        })
    
    @action(detail=True, methods=['get'])
    def workload_details(self, request, pk=None):
        """
        Get detailed workload calculation for a specific employee.
        Shows the metrics used to determine workload status.
        """
        employee = self.get_object()
        role = employee.role
        
        # Calculate the metrics
        responsibility_count = len(role.responsibilities) if role.responsibilities else 0
        headcount = max(role.current_headcount, 1)
        responsibilities_per_person = responsibility_count / headcount
        
        # Team size factor
        team_size_factor = 0
        if role.team_size > 0:
            if role.team_size <= 3:
                team_size_factor = 0
            elif role.team_size <= 7:
                team_size_factor = 2
            else:
                team_size_factor = 5
        
        workload_score = responsibilities_per_person + team_size_factor
        
        # Determine what would be calculated
        calculated_status = employee.calculate_workload_status()
        
        return Response({
            'employee_id': employee.employee_id,
            'employee_name': employee.name,
            'role_title': role.role_title,
            'department': role.department,
            'current_workload_status': employee.workload_status,
            'calculated_workload_status': calculated_status,
            'calculation_details': {
                'responsibility_count': responsibility_count,
                'headcount_in_role': role.current_headcount,
                'responsibilities_per_person': round(responsibilities_per_person, 2),
                'team_size': role.team_size,
                'team_size_factor': team_size_factor,
                'workload_score': round(workload_score, 2),
                'thresholds': {
                    'overloaded': '>= 8',
                    'normal': '3 < score < 8',
                    'underutilized': '<= 3'
                }
            }
        })


class AnalysisRunViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for analysis runs
    
    list: Get all analysis runs
    retrieve: Get a specific analysis run with full details
    trigger: Start a new analysis run
    """
    queryset = AnalysisRun.objects.all().prefetch_related('missing_roles')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnalysisRunListSerializer
        return AnalysisRunSerializer
    
    @action(detail=False, methods=['post'])
    def trigger(self, request):
        """
        Trigger a new AI analysis run
        
        Body:
        {
            "departments": ["Engineering", "Product"],  // Optional
            "include_benchmark": false  // Optional
        }
        """
        serializer = TriggerAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get parameters
        departments = serializer.validated_data.get('departments', [])
        include_benchmark = serializer.validated_data.get('include_benchmark', False)
        
        # Create analysis run record
        analysis_run = AnalysisRun.objects.create(
            status='running',
        )
        
        try:
            start_time = time.time()
            
            # Load data from database
            if departments:
                job_roles_qs = JobRole.objects.filter(department__in=departments)
                employees_qs = Employee.objects.filter(department__in=departments)
            else:
                job_roles_qs = JobRole.objects.all()
                employees_qs = Employee.objects.all()
            
            # Convert to dictionaries for the AI agents
            job_roles = []
            for role in job_roles_qs:
                job_roles.append({
                    'role_id': role.role_id,
                    'role_title': role.role_title,
                    'department': role.department,
                    'level': role.level,
                    'responsibilities': role.responsibilities,
                    'required_skills': role.required_skills,
                    'reports_to': role.reports_to,
                    'current_headcount': role.current_headcount,
                    'team_size': role.team_size,
                })
            
            employees = []
            for emp in employees_qs:
                employees.append({
                    'employee_id': emp.employee_id,
                    'name': emp.name,
                    'role_id': emp.role.role_id,
                    'department': emp.department,
                    'workload_status': emp.workload_status,
                    'skills': emp.skills,
                })
            
            dept_list = list(job_roles_qs.values_list('department', flat=True).distinct())
            
            # Retrieve previous recommendations to avoid duplicates
            previous_recommendations = []
            previous_runs = AnalysisRun.objects.filter(
                status='completed'
            ).exclude(id=analysis_run.id).order_by('-run_date')[:5]  # Get last 5 completed runs
            
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
            
            # Run AI analysis
            result = run_analysis(
                job_roles=job_roles,
                employees=employees,
                departments=dept_list,
                previous_recommendations=previous_recommendations
            )
            
            execution_time = time.time() - start_time
            
            # Update analysis run with results
            analysis_run.status = 'completed' if result['success'] else 'failed'
            analysis_run.total_roles_analyzed = len(job_roles)
            analysis_run.total_employees_analyzed = len(employees)
            analysis_run.departments_analyzed = dept_list
            analysis_run.execution_time_seconds = round(execution_time, 2)
            
            if result['success']:
                analysis_run.org_structure_gaps = result.get('org_structure_analysis', '')
                analysis_run.responsibility_gaps = result.get('responsibility_analysis', '')
                analysis_run.workload_gaps = result.get('workload_analysis', '')
                analysis_run.skills_gaps = result.get('skills_analysis', '')
                analysis_run.recommendations = result.get('recommendations', [])
                
                # Create MissingRole records
                for rec in result.get('recommendations', []):
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
            else:
                analysis_run.error_message = result.get('error', 'Unknown error')
            
            analysis_run.save()
            
            # Return result
            serializer = AnalysisRunSerializer(analysis_run)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # Mark as failed
            analysis_run.status = 'failed'
            analysis_run.error_message = str(e)
            analysis_run.save()
            
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """Get just the recommendations for a specific analysis run"""
        analysis_run = self.get_object()
        missing_roles = analysis_run.missing_roles.all()
        serializer = MissingRoleSerializer(missing_roles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest analysis run"""
        latest_run = AnalysisRun.objects.filter(status='completed').order_by('-run_date').first()
        
        if not latest_run:
            return Response(
                {'message': 'No completed analysis runs found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AnalysisRunSerializer(latest_run)
        return Response(serializer.data)


class MissingRoleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing missing role recommendations
    """
    queryset = MissingRole.objects.all().select_related('analysis_run')
    serializer_class = MissingRoleSerializer
    
    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        """Get missing roles grouped by priority"""
        priorities = ['critical', 'high', 'medium', 'low']
        result = {}
        
        for priority in priorities:
            roles = MissingRole.objects.filter(priority=priority).order_by('-analysis_run__run_date')
            result[priority] = MissingRoleSerializer(roles, many=True).data
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get missing roles grouped by department"""
        departments = MissingRole.objects.values_list('department', flat=True).distinct()
        result = {}
        
        for dept in departments:
            roles = MissingRole.objects.filter(department=dept).order_by('-analysis_run__run_date')
            result[dept] = MissingRoleSerializer(roles, many=True).data
        
        return Response(result)


@api_view(['POST'])
def chatbot_message(request):
    """
    Chatbot endpoint for conversational HR assistance
    """
    user_message = request.data.get('message', '').strip()
    conversation_id = request.data.get('conversation_id', None)
    
    if not user_message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        chatbot = HRChatbot()
        result = chatbot.chat(user_message, conversation_id)
        
        return Response({
            'response': result['response'],
            'conversation_id': result.get('conversation_id'),
            'triggered_analysis': result.get('triggered_analysis', False),
            'recommendations_count': result.get('recommendations_count', 0),
            'analysis_id': result.get('analysis_id'),
        })
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_conversations(request):
    """
    List all conversations ordered by most recent
    """
    try:
        conversations = Conversation.objects.all().order_by('-updated_at')[:50]  # Limit to 50 most recent
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_conversation(request, conversation_id):
    """
    Get a specific conversation with all its messages
    """
    try:
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        serializer = ConversationDetailSerializer(conversation)
        return Response(serializer.data)
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

