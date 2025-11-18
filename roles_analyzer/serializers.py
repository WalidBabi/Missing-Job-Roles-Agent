"""
Django REST Framework Serializers
"""
from rest_framework import serializers
from .models import JobRole, Employee, AnalysisRun, MissingRole, Conversation, ConversationMessage


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


class ConversationMessageSerializer(serializers.ModelSerializer):
    """Serializer for conversation messages"""
    class Meta:
        model = ConversationMessage
        fields = ['id', 'role', 'content', 'timestamp', 'triggered_analysis', 'analysis_id']
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    last_message_preview = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'created_at', 'updated_at', 'message_count', 
                  'last_message_preview', 'last_message_time']
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message_preview(self, obj):
        """Get preview of last message"""
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            preview = last_message.content[:100]
            return preview + '...' if len(last_message.content) > 100 else preview
        return None
    
    def get_last_message_time(self, obj):
        """Get timestamp of last message"""
        last_message = obj.messages.order_by('-timestamp').first()
        return last_message.timestamp if last_message else obj.updated_at


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for conversation with messages"""
    messages = ConversationMessageSerializer(many=True, read_only=True)
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'created_at', 'updated_at', 'message_count', 'messages']
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']

