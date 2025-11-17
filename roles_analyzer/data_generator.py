"""
Generate realistic sample HR data for demonstration
"""
from faker import Faker
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

fake = Faker()


class HRDataGenerator:
    """Generates realistic HR organizational data"""
    
    # Realistic departments and their typical roles
    DEPARTMENT_STRUCTURES = {
        'Engineering': {
            'roles': [
                ('Junior Software Engineer', 'junior', ['Python', 'JavaScript', 'Git'], 
                 ['Implement features', 'Bug fixes', 'Write tests', 'Code review participation']),
                ('Software Engineer', 'mid', ['Python', 'JavaScript', 'API Development', 'Testing'], 
                 ['Develop features', 'Code review', 'Bug fixes', 'Documentation']),
                ('Senior Software Engineer', 'senior', ['System Design', 'Python', 'Leadership', 'Cloud'], 
                 ['Architecture design', 'Mentor juniors', 'Technical decisions', 'Code review']),
                ('Frontend Developer', 'mid', ['React', 'TypeScript', 'CSS', 'UI/UX'], 
                 ['Build UI components', 'Implement designs', 'Performance optimization']),
                ('Backend Developer', 'mid', ['Python', 'Django', 'PostgreSQL', 'Redis'], 
                 ['API development', 'Database design', 'Backend services']),
                ('Full Stack Developer', 'mid', ['React', 'Python', 'PostgreSQL', 'Docker'], 
                 ['End-to-end feature development', 'API and UI work', 'Database management']),
                ('DevOps Engineer', 'senior', ['AWS', 'Docker', 'Kubernetes', 'CI/CD'], 
                 ['Infrastructure management', 'Deployment automation', 'Monitoring']),
                ('Tech Lead', 'lead', ['Technical Leadership', 'Architecture', 'Mentoring'], 
                 ['Technical direction', 'Code review oversight', 'Mentor team', 'Sprint planning']),
                ('Engineering Manager', 'manager', ['Leadership', 'Agile', 'Technical Strategy'], 
                 ['Team management', 'Sprint planning', 'Performance reviews', 'Hiring']),
            ],
            'missing_indicators': {
                'QA Engineer': 'No dedicated QA - developers doing own testing',
                'Data Engineer': 'No data pipeline management',
                'Security Engineer': 'Security is ad-hoc, no dedicated role',
            }
        },
        'Product': {
            'roles': [
                ('Product Manager', 'senior', ['Product Strategy', 'Analytics', 'Roadmapping'], 
                 ['Define features', 'Market research', 'Stakeholder management']),
                ('Associate Product Manager', 'junior', ['Product Strategy', 'Analytics', 'Documentation'], 
                 ['Support PM', 'User research', 'Write requirements', 'Track metrics']),
                ('Product Designer', 'mid', ['Figma', 'UI/UX', 'User Research'], 
                 ['Design mockups', 'User testing', 'Design system']),
                ('Senior Product Designer', 'senior', ['Figma', 'UI/UX', 'Design Leadership'], 
                 ['Lead design initiatives', 'Mentor designers', 'Design strategy']),
            ],
            'missing_indicators': {
                'Product Analyst': 'No data-driven product decisions',
                'UX Researcher': 'Limited user research capabilities',
            }
        },
        'Marketing': {
            'roles': [
                ('Marketing Manager', 'manager', ['Digital Marketing', 'Strategy', 'Budget Management'], 
                 ['Campaign planning', 'Budget allocation', 'Team coordination']),
                ('Digital Marketing Specialist', 'mid', ['Google Ads', 'Facebook Ads', 'Analytics'], 
                 ['Run ad campaigns', 'A/B testing', 'Performance reporting', 'Budget optimization']),
                ('Content Writer', 'junior', ['Copywriting', 'SEO', 'Content Strategy'], 
                 ['Write blog posts', 'Create marketing copy', 'Social media']),
                ('Marketing Coordinator', 'junior', ['Marketing Operations', 'Project Management', 'Communication'], 
                 ['Coordinate campaigns', 'Event planning', 'Vendor management', 'Marketing materials']),
            ],
            'missing_indicators': {
                'SEO Specialist': 'Organic search traffic declining',
                'Social Media Manager': 'Inconsistent social presence',
                'Growth Hacker': 'No systematic growth experiments',
            }
        },
        'Sales': {
            'roles': [
                ('Sales Manager', 'manager', ['Sales Strategy', 'CRM', 'Negotiation'], 
                 ['Lead team', 'Close deals', 'Client relationships']),
                ('Senior Account Executive', 'senior', ['Enterprise Sales', 'CRM', 'Negotiation'], 
                 ['Large deal closures', 'Strategic accounts', 'Negotiate contracts', 'Mentor team']),
                ('Account Executive', 'mid', ['Sales', 'CRM', 'Communication'], 
                 ['Client acquisition', 'Demo products', 'Negotiate contracts']),
                ('Sales Development Representative', 'junior', ['Lead Generation', 'CRM', 'Cold Calling'], 
                 ['Prospect outreach', 'Qualify leads', 'Schedule demos', 'Pipeline building']),
            ],
            'missing_indicators': {
                'Sales Operations': 'Manual sales processes, no automation',
                'Business Development': 'No focus on partnerships',
            }
        },
        'Human Resources': {
            'roles': [
                ('HR Manager', 'manager', ['Recruitment', 'Employee Relations', 'HRIS'], 
                 ['Hiring', 'Onboarding', 'Policy management', 'Employee issues']),
                ('Recruiter', 'mid', ['Recruitment', 'Interviewing', 'Sourcing'], 
                 ['Source candidates', 'Screen resumes', 'Coordinate interviews']),
            ],
            'missing_indicators': {
                'L&D Specialist': 'No structured training programs',
                'HR Business Partner': 'HR is reactive, not strategic',
            }
        },
        'Finance': {
            'roles': [
                ('Finance Manager', 'manager', ['Financial Planning', 'Accounting', 'Excel'], 
                 ['Budget management', 'Financial reporting', 'Audits']),
                ('Senior Accountant', 'senior', ['Accounting', 'Financial Reporting', 'Tax'], 
                 ['Month-end close', 'Financial statements', 'Tax preparation', 'Audit support']),
                ('Accountant', 'mid', ['Accounting', 'QuickBooks', 'Tax'], 
                 ['Bookkeeping', 'Invoicing', 'Expense tracking']),
            ],
            'missing_indicators': {
                'Financial Analyst': 'No forward-looking financial analysis',
                'Payroll Specialist': 'Payroll is manual and error-prone',
            }
        },
        'Customer Support': {
            'roles': [
                ('Customer Support Manager', 'manager', ['Support Operations', 'CRM', 'Team Leadership'], 
                 ['Team management', 'Escalations', 'Quality assurance']),
                ('Senior Support Specialist', 'senior', ['Customer Service', 'Technical Support', 'CRM'], 
                 ['Complex issue resolution', 'Customer escalations', 'Train team', 'Knowledge base']),
                ('Support Specialist', 'junior', ['Customer Service', 'Communication', 'CRM'], 
                 ['Answer tickets', 'Help customers', 'Troubleshooting']),
            ],
            'missing_indicators': {
                'Customer Success Manager': 'High churn, no proactive engagement',
                'Technical Support Engineer': 'Complex issues take too long',
            }
        },
        'Operations': {
            'roles': [
                ('Operations Manager', 'manager', ['Process Optimization', 'Project Management'], 
                 ['Process improvement', 'Cross-functional coordination']),
                ('Office Coordinator', 'junior', ['Office Management', 'Organization', 'Communication'], 
                 ['Office supplies', 'Facility management', 'Event coordination', 'Admin support']),
                ('Executive Assistant', 'mid', ['Executive Support', 'Scheduling', 'Communication'], 
                 ['Calendar management', 'Meeting coordination', 'Travel arrangements', 'Executive support']),
            ],
            'missing_indicators': {
                'Business Analyst': 'Decisions based on gut, not data',
                'Office Manager': 'Administrative chaos',
            }
        }
    }
    
    def __init__(self, company_size: str = 'medium'):
        """
        Initialize generator
        Args:
            company_size: 'small' (20-50), 'medium' (50-150), 'large' (150+)
        """
        self.company_size = company_size
        self.size_multipliers = {
            'small': 0.5,
            'medium': 1.0,
            'large': 2.0,
        }
    
    def generate_job_roles(self) -> List[Dict[str, Any]]:
        """Generate job roles with realistic data"""
        roles = []
        role_counter = 1
        multiplier = self.size_multipliers[self.company_size]
        
        for dept, config in self.DEPARTMENT_STRUCTURES.items():
            for role_title, level, skills, responsibilities in config['roles']:
                # Vary headcount based on role
                base_headcount = {
                    'entry': random.randint(1, 3),
                    'junior': random.randint(2, 5),
                    'mid': random.randint(3, 8),
                    'senior': random.randint(1, 4),
                    'lead': random.randint(1, 2),
                    'manager': 1,
                    'director': 1,
                }.get(level, 2)
                
                headcount = max(1, int(base_headcount * multiplier))
                
                # Managers have direct reports
                team_size = random.randint(4, 10) if level == 'manager' else 0
                
                role_id = f"ROLE{role_counter:03d}"
                role_counter += 1
                
                roles.append({
                    'role_id': role_id,
                    'role_title': role_title,
                    'department': dept,
                    'level': level,
                    'responsibilities': responsibilities,
                    'required_skills': skills,
                    'reports_to': None,  # Will be set based on hierarchy
                    'current_headcount': headcount,
                    'team_size': team_size,
                })
        
        # Set reporting structure
        for role in roles:
            if role['level'] in ['entry', 'junior', 'mid', 'senior']:
                # Find manager in same department
                manager = next(
                    (r for r in roles 
                     if r['department'] == role['department'] 
                     and r['level'] == 'manager'),
                    None
                )
                if manager:
                    role['reports_to'] = manager['role_id']
        
        return roles
    
    def generate_employees(self, job_roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate employee records based on job roles"""
        employees = []
        employee_counter = 1
        
        for role in job_roles:
            headcount = role['current_headcount']
            
            for _ in range(headcount):
                # Generate hire date (past 5 years)
                days_ago = random.randint(30, 1825)
                hire_date = datetime.now() - timedelta(days=days_ago)
                
                # Workload status - intentionally create some overloaded people
                # to trigger "missing roles" recommendations
                workload_weights = [0.15, 0.60, 0.25]  # under, normal, over
                workload_status = random.choices(
                    ['underutilized', 'normal', 'overloaded'],
                    weights=workload_weights
                )[0]
                
                employee_id = f"EMP{employee_counter:04d}"
                employee_counter += 1
                
                # Employees have subset of required skills + some extra
                role_skills = role['required_skills']
                employee_skills = random.sample(
                    role_skills, 
                    k=min(len(role_skills), random.randint(2, len(role_skills)))
                )
                # Add some bonus skills
                bonus_skills = ['Communication', 'Teamwork', 'Problem Solving', 
                               'Time Management', 'Creativity']
                employee_skills.extend(random.sample(bonus_skills, k=random.randint(1, 3)))
                
                employees.append({
                    'employee_id': employee_id,
                    'name': fake.name(),
                    'email': fake.email(),
                    'role_id': role['role_id'],
                    'department': role['department'],
                    'hire_date': hire_date.strftime('%Y-%m-%d'),
                    'workload_status': workload_status,
                    'skills': employee_skills,
                })
        
        return employees
    
    def generate_full_dataset(self) -> Dict[str, Any]:
        """Generate complete HR dataset"""
        job_roles = self.generate_job_roles()
        employees = self.generate_employees(job_roles)
        
        # Calculate some org stats
        departments = list(set(role['department'] for role in job_roles))
        total_headcount = sum(role['current_headcount'] for role in job_roles)
        
        # Identify intentional gaps for validation
        missing_roles_hints = {}
        for dept, config in self.DEPARTMENT_STRUCTURES.items():
            if 'missing_indicators' in config:
                missing_roles_hints[dept] = config['missing_indicators']
        
        return {
            'job_roles': job_roles,
            'employees': employees,
            'metadata': {
                'company_name': 'One Development',
                'company_location': 'Dubai, UAE',
                'company_size': self.company_size,
                'total_roles': len(job_roles),
                'total_employees': total_headcount,
                'departments': departments,
                'generation_date': datetime.now().isoformat(),
            },
            'validation_hints': {
                'expected_missing_roles': missing_roles_hints,
                'note': 'These are hints for what the AI should ideally identify'
            }
        }


def export_to_sql_format(data: Dict[str, Any]) -> str:
    """Export data as SQL INSERT statements"""
    sql_statements = []
    
    # Job Roles
    sql_statements.append("-- Job Roles")
    for role in data['job_roles']:
        responsibilities = str(role['responsibilities']).replace("'", "''")
        skills = str(role['required_skills']).replace("'", "''")
        reports_to = f"'{role['reports_to']}'" if role['reports_to'] else "NULL"
        
        sql = f"""INSERT INTO job_roles (role_id, role_title, department, level, 
            responsibilities, required_skills, reports_to, current_headcount, team_size) 
            VALUES ('{role['role_id']}', '{role['role_title']}', '{role['department']}', 
            '{role['level']}', '{responsibilities}', '{skills}', {reports_to}, 
            {role['current_headcount']}, {role['team_size']});"""
        sql_statements.append(sql)
    
    # Employees
    sql_statements.append("\n-- Employees")
    for emp in data['employees']:
        skills = str(emp['skills']).replace("'", "''")
        sql = f"""INSERT INTO employees (employee_id, name, email, role_id, department, 
            hire_date, workload_status, skills) 
            VALUES ('{emp['employee_id']}', '{emp['name']}', '{emp['email']}', 
            '{emp['role_id']}', '{emp['department']}', '{emp['hire_date']}', 
            '{emp['workload_status']}', '{skills}');"""
        sql_statements.append(sql)
    
    return '\n'.join(sql_statements)

