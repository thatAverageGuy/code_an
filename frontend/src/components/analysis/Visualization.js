import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as d3 from 'd3';
import Loader from '../common/Loader';

const Visualization = ({ analysisResults }) => {
  const [selectedView, setSelectedView] = useState('dependencies');
  const [loading] = useState(false);
  
  if (!analysisResults || !analysisResults.structure) {
    return <div className="no-data">No analysis data available for visualization</div>;
  }
  
  const renderDependencyGraph = () => {
    // Convert analysis results to nodes and links
    const structure = analysisResults.structure;
    const nodes = [];
    const links = [];
    const nodeMap = {};
    let nodeId = 0;
    
    // Process each file's functions and their calls
    Object.entries(structure).forEach(([filePath, fileData]) => {
      const fileName = filePath.split('/').pop();
      
      // Add file as node
      const fileNodeId = `file-${nodeId}`;
      nodes.push({
        id: fileNodeId,
        name: fileName,
        type: 'file',
        size: 15
      });
      nodeMap[fileName] = fileNodeId;
      nodeId++;
      
      // Process functions
      Object.entries(fileData.functions || {}).forEach(([funcName, funcData]) => {
        const funcNodeId = `func-${nodeId}`;
        nodes.push({
          id: funcNodeId,
          name: funcName,
          type: 'function',
          file: fileName,
          size: 10
        });
        nodeMap[`${fileName}.${funcName}`] = funcNodeId;
        nodeId++;
        
        // Link function to file
        links.push({
          source: fileNodeId,
          target: funcNodeId,
          type: 'contains'
        });
        
        // Add function calls as links
        (funcData.calls || []).forEach(calledFunc => {
          // Try to find the called function in our nodes
          Object.entries(structure).forEach(([otherFile, otherData]) => {
            const otherFileName = otherFile.split('/').pop();
            if (otherData.functions && otherData.functions[calledFunc]) {
              const targetNodeId = nodeMap[`${otherFileName}.${calledFunc}`];
              if (targetNodeId) {
                links.push({
                  source: funcNodeId,
                  target: targetNodeId,
                  type: 'calls'
                });
              }
            }
          });
        });
      });
      
      // Process classes
      Object.entries(fileData.classes || {}).forEach(([className, classData]) => {
        const classNodeId = `class-${nodeId}`;
        nodes.push({
          id: classNodeId,
          name: className,
          type: 'class',
          file: fileName,
          size: 12
        });
        nodeMap[`${fileName}.${className}`] = classNodeId;
        nodeId++;
        
        // Link class to file
        links.push({
          source: fileNodeId,
          target: classNodeId,
          type: 'contains'
        });
        
        // Add inheritance relationships
        (classData.bases || []).forEach(baseClass => {
          // Try to find the base class in our nodes
          Object.entries(structure).forEach(([otherFile, otherData]) => {
            const otherFileName = otherFile.split('/').pop();
            if (otherData.classes && otherData.classes[baseClass]) {
              const targetNodeId = nodeMap[`${otherFileName}.${baseClass}`];
              if (targetNodeId) {
                links.push({
                  source: classNodeId,
                  target: targetNodeId,
                  type: 'inherits'
                });
              }
            }
          });
        });
      });
    });
    
    return (
      <div className="dependency-graph">
        <ForceDirectedGraph nodes={nodes} links={links} />
      </div>
    );
  };
  
  const renderModuleStructure = () => {
    const structure = analysisResults.structure;
    const moduleData = [];
    
    // Count items by directory/module
    const moduleCounts = {};
    
    Object.keys(structure).forEach(filePath => {
      const parts = filePath.split('/');
      const moduleName = parts.length > 1 ? parts[parts.length - 2] : 'root';
      
      if (!moduleCounts[moduleName]) {
        moduleCounts[moduleName] = {
          name: moduleName,
          files: 0,
          functions: 0,
          classes: 0,
          imports: 0
        };
      }
      
      const fileData = structure[filePath];
      moduleCounts[moduleName].files++;
      moduleCounts[moduleName].functions += Object.keys(fileData.functions || {}).length;
      moduleCounts[moduleName].classes += Object.keys(fileData.classes || {}).length;
      moduleCounts[moduleName].imports += Object.keys(fileData.imports || {}).length;
    });
    
    // Convert to array for chart
    Object.values(moduleCounts).forEach(module => {
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
            <Bar dataKey="imports" fill="#ffc658" name="Imports" />
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
    
    // Create the simulation
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
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
      .data(links)
      .enter().append("line")
        .attr("stroke", d => {
          if (d.type === "contains") return "#999";
          if (d.type === "calls") return "#1e88e5";
          return "#e53935";
        })
        .attr("stroke-width", 1.5)
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
      .attr("r", d => d.size || 5)
      .attr("fill", d => {
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
      .style("font-size", "10px");
    
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

// eslint-disable-next-line no-unused-vars
const ModuleBarChart = ({ data, width = 600, height = 400 }) => {
    const chartRef = React.useRef(null);
    
    React.useEffect(() => {
      if (!data || data.length === 0) return;
      
      // Clear previous chart
      d3.select(chartRef.current).selectAll("*").remove();
      
      const margin = { top: 20, right: 30, bottom: 40, left: 40 };
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;
      
      // Create the SVG
      const svg = d3.select(chartRef.current)
        .attr("width", width)
        .attr("height", height);
      
      const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
      
      // Scales
      const x = d3.scaleBand()
        .domain(data.map(d => d.name))
        .range([0, innerWidth])
        .padding(0.1);
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => Math.max(d.functions, d.classes, d.imports))])
        .nice()
        .range([innerHeight, 0]);
      
      // X axis
      g.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
          .attr("transform", "rotate(-45)")
          .attr("text-anchor", "end");
      
      // Y axis
      g.append("g")
        .call(d3.axisLeft(y));
      
      // Functions bars
      g.selectAll(".bar-functions")
        .data(data)
        .enter().append("rect")
          .attr("class", "bar-functions")
          .attr("x", d => x(d.name))
          .attr("y", d => y(d.functions))
          .attr("width", x.bandwidth() / 3)
          .attr("height", d => innerHeight - y(d.functions))
          .attr("fill", "#8884d8");
      
      // Classes bars
      g.selectAll(".bar-classes")
        .data(data)
        .enter().append("rect")
          .attr("class", "bar-classes")
          .attr("x", d => x(d.name) + x.bandwidth() / 3)
          .attr("y", d => y(d.classes))
          .attr("width", x.bandwidth() / 3)
          .attr("height", d => innerHeight - y(d.classes))
          .attr("fill", "#82ca9d");
      
      // Imports bars
      g.selectAll(".bar-imports")
        .data(data)
        .enter().append("rect")
          .attr("class", "bar-imports")
          .attr("x", d => x(d.name) + 2 * x.bandwidth() / 3)
          .attr("y", d => y(d.imports))
          .attr("width", x.bandwidth() / 3)
          .attr("height", d => innerHeight - y(d.imports))
          .attr("fill", "#ffc658");
      
      // Legend
      const legend = svg.append("g")
        .attr("transform", `translate(${width - 120},20)`);
      
      const legendData = [
        { name: "Functions", color: "#8884d8" },
        { name: "Classes", color: "#82ca9d" },
        { name: "Imports", color: "#ffc658" }
      ];
      
      legendData.forEach((item, i) => {
        const legendRow = legend.append("g")
          .attr("transform", `translate(0, ${i * 20})`);
        
        legendRow.append("rect")
          .attr("width", 10)
          .attr("height", 10)
          .attr("fill", item.color);
        
        legendRow.append("text")
          .attr("x", 15)
          .attr("y", 10)
          .text(item.name)
          .style("font-size", "12px");
      });
      
    }, [data, width, height]);
    
    return <svg ref={chartRef}></svg>;
  };

export default Visualization;