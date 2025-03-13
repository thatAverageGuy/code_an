import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as d3 from 'd3';
import Loader from '../common/Loader';

const Visualization = ({ rawData }) => {
  const [selectedView, setSelectedView] = useState('dependencies');
  const [loading] = useState(false);
  
  if (!rawData || !rawData.nodes) {
    return <div className="no-data">No visualization data available</div>;
  }
  
  const renderDependencyGraph = () => {
    return (
      <div className="dependency-graph">
        <ForceDirectedGraph nodes={rawData.nodes} links={rawData.links} />
      </div>
    );
  };
  
  const renderModuleStructure = () => {
    // Process data for module structure chart
    const moduleData = [];
    
    // Group by module
    const moduleGroups = {};
    for (const node of rawData.nodes) {
      if (node.path) {
        // Extract module path
        const parts = node.path.split('/');
        const modulePath = parts.length > 1 ? parts.slice(0, -1).join('/') : 'root';
        
        if (!moduleGroups[modulePath]) {
          moduleGroups[modulePath] = {
            name: modulePath,
            files: 0,
            functions: 0,
            classes: 0
          };
        }
        
        if (node.type === 'file') {
          moduleGroups[modulePath].files++;
        } else if (node.type === 'function') {
          moduleGroups[modulePath].functions++;
        } else if (node.type === 'class') {
          moduleGroups[modulePath].classes++;
        }
      }
    }
    
    // Convert to array for chart
    Object.values(moduleGroups).forEach(module => {
      moduleData.push(module);
    });
    
    return (
      <div className="module-structure">
        <h3>Module Structure</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={moduleData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="functions" fill="#8884d8" name="Functions" />
            <Bar dataKey="classes" fill="#82ca9d" name="Classes" />
            <Bar dataKey="files" fill="#ffc658" name="Files" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };
  
  return (
    <div className="visualization-container">
      <div className="visualization-controls">
        <div className="view-selector">
          <button 
            className={`view-button ${selectedView === 'dependencies' ? 'active' : ''}`}
            onClick={() => setSelectedView('dependencies')}
          >
            Dependency Graph
          </button>
          <button 
            className={`view-button ${selectedView === 'modules' ? 'active' : ''}`}
            onClick={() => setSelectedView('modules')}
          >
            Module Structure
          </button>
        </div>
      </div>
      
      <div className="visualization-display">
        {loading ? (
          <Loader message="Generating visualization..." />
        ) : (
          <>
            {selectedView === 'dependencies' && renderDependencyGraph()}
            {selectedView === 'modules' && renderModuleStructure()}
          </>
        )}
      </div>
    </div>
  );
};

// D3 Force Directed Graph Component
const ForceDirectedGraph = ({ nodes, links }) => {
  const svgRef = React.useRef(null);
  
  React.useEffect(() => {
    if (!nodes || !links || nodes.length === 0) return;
    
    const width = 800;
    const height = 600;
    
    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();
    
    // Process links to ensure all referenced nodes exist
    const nodeMap = new Map(nodes.map(node => [node.id, node]));
    const unknownNodes = new Set();
    
    // Create nodes for unknown targets
    links.forEach(link => {
      if (typeof link.target === 'string' && link.target.startsWith('unknown:')) {
        const targetName = link.targetName || link.target.split(':')[1];
        if (!unknownNodes.has(link.target)) {
          const unknownNode = {
            id: link.target,
            name: targetName,
            type: "unknown",
            // Add a visual indicator that this is an external/unknown node
            unknown: true
          };
          nodes.push(unknownNode);
          nodeMap.set(link.target, unknownNode);
          unknownNodes.add(link.target);
        }
      }
    });
    
    // Process links to ensure proper source/target format for D3
    const processedLinks = links.map(link => {
      return {
        ...link,
        source: typeof link.source === 'number' ? link.source : link.source,
        target: typeof link.target === 'number' ? link.target : link.target
      };
    });
    
    // Create the simulation
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(processedLinks).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(30));
    
    // Create the SVG
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("height", height);
    
    // Define arrow markers
    svg.append("defs").selectAll("marker")
      .data(["contains", "calls", "inherits"])
      .enter().append("marker")
        .attr("id", d => `arrow-${d}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("fill", d => {
          if (d === "contains") return "#999";
          if (d === "calls") return "#1e88e5";
          return "#e53935";
        })
        .attr("d", "M0,-5L10,0L0,5");
    
    // Create the links
    const link = svg.append("g")
      .selectAll("line")
      .data(processedLinks)
      .enter().append("line")
        .attr("stroke", d => {
          if (d.type === "contains") return "#999";
          if (d.type === "calls") return "#1e88e5";
          return "#e53935";
        })
        .attr("stroke-width", 1.5)
        .attr("stroke-dasharray", d => {
          // Use dashed lines for links to unknown nodes
          return (typeof d.target === 'string' && d.target.startsWith('unknown:')) ? "5,5" : null;
        })
        .attr("marker-end", d => `url(#arrow-${d.type})`);
    
    // Create the nodes
    const node = svg.append("g")
      .selectAll("g")
      .data(nodes)
      .enter().append("g")
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));
    
    // Node circles
    node.append("circle")
      .attr("r", d => d.unknown ? 4 : (d.size || 5))
      .attr("fill", d => {
        if (d.unknown) return "#aaaaaa"; // Gray for unknown nodes
        if (d.type === "file") return "#4caf50";
        if (d.type === "function") return "#2196f3";
        if (d.type === "class") return "#ff9800";
        return "#9c27b0";
      });
    
    // Node labels
    node.append("text")
      .attr("dx", 12)
      .attr("dy", ".35em")
      .text(d => d.name)
      .style("font-size", "10px")
      .style("font-style", d => d.unknown ? "italic" : "normal");
    
    // Add tooltips
    node.append("title")
      .text(d => {
        if (d.unknown) return `External reference: ${d.name}`;
        return `${d.type}: ${d.name}${d.path ? `\nPath: ${d.path}` : ''}`;
      });
    
    // Update positions
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);
      
      node.attr("transform", d => `translate(${d.x},${d.y})`);
    });
    
    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
    
    // Add zoom functionality
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        svg.selectAll("g").attr("transform", event.transform);
      });
    
    svg.call(zoom);
    
    return () => {
      simulation.stop();
    };
  }, [nodes, links]);
  
  return <svg ref={svgRef} className="dependency-graph-svg"></svg>;
};

export default Visualization;