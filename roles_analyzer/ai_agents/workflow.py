"""
LangGraph workflow orchestration
"""
import sys
import os
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import AnalysisState
from .agents import (
    org_structure_analyzer,
    responsibility_analyzer,
    workload_analyzer,
    skills_analyzer,
    synthesizer
)

# Set UTF-8 encoding for stdout on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Python < 3.7 or already configured
        pass

# Import safe print function
try:
    from ..utils import safe_print as print
except ImportError:
    # Fallback if utils not available
    import builtins
    def safe_print(*args, **kwargs):
        try:
            builtins.print(*args, **kwargs)
        except UnicodeEncodeError:
            # Replace emojis with ASCII
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    safe_args.append(arg.replace('🚀', '[START]').replace('✅', '[OK]').replace('❌', '[ERROR]'))
                else:
                    safe_args.append(arg)
            builtins.print(*safe_args, **kwargs)
    print = safe_print


def create_analysis_workflow():
    """
    Creates the LangGraph workflow for multi-agent analysis
    
    Workflow:
    1. Org Structure Analyzer
    2. Responsibility Analyzer  
    3. Workload Analyzer
    4. Skills Analyzer
    5. Synthesizer (combines all findings)
    """
    
    # Create state graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes (agents)
    workflow.add_node("org_structure", org_structure_analyzer)
    workflow.add_node("responsibilities", responsibility_analyzer)
    workflow.add_node("workload", workload_analyzer)
    workflow.add_node("skills", skills_analyzer)
    workflow.add_node("synthesize", synthesizer)
    
    # Define sequential flow
    workflow.set_entry_point("org_structure")
    workflow.add_edge("org_structure", "responsibilities")
    workflow.add_edge("responsibilities", "workload")
    workflow.add_edge("workload", "skills")
    workflow.add_edge("skills", "synthesize")
    workflow.add_edge("synthesize", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def run_analysis(job_roles: list, employees: list, departments: list, previous_recommendations: list = None) -> Dict[str, Any]:
    """
    Run the full multi-agent analysis
    
    Args:
        job_roles: List of job role dictionaries
        employees: List of employee dictionaries
        departments: List of department names
        previous_recommendations: Optional list of previous recommendations to avoid duplicates
    
    Returns:
        Dictionary with analysis results and recommendations
    """
    print("\n" + "="*60)
    print("🚀 Starting Multi-Agent Analysis Workflow")
    print("="*60 + "\n")
    
    # Create workflow
    workflow = create_analysis_workflow()
    
    # Prepare initial state
    initial_state: AnalysisState = {
        "org_data": {
            "job_roles": job_roles,
            "employees": employees,
            "departments": departments,
        },
        "job_roles": job_roles,
        "employees": employees,
        "departments": departments,
        "previous_recommendations": previous_recommendations or [],
        "org_structure_analysis": None,
        "responsibility_analysis": None,
        "workload_analysis": None,
        "skills_analysis": None,
        "recommendations": None,
        "analysis_progress": [],
        "error": None,
    }
    
    # Run workflow
    try:
        result = workflow.invoke(initial_state)
        
        print("\n" + "="*60)
        print("✅ Analysis Complete!")
        print("="*60 + "\n")
        
        return {
            "success": True,
            "recommendations": result.get("recommendations", []),
            "org_structure_analysis": result.get("org_structure_analysis"),
            "responsibility_analysis": result.get("responsibility_analysis"),
            "workload_analysis": result.get("workload_analysis"),
            "skills_analysis": result.get("skills_analysis"),
            "analysis_progress": result.get("analysis_progress", []),
            "error": result.get("error"),
        }
    
    except Exception as e:
        print(f"\n❌ Analysis Failed: {e}\n")
        return {
            "success": False,
            "recommendations": [],
            "error": str(e),
        }

