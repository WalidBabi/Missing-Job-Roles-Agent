"""
Django Admin configuration for Job Roles Analyzer
"""
from django.contrib import admin
from .models import JobRole, Employee, AnalysisRun, MissingRole


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ['role_id', 'role_title', 'department', 'level', 'current_headcount', 'team_size']
    list_filter = ['department', 'level']
    search_fields = ['role_id', 'role_title', 'department']
    ordering = ['department', 'role_title']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'name', 'role', 'department', 'workload_status', 'hire_date']
    list_filter = ['department', 'workload_status']
    search_fields = ['employee_id', 'name', 'email']
    ordering = ['name']


@admin.register(AnalysisRun)
class AnalysisRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'run_date', 'status', 'total_roles_analyzed', 'total_employees_analyzed', 'execution_time_seconds']
    list_filter = ['status', 'run_date']
    readonly_fields = ['run_date', 'execution_time_seconds']
    ordering = ['-run_date']


@admin.register(MissingRole)
class MissingRoleAdmin(admin.ModelAdmin):
    list_display = ['recommended_role_title', 'department', 'priority', 'recommended_headcount', 'analysis_run']
    list_filter = ['priority', 'department', 'gap_type']
    search_fields = ['recommended_role_title', 'justification']
    ordering = ['-analysis_run__run_date', 'priority']

