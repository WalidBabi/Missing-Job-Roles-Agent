"""
Individual AI agents for analyzing different aspects of organizational structure
"""
import json
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from .llm_factory import get_llm
from .state import AnalysisState


def org_structure_analyzer(state: AnalysisState) -> Dict[str, Any]:
    """
    Analyzes organizational structure for gaps and inefficiencies
    - Span of control issues
    - Missing management layers
    - Reporting structure problems
    """
    print("🔍 Running Organizational Structure Analysis...")
    
    llm = get_llm(temperature=0.1)
    
    # Prepare data summary
    roles = state['job_roles']
    total_roles = len(roles)
    
    # Build org hierarchy summary
    hierarchy_summary = []
    for role in roles:
        hierarchy_summary.append({
            'role': role['role_title'],
            'department': role['department'],
            'level': role['level'],
            'headcount': role['current_headcount'],
            'team_size': role['team_size'],
            'reports_to': role.get('reports_to', 'None')
        })
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an organizational structure expert specializing in HR analytics.

Analyze the organizational hierarchy for structural inefficiencies and gaps:

1. **Span of Control**: Identify managers with too many direct reports (>8-10 is problematic)
2. **Management Layers**: Check if there are missing middle management positions
3. **Flat Structures**: Large departments without proper hierarchy
4. **Single Points of Failure**: Critical functions with only one person
5. **Missing Roles**: Identify structural gaps (e.g., no team leads between ICs and managers)

Provide specific, actionable findings with evidence from the data."""),
        ("user", """
Organization Data:
- Total Roles: {total_roles}
- Departments: {departments}

Organizational Hierarchy:
{hierarchy_json}

Analyze the structure and identify gaps. Focus on:
- Which departments need additional management layers?
- Are there missing team lead or supervisor roles?
- Any bottlenecks in reporting structure?

Provide your analysis in a structured format with specific recommendations.
""")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "total_roles": total_roles,
            "departments": ", ".join(state['departments']),
            "hierarchy_json": json.dumps(hierarchy_summary, indent=2)
        })
        
        analysis_text = response.content
        
        return {
            "org_structure_analysis": analysis_text,
            "analysis_progress": state.get("analysis_progress", []) + ["org_structure"]
        }
    
    except Exception as e:
        print(f"❌ Error in org structure analysis: {e}")
        return {
            "org_structure_analysis": f"Error: {str(e)}",
            "analysis_progress": state.get("analysis_progress", []) + ["org_structure_error"],
            "error": str(e)
        }


def responsibility_analyzer(state: AnalysisState) -> Dict[str, Any]:
    """
    Analyzes whether critical business responsibilities are covered
    - Missing critical functions
    - Overlap and redundancy
    - Coverage gaps
    """
    print("🔍 Running Responsibility Coverage Analysis...")
    
    llm = get_llm(temperature=0.1)
    
    # Collect all responsibilities by department
    dept_responsibilities = {}
    for role in state['job_roles']:
        dept = role['department']
        if dept not in dept_responsibilities:
            dept_responsibilities[dept] = []
        
        dept_responsibilities[dept].append({
            'role': role['role_title'],
            'responsibilities': role['responsibilities'],
            'headcount': role['current_headcount']
        })
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a business operations expert specializing in organizational design.

Analyze the distribution of responsibilities across the organization:

1. **Critical Functions**: Check if standard business functions are covered (strategy, operations, compliance, etc.)
2. **Department-Specific Gaps**: Identify missing functions within each department
3. **Overlap Detection**: Find redundant responsibilities that could be consolidated
4. **Workload Balance**: Check if responsibilities are distributed appropriately

Common gaps to look for:
- Engineering: QA, Security, Data Engineering, Tech Lead
- Product: Product Analytics, UX Research
- Marketing: SEO, Growth, Social Media Management
- HR: L&D, HRBP, Compensation Specialist
- Finance: Financial Planning & Analysis, Payroll
- Sales: Sales Operations, Business Development
- Support: Customer Success, Technical Support

Provide specific missing role recommendations based on responsibility gaps."""),
        ("user", """
Responsibilities by Department:
{responsibilities_json}

Analyze what critical responsibilities are NOT being covered and recommend specific roles needed.
""")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "responsibilities_json": json.dumps(dept_responsibilities, indent=2)
        })
        
        return {
            "responsibility_analysis": response.content,
            "analysis_progress": state.get("analysis_progress", []) + ["responsibilities"]
        }
    
    except Exception as e:
        print(f"❌ Error in responsibility analysis: {e}")
        return {
            "responsibility_analysis": f"Error: {str(e)}",
            "analysis_progress": state.get("analysis_progress", []) + ["responsibilities_error"],
            "error": str(e)
        }


def workload_analyzer(state: AnalysisState) -> Dict[str, Any]:
    """
    Analyzes workload and capacity issues
    - Overloaded employees
    - Understaffed roles
    - Capacity constraints
    """
    print("🔍 Running Workload & Capacity Analysis...")
    
    llm = get_llm(temperature=0.1)
    
    # Calculate workload statistics
    workload_stats = {}
    for dept in state['departments']:
        dept_employees = [e for e in state['employees'] if e['department'] == dept]
        
        total = len(dept_employees)
        overloaded = len([e for e in dept_employees if e['workload_status'] == 'overloaded'])
        underutilized = len([e for e in dept_employees if e['workload_status'] == 'underutilized'])
        
        workload_stats[dept] = {
            'total_employees': total,
            'overloaded_count': overloaded,
            'overloaded_percentage': round((overloaded / total * 100), 1) if total > 0 else 0,
            'underutilized_count': underutilized,
        }
    
    # Role-level analysis
    role_workload = []
    for role in state['job_roles']:
        role_employees = [e for e in state['employees'] if e['role_id'] == role['role_id']]
        
        overloaded = len([e for e in role_employees if e['workload_status'] == 'overloaded'])
        
        responsibility_count = len(role['responsibilities'])
        
        role_workload.append({
            'role': role['role_title'],
            'department': role['department'],
            'headcount': role['current_headcount'],
            'overloaded_employees': overloaded,
            'responsibilities_count': responsibility_count,
            'responsibilities_per_person': round(responsibility_count / max(role['current_headcount'], 1), 2)
        })
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a workforce planning expert.

Analyze workload distribution and capacity constraints:

1. **High Overload Rates**: Departments/roles with >20% overloaded employees need help
2. **Responsibility Overload**: Roles with too many responsibilities need to be split
3. **Single Points of Failure**: Critical roles with only 1 person and high workload
4. **Capacity Planning**: Identify where additional headcount is needed vs. new role types

When overload is high, recommend either:
- Additional headcount for existing roles
- New specialized roles to offload specific responsibilities

Be specific about which roles are needed and why."""),
        ("user", """
Workload Statistics by Department:
{workload_dept_json}

Role-Level Workload Analysis:
{workload_role_json}

Identify which roles are understaffed or need new supporting roles.
""")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "workload_dept_json": json.dumps(workload_stats, indent=2),
            "workload_role_json": json.dumps(role_workload, indent=2)
        })
        
        return {
            "workload_analysis": response.content,
            "analysis_progress": state.get("analysis_progress", []) + ["workload"]
        }
    
    except Exception as e:
        print(f"❌ Error in workload analysis: {e}")
        return {
            "workload_analysis": f"Error: {str(e)}",
            "analysis_progress": state.get("analysis_progress", []) + ["workload_error"],
            "error": str(e)
        }


def skills_analyzer(state: AnalysisState) -> Dict[str, Any]:
    """
    Analyzes skills gaps in the organization
    - Missing critical skills
    - Emerging skill requirements
    - Skills concentration risks
    """
    print("🔍 Running Skills Gap Analysis...")
    
    llm = get_llm(temperature=0.1)
    
    # Collect required vs available skills
    required_skills_by_dept = {}
    available_skills_by_dept = {}
    
    for dept in state['departments']:
        # Required skills (from job roles)
        dept_roles = [r for r in state['job_roles'] if r['department'] == dept]
        required = set()
        for role in dept_roles:
            required.update(role['required_skills'])
        required_skills_by_dept[dept] = list(required)
        
        # Available skills (from employees)
        dept_employees = [e for e in state['employees'] if e['department'] == dept]
        available = set()
        for emp in dept_employees:
            available.update(emp['skills'])
        available_skills_by_dept[dept] = list(available)
    
    # Find gaps
    skills_gaps = {}
    for dept in state['departments']:
        required_set = set(required_skills_by_dept.get(dept, []))
        available_set = set(available_skills_by_dept.get(dept, []))
        missing = required_set - available_set
        
        if missing:
            skills_gaps[dept] = list(missing)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a talent acquisition and workforce planning expert.

Analyze skills gaps across the organization:

1. **Critical Missing Skills**: Skills required but not present in the organization
2. **Emerging Needs**: Modern skills needed for digital transformation (Cloud, AI/ML, Data, Security, etc.)
3. **Skill Concentration Risk**: Critical skills held by too few people
4. **Department-Specific Gaps**: Which departments lack key competencies

For each significant gap, recommend:
- Specific role types that would fill the skill gap
- Priority level (Critical/High/Medium)
- Justification based on business impact

Consider modern business needs like:
- Digital transformation skills
- Data literacy and analytics
- Security and compliance
- Customer experience
- Automation and efficiency"""),
        ("user", """
Skills Analysis:

Required Skills by Department:
{required_skills_json}

Available Skills by Department:
{available_skills_json}

Identified Skills Gaps:
{skills_gaps_json}

Recommend specific roles to fill these skills gaps, prioritizing by business impact.
""")
    ])
    
    try:
        chain = prompt | llm
        response = chain.invoke({
            "required_skills_json": json.dumps(required_skills_by_dept, indent=2),
            "available_skills_json": json.dumps(available_skills_by_dept, indent=2),
            "skills_gaps_json": json.dumps(skills_gaps, indent=2)
        })
        
        return {
            "skills_analysis": response.content,
            "analysis_progress": state.get("analysis_progress", []) + ["skills"]
        }
    
    except Exception as e:
        print(f"❌ Error in skills analysis: {e}")
        return {
            "skills_analysis": f"Error: {str(e)}",
            "analysis_progress": state.get("analysis_progress", []) + ["skills_error"],
            "error": str(e)
        }


def synthesizer(state: AnalysisState) -> Dict[str, Any]:
    """
    Synthesizes all analyses into prioritized, actionable recommendations
    """
    print("🔍 Synthesizing Final Recommendations...")
    
    llm = get_llm(temperature=0.3)  # Slightly higher for creative synthesis
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a senior HR strategy consultant synthesizing multiple analyses.

Your task: Combine all the analyses into a prioritized list of missing job role recommendations.

For EACH recommended role, provide:
1. **role_title**: Specific job title (e.g., "QA Engineer", not just "Quality Assurance")
2. **department**: Which department needs this role
3. **level**: Seniority level (junior/mid/senior/manager)
4. **gap_type**: Primary gap type (structural/skills/workload/responsibility)
5. **justification**: 2-3 sentences explaining WHY this role is needed (cite specific findings)
6. **expected_impact**: What business outcomes this role will improve
7. **priority**: Critical/High/Medium (Critical = urgent business need, High = important but not urgent, Medium = nice to have)
8. **recommended_headcount**: How many people (usually 1-2)
9. **estimated_timeline**: When to hire (Immediate, 3 months, 6 months)
10. **required_skills**: List of 3-5 key skills needed
11. **responsibilities**: List of 3-5 main responsibilities

CRITICAL: DO NOT recommend roles that were already recommended in previous analyses. Check the previous_recommendations list carefully and avoid any duplicate recommendations. Only recommend NEW roles that haven't been suggested before.

IMPORTANT: 
- Only recommend TRULY MISSING roles, not incremental headcount for existing roles
- Be specific and actionable
- Prioritize ruthlessly - focus on top 5-10 most important gaps
- Cite evidence from the analyses
- AVOID DUPLICATES: Do not recommend roles that appear in previous_recommendations

Return ONLY a valid JSON array of role objects. No other text.

Example format:
[
  {{
    "role_title": "QA Engineer",
    "department": "Engineering",
    "level": "mid",
    "gap_type": "responsibility",
    "justification": "Currently no dedicated testing role. Developers are doing their own QA, leading to quality issues and slower delivery. The org structure analysis found this is a common gap in the engineering team.",
    "expected_impact": "Improved product quality, faster release cycles, reduced production bugs by 40%",
    "priority": "critical",
    "recommended_headcount": 2,
    "estimated_timeline": "Immediate",
    "required_skills": ["Test Automation", "Selenium", "API Testing", "CI/CD", "Quality Assurance"],
    "responsibilities": ["Create test plans", "Automate testing", "Bug tracking", "Quality metrics", "Release validation"]
  }}
]
"""),
        ("user", """
ORGANIZATIONAL STRUCTURE ANALYSIS:
{org_structure}

RESPONSIBILITY COVERAGE ANALYSIS:
{responsibilities}

WORKLOAD & CAPACITY ANALYSIS:
{workload}

SKILLS GAP ANALYSIS:
{skills}

PREVIOUS RECOMMENDATIONS (DO NOT DUPLICATE THESE):
{previous_recommendations}

---

Now synthesize these into a prioritized JSON array of 5-10 missing role recommendations.
IMPORTANT: Do NOT recommend any roles that appear in the PREVIOUS RECOMMENDATIONS list above.
Only recommend NEW roles that haven't been suggested before.
Return ONLY the JSON array, no other text.
""")
    ])
    
    try:
        # Format previous recommendations for the prompt
        previous_recs = state.get("previous_recommendations", [])
        previous_recs_text = "None" if not previous_recs else json.dumps(
            [
                {
                    "role_title": rec.get("role_title", ""),
                    "department": rec.get("department", ""),
                    "level": rec.get("level", ""),
                }
                for rec in previous_recs
            ],
            indent=2
        )
        
        chain = prompt | llm
        response = chain.invoke({
            "org_structure": state.get("org_structure_analysis", "No analysis available"),
            "responsibilities": state.get("responsibility_analysis", "No analysis available"),
            "workload": state.get("workload_analysis", "No analysis available"),
            "skills": state.get("skills_analysis", "No analysis available"),
            "previous_recommendations": previous_recs_text,
        })
        
        # Parse JSON response
        content = response.content.strip()
        
        # Handle markdown code blocks
        if content.startswith("```"):
            # Extract JSON from markdown code block
            lines = content.split("\n")
            json_lines = []
            in_code_block = False
            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (not line.startswith("```")):
                    json_lines.append(line)
            content = "\n".join(json_lines).strip()
        
        recommendations = json.loads(content)
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        return {
            "recommendations": recommendations,
            "analysis_progress": state.get("analysis_progress", []) + ["synthesis_complete"]
        }
    
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing recommendations JSON: {e}")
        print(f"Response was: {response.content}")
        return {
            "recommendations": [],
            "analysis_progress": state.get("analysis_progress", []) + ["synthesis_error"],
            "error": f"Failed to parse recommendations: {str(e)}"
        }
    except Exception as e:
        print(f"❌ Error in synthesis: {e}")
        return {
            "recommendations": [],
            "analysis_progress": state.get("analysis_progress", []) + ["synthesis_error"],
            "error": str(e)
        }

