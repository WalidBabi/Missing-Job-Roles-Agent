"""
Django models for Job Roles Analysis System
These models mirror the MySQL database structure for analysis results
"""
from django.db import models
from django.db.models import JSONField


class JobRole(models.Model):
    """
    Model representing a job role in the organization
    This reads from existing MySQL HR database
    """
    LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('vp', 'Vice President'),
        ('c_level', 'C-Level Executive'),
    ]
    
    role_id = models.CharField(max_length=50, primary_key=True)
    role_title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    
    # Store as JSON since we're reading from MySQL
    responsibilities = JSONField(default=list, help_text="List of responsibilities")
    required_skills = JSONField(default=list, help_text="List of required skills")
    
    reports_to = models.CharField(max_length=50, null=True, blank=True)
    current_headcount = models.IntegerField(default=0)
    team_size = models.IntegerField(default=0, help_text="Number of direct reports")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_roles'
        ordering = ['department', 'level', 'role_title']
        verbose_name = 'Job Role'
        verbose_name_plural = 'Job Roles'
    
    def __str__(self):
        return f"{self.role_title} ({self.department})"


class Employee(models.Model):
    """
    Model representing employees in the organization
    """
    WORKLOAD_CHOICES = [
        ('underutilized', 'Underutilized'),
        ('normal', 'Normal'),
        ('overloaded', 'Overloaded'),
    ]
    
    employee_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='employees')
    department = models.CharField(max_length=100)
    
    hire_date = models.DateField()
    workload_status = models.CharField(
        max_length=20, 
        choices=WORKLOAD_CHOICES, 
        default='normal'
    )
    
    skills = JSONField(default=list, help_text="List of employee skills")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        ordering = ['department', 'name']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def calculate_workload_status(self) -> str:
        """
        Calculate workload status based on actual metrics:
        - Responsibilities per person in the role
        - Team size (for managers)
        - Headcount in the role (fewer people = more workload per person)
        
        Returns: 'underutilized', 'normal', or 'overloaded'
        """
        role = self.role
        
        # Get number of responsibilities for this role
        responsibility_count = len(role.responsibilities) if role.responsibilities else 0
        
        # Get headcount in this role (how many people share these responsibilities)
        headcount = max(role.current_headcount, 1)  # Avoid division by zero
        
        # Calculate responsibilities per person
        responsibilities_per_person = responsibility_count / headcount
        
        # For managers, add team size as a factor
        team_size_factor = 0
        if role.team_size > 0:
            # Each direct report adds to workload
            # Normalize: 1-3 reports = normal, 4-7 = moderate, 8+ = high
            if role.team_size <= 3:
                team_size_factor = 0
            elif role.team_size <= 7:
                team_size_factor = 2
            else:
                team_size_factor = 5  # High span of control
        
        # Calculate workload score
        workload_score = responsibilities_per_person + team_size_factor
        
        # Determine status based on thresholds
        # These thresholds can be adjusted based on your organization's standards
        if workload_score >= 8:
            return 'overloaded'
        elif workload_score <= 3:
            return 'underutilized'
        else:
            return 'normal'
    
    def update_workload_status(self):
        """Update workload_status based on calculated metrics"""
        self.workload_status = self.calculate_workload_status()
        self.save(update_fields=['workload_status'])
    
    def __str__(self):
        return f"{self.name} - {self.role.role_title}"


class AnalysisRun(models.Model):
    """
    Model to track AI analysis runs and their results
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.AutoField(primary_key=True)
    run_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Analysis parameters
    total_roles_analyzed = models.IntegerField(default=0)
    total_employees_analyzed = models.IntegerField(default=0)
    departments_analyzed = JSONField(default=list)
    
    # Execution details
    execution_time_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Analysis findings
    org_structure_gaps = models.TextField(null=True, blank=True)
    responsibility_gaps = models.TextField(null=True, blank=True)
    workload_gaps = models.TextField(null=True, blank=True)
    skills_gaps = models.TextField(null=True, blank=True)
    
    # Final recommendations (JSON format)
    recommendations = JSONField(default=list)
    
    class Meta:
        db_table = 'analysis_runs'
        ordering = ['-run_date']
        verbose_name = 'Analysis Run'
        verbose_name_plural = 'Analysis Runs'
    
    def __str__(self):
        return f"Analysis Run {self.id} - {self.run_date.strftime('%Y-%m-%d %H:%M')} ({self.status})"


class MissingRole(models.Model):
    """
    Model representing a recommended missing role from AI analysis
    """
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    id = models.AutoField(primary_key=True)
    analysis_run = models.ForeignKey(
        AnalysisRun, 
        on_delete=models.CASCADE, 
        related_name='missing_roles'
    )
    
    # Recommended role details
    recommended_role_title = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    level = models.CharField(max_length=20)
    
    # Justification
    gap_type = models.CharField(
        max_length=100, 
        help_text="Type of gap: structural, skills, workload, etc."
    )
    justification = models.TextField(help_text="Why this role is needed")
    expected_impact = models.TextField(help_text="Expected business impact")
    
    # Priority and sizing
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    recommended_headcount = models.IntegerField(default=1)
    estimated_timeline = models.CharField(
        max_length=100, 
        help_text="e.g., Immediate, 3 months, 6 months"
    )
    
    # Additional metadata
    required_skills = JSONField(default=list)
    responsibilities = JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'missing_roles'
        ordering = ['-analysis_run__run_date', 'priority', 'recommended_role_title']
        verbose_name = 'Missing Role Recommendation'
        verbose_name_plural = 'Missing Role Recommendations'
    
    def __str__(self):
        return f"{self.recommended_role_title} - {self.priority.upper()} priority"


class Conversation(models.Model):
    """
    Model representing a chatbot conversation session
    """
    conversation_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
    
    def __str__(self):
        return f"Conversation {self.conversation_id} ({self.message_count} messages)"
    
    @property
    def message_count(self):
        """Get the number of messages in this conversation"""
        return self.messages.count()
    
    def get_recent_messages(self, limit=10):
        """Get recent messages for context"""
        return self.messages.all().order_by('timestamp')[:limit]


class ConversationMessage(models.Model):
    """
    Model representing a single message in a conversation
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional metadata
    triggered_analysis = models.BooleanField(default=False)
    analysis_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'conversation_messages'
        ordering = ['timestamp']
        verbose_name = 'Conversation Message'
        verbose_name_plural = 'Conversation Messages'
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

