import React, { useState, useEffect, useRef } from 'react';
import { getOrgChart, getMissingRoles } from '../services/api';

export default function OrganizationChart() {
  const [orgData, setOrgData] = useState(null);
  const [missingRoles, setMissingRoles] = useState([]);
  const [showAllAnalyses, setShowAllAnalyses] = useState(true);
  const [loading, setLoading] = useState(true);
  const [selectedDept, setSelectedDept] = useState('all');
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const containerRef = useRef(null);

  useEffect(() => {
    loadOrgChart();
  }, [showAllAnalyses]);

  const loadOrgChart = async () => {
    try {
      const [orgResponse, missingRolesResponse] = await Promise.all([
        getOrgChart(),
        getMissingRoles().catch(() => ({ data: [] })) // Don't fail if no analysis
      ]);
      
      console.log('Org chart data loaded:', orgResponse.data);
      setOrgData(orgResponse.data);
      
      // Get missing roles from all analyses
      // Handle paginated response (results array) or direct array
      let allMissingRoles = [];
      if (missingRolesResponse.data) {
        if (Array.isArray(missingRolesResponse.data)) {
          allMissingRoles = missingRolesResponse.data;
        } else if (missingRolesResponse.data.results && Array.isArray(missingRolesResponse.data.results)) {
          allMissingRoles = missingRolesResponse.data.results;
        } else if (Array.isArray(missingRolesResponse.data.data)) {
          allMissingRoles = missingRolesResponse.data.data;
        }
      }
      console.log('Missing roles loaded:', allMissingRoles.length, allMissingRoles);
      
      // If showAllAnalyses is false, only show from the most recent analysis
      if (!showAllAnalyses && allMissingRoles.length > 0) {
        // Group by analysis_run
        const rolesByAnalysis = {};
        allMissingRoles.forEach(role => {
          const analysisId = role.analysis_run;
          if (!rolesByAnalysis[analysisId]) {
            rolesByAnalysis[analysisId] = [];
          }
          rolesByAnalysis[analysisId].push(role);
        });
        
        // Get the most recent analysis ID (higher ID = more recent, since auto-increment)
        const analysisIds = Object.keys(rolesByAnalysis).map(Number);
        if (analysisIds.length > 0) {
          const mostRecentAnalysisId = Math.max(...analysisIds);
          allMissingRoles = rolesByAnalysis[mostRecentAnalysisId] || [];
        }
      }
      
      setMissingRoles(allMissingRoles);
      
      // Auto-expand all root nodes
      const allRootIds = new Set();
      Object.values(orgResponse.data.hierarchy || {}).forEach(deptRoles => {
        deptRoles.forEach(role => {
          allRootIds.add(role.role_id);
          collectChildIds(role, allRootIds);
        });
      });
      setExpandedNodes(allRootIds);
    } catch (error) {
      console.error('Error loading org chart:', error);
      setOrgData(null);
      setMissingRoles([]);
    } finally {
      setLoading(false);
    }
  };

  const collectChildIds = (role, ids) => {
    if (role.children && role.children.length > 0) {
      role.children.forEach(child => {
        ids.add(child.role_id);
        collectChildIds(child, ids);
      });
    }
  };

  const toggleNode = (roleId) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(roleId)) {
        newSet.delete(roleId);
      } else {
        newSet.add(roleId);
      }
      return newSet;
    });
  };

  const getLevelColor = (level, isRecommended = false) => {
    if (isRecommended) {
      // Unique color for recommended roles - teal/cyan
      return '#14b8a6'; // teal-500
    }
    
    const colors = {
      'manager': '#2563eb',      // blue-600
      'director': '#9333ea',     // purple-600
      'vp': '#4f46e5',           // indigo-600
      'c_level': '#dc2626',      // red-600
      'lead': '#16a34a',         // green-600
      'senior': '#ca8a04',       // yellow-600
      'mid': '#f97316',          // orange-500
      'junior': '#6b7280',       // gray-500
      'entry': '#9ca3af',        // gray-400
    };
    return colors[level] || '#6b7280';
  };

  const getLevelSize = (level) => {
    const sizes = {
      'manager': 120,
      'director': 130,
      'vp': 140,
      'c_level': 150,
      'lead': 110,
      'senior': 100,
      'mid': 90,
      'junior': 80,
      'entry': 70,
    };
    return sizes[level] || 90;
  };

  const calculateNodePositions = (role, x = 0, y = 0, level = 0, positions = {}, visited = new Set()) => {
    if (!role || !role.role_id) return positions;
    
    const nodeId = role.role_id;
    if (visited.has(nodeId)) return positions;
    visited.add(nodeId);
    
    try {
      const hasChildren = role.children && Array.isArray(role.children) && role.children.length > 0 && expandedNodes.has(nodeId);
      
      positions[nodeId] = { x, y, role, hasChildren };
      
      if (hasChildren) {
        const childCount = role.children.length;
        // Calculate minimum spacing: node size + more gap to prevent overlap
        const maxChildSize = Math.max(...role.children.map(c => getLevelSize(c.level || 'mid')));
        const spacing = maxChildSize + 100; // Node size + 100px gap (increased significantly to prevent overlap)
        const startX = x - ((childCount - 1) * spacing) / 2;
        
        // Add extra vertical space for title and arrow clearance
        const titleHeight = 50; // Space for title above circle
        const arrowClearance = 150; // Space for arrows between parent and child (increased significantly to move circles down)
        
        role.children.forEach((child, index) => {
          if (child && child.role_id) {
            const childX = startX + (index * spacing);
            const childY = y + getLevelSize(role.level) / 2 + arrowClearance + getLevelSize(child.level || 'mid') / 2;
            calculateNodePositions(child, childX, childY, level + 1, positions, visited);
          }
        });
      }
    } catch (error) {
      console.error('Error calculating node positions:', error, role);
    }
    
    return positions;
  };

  const renderArrows = (role, positions, arrows = []) => {
    const nodeId = role.role_id;
    const hasChildren = role.children && role.children.length > 0 && expandedNodes.has(nodeId);
    
    if (hasChildren) {
      const parentPos = positions[nodeId];
      role.children.forEach(child => {
        const childPos = positions[child.role_id];
        if (parentPos && childPos) {
          const parentSize = getLevelSize(role.level);
          const childSize = getLevelSize(child.level || 'mid');
          const arrowGap = 25; // Space between arrow and circle edge (increased from 15)
          
          // Calculate connection points with gap from circle edges
          const fromX = parentPos.x;
          const fromY = parentPos.y + parentSize / 2 + arrowGap; // Bottom of parent + gap
          const toX = childPos.x;
          const toY = childPos.y - childSize / 2 - arrowGap; // Top of child - gap
          
          // Calculate corner point: go straight down first, then horizontal, then down to child
          // Ensure the final segment always goes DOWN by positioning horizontal segment above the child
          // Position horizontal segment just above the child's top connection point
          const horizontalY = toY - 20; // Position horizontal segment 20px above child connection point
          
          arrows.push({
            from: { x: fromX, y: fromY },
            corner1: { x: fromX, y: horizontalY }, // First corner: straight down
            corner2: { x: toX, y: horizontalY }, // Second corner: horizontal move
            to: { x: toX, y: toY } // Final segment: down to child (always downward)
          });
        }
        renderArrows(child, positions, arrows);
      });
    }
    
    return arrows;
  };

  const mergeMissingRolesIntoHierarchy = (roles, dept) => {
    // Ensure missingRoles is an array
    if (!Array.isArray(missingRoles) || missingRoles.length === 0) {
      return roles;
    }
    
    // Get missing roles for this department
    const deptMissingRoles = missingRoles.filter(mr => mr && mr.department === dept);
    
    if (deptMissingRoles.length === 0) return roles;
    
    // Convert missing roles to role format
    const missingRolesAsNodes = deptMissingRoles.map((mr, idx) => ({
      role_id: `RECOMMENDED_${mr.id || idx}`,
      role_title: mr.recommended_role_title,
      department: mr.department,
      level: mr.level || 'mid',
      current_headcount: mr.recommended_headcount || 0,
      team_size: 0,
      reports_to: null, // We'll try to find a parent based on level
      children: [],
      isRecommended: true,
      priority: mr.priority,
      gap_type: mr.gap_type,
      analysis_run_id: mr.analysis_run_id || mr.analysis_run,
      analysis_run_date: mr.analysis_run_date,
    }));
    
    // Try to attach recommended roles to appropriate parents based on level
    missingRolesAsNodes.forEach(missingRole => {
      // Find a suitable parent (manager or lead in same department)
      const potentialParent = roles.find(r => 
        (r.level === 'manager' || r.level === 'lead' || r.level === 'director') &&
        r.department === dept
      );
      
      if (potentialParent) {
        if (!potentialParent.children) {
          potentialParent.children = [];
        }
        potentialParent.children.push(missingRole);
      } else {
        // Add as root if no suitable parent
        roles.push(missingRole);
      }
    });
    
    return roles;
  };

  const renderOrgChart = (roles, dept) => {
    if (!roles || roles.length === 0) {
      return (
        <div className="text-center py-8 text-gray-600">
          No roles found for this department.
        </div>
      );
    }

    try {
      console.log(`Rendering org chart for ${dept} with ${roles.length} roles`);
      
      // Merge missing roles into hierarchy
      const rolesWithMissing = mergeMissingRolesIntoHierarchy([...roles], dept);
      console.log(`After merging missing roles: ${rolesWithMissing.length} total roles`);

      // Calculate all node positions
      const positions = {};
      // Calculate minimum spacing between root nodes to prevent overlap
      const maxRootSize = Math.max(...rolesWithMissing.map(r => getLevelSize(r.level || 'mid')));
      const baseSpacing = maxRootSize + 120; // Node size + 120px gap (increased significantly to prevent overlap)
      const startX = 0;
      const topMargin = 150; // Extra space at top for titles (increased to accommodate higher labels)
      
      rolesWithMissing.forEach((role, index) => {
        const xOffset = index * baseSpacing;
        calculateNodePositions(role, startX + xOffset, topMargin, 0, positions);
      });

      // Calculate arrows
      const arrows = [];
      rolesWithMissing.forEach(role => {
        renderArrows(role, positions, arrows);
      });

      // Find bounds for SVG
      const allPositions = Object.values(positions);
      if (allPositions.length === 0) {
        return (
          <div className="text-center py-8 text-gray-600">
            No organizational structure data available.
          </div>
        );
      }

      const minX = Math.min(...allPositions.map(p => p.x)) - 100;
      const maxX = Math.max(...allPositions.map(p => p.x)) + 100;
      const minY = Math.min(...allPositions.map(p => p.y)) - 100;
      const maxY = Math.max(...allPositions.map(p => p.y)) + 100;
      const width = Math.max(maxX - minX, 800);
      const height = Math.max(maxY - minY, 600);

      return (
      <div className="overflow-auto" style={{ maxHeight: '800px' }}>
        <svg
          width={width || 800}
          height={height || 600}
          className="border border-gray-200 rounded-lg bg-white"
          style={{ minWidth: '100%' }}
        >
          {/* Render arrows with right-angle corners */}
          {arrows.map((arrow, index) => {
            const fromX = arrow.from.x - minX;
            const fromY = arrow.from.y - minY;
            const corner1X = arrow.corner1.x - minX;
            const corner1Y = arrow.corner1.y - minY;
            const corner2X = arrow.corner2.x - minX;
            const corner2Y = arrow.corner2.y - minY;
            const toX = arrow.to.x - minX;
            const toY = arrow.to.y - minY;
            
            // Create path with right-angle corners: 
            // 1. Down from parent bottom
            // 2. Horizontal to child x position
            // 3. Down to child top
            const pathData = `M ${fromX} ${fromY} L ${corner1X} ${corner1Y} L ${corner2X} ${corner2Y} L ${toX} ${toY}`;
            
            return (
              <g key={`arrow-${index}`}>
                <path
                  d={pathData}
                  fill="none"
                  stroke="#94a3b8"
                  strokeWidth="2"
                  markerEnd="url(#arrowhead)"
                />
              </g>
            );
          })}
          
          {/* Arrow marker definition - pointing downward */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="5"
              refY="9"
              orient="auto"
            >
              <polygon points="0 0, 10 0, 5 10" fill="#94a3b8" />
            </marker>
          </defs>

          {/* Render nodes */}
          {Object.entries(positions).map(([nodeId, pos]) => {
            const role = pos.role;
            const isRecommended = role.isRecommended || false;
            const size = getLevelSize(role.level);
            const color = getLevelColor(role.level, isRecommended);
            const x = pos.x - minX;
            const y = pos.y - minY;
            const hasChildren = role.children && role.children.length > 0;
            const isExpanded = expandedNodes.has(nodeId);

            return (
              <g key={nodeId}>
                {/* Outer ring for recommended roles */}
                {isRecommended && (
                  <circle
                    cx={x}
                    cy={y}
                    r={size / 2 + 8}
                    fill="none"
                    stroke="#14b8a6"
                    strokeWidth="3"
                    strokeDasharray="5,5"
                    opacity="0.8"
                  />
                )}
                
                {/* Circle */}
                <circle
                  cx={x}
                  cy={y}
                  r={size / 2}
                  fill={color}
                  stroke="white"
                  strokeWidth={isRecommended ? "4" : "3"}
                  className="cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => hasChildren && toggleNode(nodeId)}
                />
                
                {/* Recommended badge */}
                {isRecommended && (
                  <circle
                    cx={x + size / 2 - 8}
                    cy={y - size / 2 + 8}
                    r="10"
                    fill="#14b8a6"
                    stroke="white"
                    strokeWidth="2"
                  />
                )}
                {isRecommended && (
                  <text
                    x={x + size / 2 - 8}
                    y={y - size / 2 + 12}
                    textAnchor="middle"
                    className="text-xs font-bold fill-white"
                    style={{ fontSize: '10px' }}
                  >
                    ★
                  </text>
                )}
                
                {/* Expand/Collapse indicator */}
                {hasChildren && (
                  <circle
                    cx={x}
                    cy={y + size / 2 + 15}
                    r="12"
                    fill="white"
                    stroke={color}
                    strokeWidth="2"
                    className="cursor-pointer hover:bg-gray-100"
                    onClick={() => toggleNode(nodeId)}
                  />
                )}
                {hasChildren && (
                  <text
                    x={x}
                    y={y + size / 2 + 19}
                    textAnchor="middle"
                    className="text-xs font-bold cursor-pointer select-none"
                    fill={color}
                    onClick={() => toggleNode(nodeId)}
                  >
                    {isExpanded ? '−' : '+'}
                  </text>
                )}

                {/* Role title - moved higher to avoid arrow overlap */}
                <text
                  x={x}
                  y={y - size / 2 - 50}
                  textAnchor="middle"
                  className="text-xs font-semibold"
                  fill={isRecommended ? "#14b8a6" : "#111827"}
                  style={{ fontSize: '11px', fontWeight: isRecommended ? 'bold' : '600' }}
                >
                  {role.role_title}
                </text>

                {/* Recommended label - moved higher to avoid arrow overlap */}
                {isRecommended && (
                  <text
                    x={x}
                    y={y - size / 2 - 70}
                    textAnchor="middle"
                    className="text-xs font-bold"
                    fill="#14b8a6"
                    style={{ fontSize: '9px' }}
                  >
                    RECOMMENDED
                  </text>
                )}

                {/* Department - with more margin from circle */}
                <text
                  x={x}
                  y={y + size / 2 + 40}
                  textAnchor="middle"
                  className="text-xs fill-gray-600"
                  style={{ fontSize: '10px' }}
                >
                  {role.department}
                </text>

                {/* Headcount or Priority - with more margin */}
                <text
                  x={x}
                  y={y + size / 2 + 58}
                  textAnchor="middle"
                  className="text-xs font-medium"
                  fill={isRecommended ? "#14b8a6" : "#6b7280"}
                  style={{ fontSize: '9px' }}
                >
                  {isRecommended 
                    ? `${role.priority?.toUpperCase() || 'MEDIUM'} Priority`
                    : `${role.current_headcount} ${role.current_headcount === 1 ? 'person' : 'people'}`}
                </text>

                {/* Analysis information for recommended roles */}
                {isRecommended && role.analysis_run_id && (
                  <g>
                    <text
                      x={x}
                      y={y + size / 2 + 75}
                      textAnchor="middle"
                      className="text-xs fill-gray-500"
                      style={{ fontSize: '8px' }}
                    >
                      Analysis #{role.analysis_run_id}
                    </text>
                    {role.analysis_run_date && (
                      <text
                        x={x}
                        y={y + size / 2 + 88}
                        textAnchor="middle"
                        className="text-xs fill-gray-500"
                        style={{ fontSize: '8px' }}
                      >
                        {new Date(role.analysis_run_date).toLocaleDateString('en-US', { 
                          month: 'short', 
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </text>
                    )}
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    );
    } catch (error) {
      console.error('Error rendering org chart:', error);
      return (
        <div className="text-center py-8 text-red-600">
          Error rendering organization chart: {error.message}
        </div>
      );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!orgData || !orgData.hierarchy) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Organization Chart</h1>
          <p className="text-gray-600 mt-2">Visualize the hierarchical structure with interactive nodes</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-12">
            <p className="text-gray-600">No organizational data available.</p>
            <p className="text-sm text-gray-500 mt-2">Please ensure you have generated sample data first.</p>
          </div>
        </div>
      </div>
    );
  }

  const departments = orgData.departments || [];
  const hierarchy = orgData.hierarchy || {};
  const filteredDepts = selectedDept === 'all' ? departments : [selectedDept];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Organization Chart</h1>
        <p className="text-gray-600 mt-2">Visualize the hierarchical structure with interactive nodes</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Department
            </label>
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Departments</option>
              {departments.map((dept) => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recommendations
            </label>
            <div className="flex items-center space-x-3">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="analysisMode"
                  checked={showAllAnalyses}
                  onChange={() => setShowAllAnalyses(true)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">All Analyses</span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="analysisMode"
                  checked={!showAllAnalyses}
                  onChange={() => setShowAllAnalyses(false)}
                  className="mr-2"
                />
                <span className="text-sm text-gray-700">Latest Only</span>
              </label>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {showAllAnalyses 
                ? 'Showing recommendations from all completed analyses'
                : 'Showing only the most recent analysis recommendations'}
            </p>
          </div>
        </div>
      </div>

      {/* Organization Chart */}
      <div className="bg-gray-50 rounded-lg p-6" ref={containerRef}>
        {filteredDepts.length === 0 ? (
          <p className="text-gray-600 text-center py-8">No departments found.</p>
        ) : (
          filteredDepts.map((dept) => {
            const deptRoles = hierarchy[dept] || [];
            if (deptRoles.length === 0) {
              return (
                <div key={dept} className="mb-8 last:mb-0">
                  <div className="mb-4">
                    <h2 className="text-2xl font-bold text-gray-900">{dept}</h2>
                  </div>
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <p className="text-gray-600 text-center py-4">No roles found in this department.</p>
                  </div>
                </div>
              );
            }

            return (
              <div key={dept} className="mb-8 last:mb-0">
                <div className="mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">{dept}</h2>
                  <p className="text-sm text-gray-600">{deptRoles.length} role{deptRoles.length !== 1 ? 's' : ''}</p>
                </div>
                <div className="bg-white rounded-lg p-4 shadow-sm">
                  {renderOrgChart(deptRoles, dept)}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">How to use:</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Click on a circle to expand/collapse its children</li>
          <li>Arrows show reporting relationships (parent → child)</li>
          <li>Circle size and color indicate role level</li>
          <li><strong className="text-teal-600">Teal circles with dashed border</strong> are AI-recommended missing roles</li>
          <li>Hover over nodes for better visibility</li>
        </ul>
      </div>
      
      {/* Missing Roles Summary */}
      {missingRoles.length > 0 && (
        <div className="space-y-4">
          <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-teal-900 mb-2">
              AI Recommendations ({missingRoles.length} missing role{missingRoles.length !== 1 ? 's' : ''} identified)
              {showAllAnalyses && (
                <span className="ml-2 text-xs font-normal text-teal-700">
                  (from all analyses)
                </span>
              )}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-teal-800">
              <div>
                <span className="font-semibold">Critical: </span>
                {missingRoles.filter(mr => mr.priority === 'critical').length}
              </div>
              <div>
                <span className="font-semibold">High: </span>
                {missingRoles.filter(mr => mr.priority === 'high').length}
              </div>
              <div>
                <span className="font-semibold">Medium: </span>
                {missingRoles.filter(mr => mr.priority === 'medium').length}
              </div>
            </div>
            {showAllAnalyses && (
              <p className="text-xs text-teal-700 mt-2">
                💡 Tip: Toggle to "Latest Only" to see only the most recent analysis recommendations
              </p>
            )}
          </div>

          {/* Group by Analysis */}
          {showAllAnalyses && (() => {
            const rolesByAnalysis = {};
            missingRoles.forEach(role => {
              const analysisId = role.analysis_run_id || role.analysis_run;
              if (!analysisId) return;
              if (!rolesByAnalysis[analysisId]) {
                rolesByAnalysis[analysisId] = {
                  id: analysisId,
                  date: role.analysis_run_date,
                  roles: []
                };
              }
              rolesByAnalysis[analysisId].roles.push(role);
            });

            const analyses = Object.values(rolesByAnalysis).sort((a, b) => {
              if (a.date && b.date) {
                return new Date(b.date) - new Date(a.date);
              }
              return b.id - a.id;
            });

            if (analyses.length > 0) {
              return (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">
                    Recommendations by Analysis
                  </h3>
                  <div className="space-y-3">
                    {analyses.map(analysis => (
                      <div key={analysis.id} className="border-l-4 border-teal-500 pl-3 py-2 bg-gray-50 rounded">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-semibold text-gray-900">
                            Analysis #{analysis.id}
                          </span>
                          <span className="text-xs text-gray-600">
                            {analysis.roles.length} role{analysis.roles.length !== 1 ? 's' : ''}
                          </span>
                        </div>
                        {analysis.date && (
                          <p className="text-xs text-gray-600 mb-2">
                            {new Date(analysis.date).toLocaleDateString('en-US', { 
                              weekday: 'short',
                              month: 'short', 
                              day: 'numeric',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        )}
                        <div className="flex flex-wrap gap-1 mt-2">
                          {analysis.roles.map(role => (
                            <span
                              key={role.id}
                              className="inline-block px-2 py-1 text-xs rounded-full bg-teal-100 text-teal-800 border border-teal-300"
                              title={`${role.recommended_role_title} - ${role.priority} priority`}
                            >
                              {role.recommended_role_title.length > 25 
                                ? role.recommended_role_title.substring(0, 25) + '...'
                                : role.recommended_role_title}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            }
            return null;
          })()}
        </div>
      )}

      {/* Legend */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Level Legend</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {['manager', 'director', 'lead', 'senior', 'mid', 'junior'].map(level => (
            <div key={level} className="flex items-center">
              <div 
                className="w-6 h-6 rounded-full mr-2 border-2 border-white shadow-sm"
                style={{ backgroundColor: getLevelColor(level) }}
              ></div>
              <span className="text-sm text-gray-700 capitalize">{level}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
