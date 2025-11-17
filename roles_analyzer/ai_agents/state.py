"""
Shared state definition for LangGraph workflow
"""
from typing import TypedDict, List, Dict, Any, Optional


class AnalysisState(TypedDict):
    """State passed between agents in the workflow"""
    
    # Input data
    org_data: Dict[str, Any]  # Raw organizational data
    job_roles: List[Dict[str, Any]]
    employees: List[Dict[str, Any]]
    departments: List[str]
    
    # Previous recommendations to avoid duplicates
    previous_recommendations: Optional[List[Dict[str, Any]]]
    
    # Analysis results from each agent
    org_structure_analysis: Optional[str]
    responsibility_analysis: Optional[str]
    workload_analysis: Optional[str]
    skills_analysis: Optional[str]
    
    # Final output
    recommendations: Optional[List[Dict[str, Any]]]
    
    # Metadata
    analysis_progress: List[str]
    error: Optional[str]

