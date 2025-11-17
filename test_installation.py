#!/usr/bin/env python3
"""
Quick installation test script
Run this to verify your setup is working correctly
"""
import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_python_version():
    """Test Python version"""
    print_header("Testing Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print_success("Python version is compatible (3.10+)")
        return True
    else:
        print_error("Python 3.10 or higher required")
        return False

def test_imports():
    """Test if key packages are installed"""
    print_header("Testing Package Imports")
    
    packages = {
        'django': 'Django',
        'rest_framework': 'Django REST Framework',
        'langchain': 'LangChain',
        'langgraph': 'LangGraph',
        'pandas': 'Pandas',
        'faker': 'Faker',
    }
    
    success = True
    for package, name in packages.items():
        try:
            __import__(package)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} not installed")
            success = False
    
    return success

def test_env_file():
    """Test if .env file exists"""
    print_header("Testing Environment Configuration")
    
    if os.path.exists('.env'):
        print_success(".env file exists")
        
        # Check critical settings
        with open('.env', 'r') as f:
            content = f.read()
            
        required = ['SECRET_KEY', 'DB_NAME', 'DB_USER', 'OPENAI_API_KEY']
        for setting in required:
            if setting in content:
                print_success(f"{setting} configured")
            else:
                print_error(f"{setting} missing in .env")
        
        return True
    else:
        print_error(".env file not found")
        print_info("Copy .env.example to .env and configure it")
        return False

def test_django_setup():
    """Test Django setup"""
    print_header("Testing Django Setup")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'missing_roles_project.settings')
        import django
        django.setup()
        print_success("Django configured successfully")
        return True
    except Exception as e:
        print_error(f"Django setup failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print_header("Testing Database Connection")
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        print_info("Make sure MySQL is running and credentials in .env are correct")
        return False

def test_models():
    """Test if models are accessible"""
    print_header("Testing Django Models")
    
    try:
        from roles_analyzer.models import JobRole, Employee, AnalysisRun, MissingRole
        print_success("All models imported successfully")
        
        # Check if tables exist
        try:
            count = JobRole.objects.count()
            print_success(f"Database tables exist ({count} job roles found)")
            
            if count == 0:
                print_info("No data found. Run: python manage.py generate_sample_data")
            
            return True
        except Exception as e:
            print_error("Database tables not created")
            print_info("Run: python manage.py migrate")
            return False
            
    except Exception as e:
        print_error(f"Model import failed: {e}")
        return False

def test_ai_config():
    """Test AI configuration"""
    print_header("Testing AI Configuration")
    
    try:
        from django.conf import settings
        config = settings.AI_CONFIG
        
        provider = config.get('PROVIDER', 'openai')
        print_info(f"LLM Provider: {provider}")
        
        api_key = config.get('OPENAI_API_KEY') or config.get('ANTHROPIC_API_KEY')
        if api_key and len(api_key) > 10:
            print_success("API key configured")
            return True
        else:
            print_error("API key not configured or invalid")
            print_info("Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env")
            return False
            
    except Exception as e:
        print_error(f"AI config failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "🚀 MISSING JOB ROLES AI AGENT - INSTALLATION TEST".center(60))
    print("This will verify your setup is correct\n")
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Package Imports", test_imports()))
    results.append(("Environment Config", test_env_file()))
    results.append(("Django Setup", test_django_setup()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Django Models", test_models()))
    results.append(("AI Configuration", test_ai_config()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n📊 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        print("\nNext steps:")
        print("  1. Generate sample data: python manage.py generate_sample_data")
        print("  2. Start server: python manage.py runserver")
        print("  3. Trigger analysis: curl -X POST http://127.0.0.1:8000/api/analysis-runs/trigger/")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please fix the issues above and run this test again.")
        print("\nSee QUICKSTART.md for detailed setup instructions.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

