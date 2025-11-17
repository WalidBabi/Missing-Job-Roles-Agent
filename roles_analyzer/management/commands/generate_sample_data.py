"""
Django management command to generate sample HR data
Usage: python manage.py generate_sample_data [--size small|medium|large]
"""
from django.core.management.base import BaseCommand
from roles_analyzer.data_generator import HRDataGenerator
from roles_analyzer.models import JobRole, Employee
import json


class Command(BaseCommand):
    help = 'Generate sample HR data for testing the AI agent'

    def add_arguments(self, parser):
        parser.add_argument(
            '--size',
            type=str,
            default='medium',
            choices=['small', 'medium', 'large'],
            help='Company size: small (20-50), medium (50-150), large (150+)',
        )
        parser.add_argument(
            '--export-sql',
            action='store_true',
            help='Export data as SQL file',
        )
        parser.add_argument(
            '--export-json',
            action='store_true',
            help='Export data as JSON file',
        )

    def handle(self, *args, **options):
        size = options['size']
        
        self.stdout.write(self.style.SUCCESS(f'\nGenerating {size} company data...'))
        
        generator = HRDataGenerator(company_size=size)
        data = generator.generate_full_dataset()
        
        # Display summary
        self.stdout.write(f"\n[*] Generated Data Summary:")
        self.stdout.write(f"  - Company: {data['metadata']['company_name']}")
        self.stdout.write(f"  - Location: {data['metadata']['company_location']}")
        self.stdout.write(f"  - Total Roles: {data['metadata']['total_roles']}")
        self.stdout.write(f"  - Total Employees: {data['metadata']['total_employees']}")
        self.stdout.write(f"  - Departments: {', '.join(data['metadata']['departments'])}")
        
        # Save to database
        self.stdout.write(f"\n[*] Saving to database...")
        
        # Clear existing data
        JobRole.objects.all().delete()
        Employee.objects.all().delete()
        
        # Insert job roles
        job_roles_created = 0
        for role_data in data['job_roles']:
            JobRole.objects.create(**role_data)
            job_roles_created += 1
        
        # Insert employees
        employees_created = 0
        for emp_data in data['employees']:
            role = JobRole.objects.get(role_id=emp_data['role_id'])
            emp_data_copy = emp_data.copy()
            emp_data_copy['role'] = role
            del emp_data_copy['role_id']
            Employee.objects.create(**emp_data_copy)
            employees_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"  [OK] Created {job_roles_created} job roles and {employees_created} employees"
        ))
        
        # Export options
        if options['export_json']:
            filename = f'sample_data_{size}.json'
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f"\n[OK] Exported to {filename}"))
        
        if options['export_sql']:
            from roles_analyzer.data_generator import export_to_sql_format
            filename = f'sample_data_{size}.sql'
            sql_content = export_to_sql_format(data)
            with open(filename, 'w') as f:
                f.write(sql_content)
            self.stdout.write(self.style.SUCCESS(f"[OK] Exported to {filename}"))
        
        # Show validation hints
        self.stdout.write(f"\n[*] Expected Missing Roles (for validation):")
        for dept, roles in data['validation_hints']['expected_missing_roles'].items():
            self.stdout.write(f"\n  {dept}:")
            for role, reason in roles.items():
                self.stdout.write(f"    - {role}: {reason}")
        
        self.stdout.write(self.style.SUCCESS(f"\n[OK] Done! You can now run the analysis.\n"))

