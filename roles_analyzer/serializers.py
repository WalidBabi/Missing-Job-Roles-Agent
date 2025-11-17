"""
Django REST Framework Serializers
"""
from rest_framework import serializers
from .models import JobRole, Employee, AnalysisRun, MissingRole


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    role_title = serializers.CharField(source='role.role_title', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'


class MissingRoleSerializer(serializers.ModelSerializer):
    analysis_run = serializers.IntegerField(source='analysis_run.id', read_only=True)
    analysis_run_date = serializers.DateTimeField(source='analysis_run.run_date', read_only=True)
    analysis_run_id = serializers.IntegerField(source='analysis_run.id', read_only=True)
    
    class Meta:
        model = MissingRole
        fields = [
            'id', 'analysis_run', 'analysis_run_id', 'analysis_run_date', 
            'recommended_role_title', 'department', 'level',
            'gap_type', 'justification', 'expected_impact',
            'priority', 'recommended_headcount', 'estimated_timeline',
            'required_skills', 'responsibilities'
        ]


class AnalysisRunSerializer(serializers.ModelSerializer):
    missing_roles = MissingRoleSerializer(many=True, read_only=True)
    
    class Meta:
        model = AnalysisRun
        fields = '__all__'
        read_only_fields = [
            'run_date', 'execution_time_seconds', 
            'org_structure_gaps', 'responsibility_gaps', 
            'workload_gaps', 'skills_gaps'
        ]


class AnalysisRunListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    missing_roles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalysisRun
        fields = [
            'id', 'run_date', 'status', 'total_roles_analyzed',
            'total_employees_analyzed', 'departments_analyzed',
            'execution_time_seconds', 'missing_roles_count'
        ]
    
    def get_missing_roles_count(self, obj):
        return obj.missing_roles.count()


class TriggerAnalysisSerializer(serializers.Serializer):
    """Serializer for triggering a new analysis"""
    departments = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Optional: Specific departments to analyze. If empty, analyzes all."
    )
    include_benchmark = serializers.BooleanField(
        default=False,
        help_text="Whether to include industry benchmark comparison"
    )

