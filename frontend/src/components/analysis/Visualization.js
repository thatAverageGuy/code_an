import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Loader from '../common/Loader';

const Visualization = ({ rawData }) => {
  const [selectedView, setSelectedView] = useState('flow');
  const [loading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [highlightedNodes, setHighlightedNodes] = useState(new Set());
  const [highlightedLinks, setHighlightedLinks] = useState(new Set());
  const [focusMode, setFocusMode] = useState(false);
  
  if (!rawData || !rawData.nodes) {
    return <div className="no-data">No visualization data available</div>;
  }
  
  const handleViewChange = (view) => {
    setSelectedView(view);
    setSelectedNode(null);
    setHighlightedNodes(new Set());
    setHighlightedLinks(new Set());
  };
  
  const renderNodeDetails = () => {
    if (!selectedNode) return null;
    
    const node = rawData.nodes.find(n => n.id === selectedNode);
    if (!node) return null;
    
    return (
      <div className="node-details">
        <h3>{node.name}</h3>
        <p><strong>Type:</strong> {node.type}</p>
        <p><strong>Path:</strong> {node.path}</p>
        
        {node.type === 'function' && (
          <div>
            <p><strong>Arguments:</strong> {node.args && node.args.join(', ')}</p>
            <p><strong>From:</strong> {node.path}</p>
          </div>
        )}
        
        {node.type === 'class' && (
          <div>
            <p><strong>Base Classes:</strong> {node.bases && node.bases.join(', ') || 'None'}</p>
            <p><strong>Methods:</strong> {node.methods && node.methods.join(', ') || 'None'}</p>
          </div>
        )}
        
        {node.summary && (
          <div>
            <h4>Summary:</h4>
            <p>{node.summary}</p>
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="visualization-container">
      <div className="visualization-controls">
        <div className="view-selector">
          <button 
            className={`view-button ${selectedView === 'flow' ? 'active' : ''}`}
            onClick={() => handleViewChange('flow')}
          >
            Flow Diagram
          </button>
          <button 
            className={`view-button ${selectedView === 'module' ? 'active' : ''}`}
            onClick={() => handleViewChange('module')}
          >
            Module Structure
          </button>
          <button 
            className={`view-button ${selectedView === 'hierarchy' ? 'active' : ''}`}
            onClick={() => handleViewChange('hierarchy')}
          >
            Class Hierarchy
          </button>
        </div>
        
        <div className="filter-controls">
          <label className="toggle-switch">
            <input 
              type="checkbox" 
              checked={focusMode} 
              onChange={() => setFocusMode(!focusMode)} 
            />
            <span className="slider"></span>
            Focus Mode
          </label>
        </div>
      </div>
      
      <div className="visualization-display">
        {loading ? (
          <Loader message="Generating visualization..." />
        ) : (
          <div className="vis-flex-container">
            <div className="vis-diagram-container">
              {selectedView === 'flow' && (
                <FlowDiagram 
                  nodes={rawData.nodes} 
                  links={rawData.links}
                  onNodeSelect={setSelectedNode}
                  selectedNode={selectedNode}
                  highlightedNodes={highlightedNodes}
                  highlightedLinks={highlightedLinks}
                  setHighlightedNodes={setHighlightedNodes}
                  setHighlightedLinks={setHighlightedLinks}
                  focusMode={focusMode}
                />
              )}
              {selectedView === 'module' && (
                <ModuleStructure 
                  nodes={rawData.nodes} 
                  links={rawData.links}
                  modules={rawData.modules}
                  onNodeSelect={setSelectedNode}
                />
              )}
              {selectedView === 'hierarchy' && (
                <ClassHierarchy 
                  nodes={rawData.nodes} 
                  links={rawData.links}
                  onNodeSelect={setSelectedNode}
                />
              )}
            </div>
            
            <div className="vis-details-panel">
              {renderNodeDetails()}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Flow Diagram Component with Force-Directed Layout
const FlowDiagram = ({ 
  nodes, 
  links, 
  onNodeSelect, 
  selectedNode,
  highlightedNodes,
  highlightedLinks,
  setHighlightedNodes,
  setHighlightedLinks,
  focusMode
}) => {
  const svgRef = useRef(null);
  const [zoomTransform, setZoomTransform] = useState(d3.zoomIdentity);
  
  useEffect(() => {
    if (!nodes || !links || nodes.length === 0) return;
    
    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();
    
    const width = 800;
    const height = 600;
    
    // Prepare nodes and links data with proper types
    const nodesData = [...nodes];
    
    // Process links, ensuring proper source/target format
    const processedLinks = links.map(link => {
      // Handle links to unknown targets
      if (typeof link.target === 'string' && link.target.startsWith('unknown:')) {
        // Create a placeholder node for the unknown target
        const targetName = link.targetName || link.target.split(':')[1];
        const unknownNodeId = `unknown-${targetName}`;
        
        // Check if we already added this unknown node
        const existingNode = nodesData.find(n => n.id === unknownNodeId);
        if (!existingNode) {
          nodesData.push({
            id: unknownNodeId,
            name: targetName,
            type: 'external',
            path: 'external',
            external: true
          });
        }
        
        return {
          ...link,
          source: typeof link.source === 'object' ? link.source.id : link.source,
          target: unknownNodeId
        };
      }
      
      return {
        ...link,
        source: typeof link.source === 'object' ? link.source.id : link.source,
        target: typeof link.target === 'object' ? link.target.id : link.target
      };
    });
    
    // Create a layout engine - using D3 force directed layout with constraints
    const simulation = d3.forceSimulation(nodesData)
      .force("link", d3.forceLink(processedLinks).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(0.05))
      .force("y", d3.forceY(height / 2).strength(0.05))
      .force("collision", d3.forceCollide().radius(d => getNodeRadius(d) + 10));
    
    // Create the SVG
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("height", height);
    
    // Create a group for the graph
    const graph = svg.append("g");
    
    // Define arrow markers for different link types
    svg.append("defs").selectAll("marker")
      .data(["contains", "calls", "inherits", "imports"])
      .enter().append("marker")
        .attr("id", d => `arrow-${d}`)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", 0)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
      .append("path")
        .attr("fill", d => getLinkColor(d))
        .attr("d", "M0,-5L10,0L0,5");
    
    // Create the links
    const link = graph.append("g")
      .selectAll("line")
      .data(processedLinks)
      .enter().append("line")
        .attr("stroke", d => getLinkColor(d.type))
        .attr("stroke-width", d => isLinkHighlighted(d) ? 3 : 1.5)
        .attr("stroke-dasharray", d => {
          return d.target.startsWith && d.target.startsWith('unknown-') ? "5,5" : null;
        })
        .attr("marker-end", d => `url(#arrow-${d.type})`)
        .attr("class", "link")
        .attr("data-source", d => d.source)
        .attr("data-target", d => d.target)
        .attr("data-type", d => d.type);
    
    // Create the nodes
    const node = graph.append("g")
      .selectAll("g")
      .data(nodesData)
      .enter().append("g")
        .attr("class", "node")
        .attr("data-id", d => d.id)
        .attr("data-type", d => d.type)
        .attr("data-name", d => d.name)
        .on("click", (event, d) => {
          onNodeSelect(d.id);
          event.stopPropagation();
          
          // Update highlighted connections
          highlightConnections(d);
        })
        .on("mouseover", (event, d) => {
          if (!focusMode) highlightConnections(d, true);
        })
        .on("mouseout", (event, d) => {
          if (!focusMode) resetHighlights();
        })
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended));
    
    // Node shapes based on type
    node.each(function(d) {
      const g = d3.select(this);
      const radius = getNodeRadius(d);
      
      if (d.type === 'file') {
        g.append("rect")
          .attr("width", radius * 2)
          .attr("height", radius * 2)
          .attr("x", -radius)
          .attr("y", -radius)
          .attr("rx", 4)
          .attr("fill", getNodeColor(d))
          .attr("stroke", d.id === selectedNode ? "#ff0000" : "#ffffff")
          .attr("stroke-width", d.id === selectedNode ? 3 : isNodeHighlighted(d) ? 2 : 1)
          .attr("opacity", getNodeOpacity(d));
      } else if (d.type === 'class') {
        g.append("polygon")
          .attr("points", getHexagonPoints(radius))
          .attr("fill", getNodeColor(d))
          .attr("stroke", d.id === selectedNode ? "#ff0000" : "#ffffff")
          .attr("stroke-width", d.id === selectedNode ? 3 : isNodeHighlighted(d) ? 2 : 1)
          .attr("opacity", getNodeOpacity(d));
      } else if (d.type === 'function') {
        g.append("circle")
          .attr("r", radius)
          .attr("fill", getNodeColor(d))
          .attr("stroke", d.id === selectedNode ? "#ff0000" : "#ffffff")
          .attr("stroke-width", d.id === selectedNode ? 3 : isNodeHighlighted(d) ? 2 : 1)
          .attr("opacity", getNodeOpacity(d));
      } else if (d.type === 'module') {
        g.append("rect")
          .attr("width", radius * 2)
          .attr("height", radius * 1.5)
          .attr("x", -radius)
          .attr("y", -radius * 0.75)
          .attr("fill", getNodeColor(d))
          .attr("stroke", d.id === selectedNode ? "#ff0000" : "#ffffff")
          .attr("stroke-width", d.id === selectedNode ? 3 : isNodeHighlighted(d) ? 2 : 1)
          .attr("opacity", getNodeOpacity(d));
      } else {
        // Default shape (diamond for external nodes)
        g.append("polygon")
          .attr("points", getDiamondPoints(radius))
          .attr("fill", getNodeColor(d))
          .attr("stroke", d.id === selectedNode ? "#ff0000" : "#ffffff")
          .attr("stroke-width", d.id === selectedNode ? 3 : isNodeHighlighted(d) ? 2 : 1)
          .attr("opacity", getNodeOpacity(d));
      }
    });
    
    // Node labels
    node.append("text")
      .attr("dy", 4)
      .attr("text-anchor", "middle")
      .text(d => d.name)
      .style("font-size", "10px")
      .style("font-weight", d => d.id === selectedNode ? "bold" : "normal")
      .style("fill", "#000")
      .each(function(d) {
        // Adjust text position based on node type
        if (d.type === 'file' || d.type === 'module') {
          d3.select(this).attr("dy", getNodeRadius(d) + 15);
        }
      });
    
    // Add node type icons or indicators
    node.each(function(d) {
      const g = d3.select(this);
      
      if (d.type === 'file') {
        g.append("text")
          .attr("y", 5)
          .attr("text-anchor", "middle")
          .text("📄")
          .style("font-size", "14px");
      } else if (d.type === 'class') {
        g.append("text")
          .attr("y", 5)
          .attr("text-anchor", "middle")
          .text("C")
          .style("font-size", "12px")
          .style("font-weight", "bold")
          .style("fill", "#fff");
      } else if (d.type === 'function') {
        g.append("text")
          .attr("y", 5)
          .attr("text-anchor", "middle")
          .text("ƒ")
          .style("font-size", "14px")
          .style("font-weight", "bold")
          .style("fill", "#fff");
      } else if (d.type === 'module') {
        g.append("text")
          .attr("y", 5)
          .attr("text-anchor", "middle")
          .text("📁")
          .style("font-size", "14px");
      }
    });
    
    // Update positions on simulation tick
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
        graph.attr("transform", event.transform);
        setZoomTransform(event.transform);
      });
    
    svg.call(zoom);
    
    // Background click to deselect
    svg.on("click", () => {
      onNodeSelect(null);
      resetHighlights();
    });
    
    // Function to get node radius based on type
    function getNodeRadius(d) {
      if (d.type === 'file') return 15;
      if (d.type === 'module') return 20;
      if (d.type === 'class') return 18;
      if (d.type === 'function') return 12;
      return 10;
    }
    
    // Function to get node color based on type
    function getNodeColor(d) {
      if (d.type === 'file') return '#4caf50';
      if (d.type === 'module') return '#ff9800';
      if (d.type === 'class') return '#2196f3';
      if (d.type === 'function') return '#9c27b0';
      if (d.type === 'external') return '#aaaaaa';
      return '#607d8b';
    }
    
    // Function to get link color based on type
    function getLinkColor(type) {
      if (type === 'contains') return '#a0a0a0';
      if (type === 'calls') return '#9c27b0';
      if (type === 'inherits') return '#2196f3';
      if (type === 'imports') return '#ff9800';
      return '#cccccc';
    }
    
    // Function to determine if a node is highlighted
    function isNodeHighlighted(d) {
      return highlightedNodes.has(d.id);
    }
    
    // Function to determine if a link is highlighted
    function isLinkHighlighted(d) {
      const linkId = `${d.source}-${d.target}`;
      return highlightedLinks.has(linkId);
    }
    
    // Function to get node opacity based on highlights
    function getNodeOpacity(d) {
      if (focusMode && !isNodeHighlighted(d) && highlightedNodes.size > 0 && d.id !== selectedNode) {
        return 0.2;
      }
      return 1;
    }
    
    // Function to highlight connections
    function highlightConnections(d, isHover = false) {
      const connectedNodes = new Set([d.id]);
      const connectedLinks = new Set();
      
      // Find all directly connected nodes
      processedLinks.forEach(link => {
        if (link.source === d.id) {
          connectedNodes.add(link.target);
          connectedLinks.add(`${link.source}-${link.target}`);
        }
        if (link.target === d.id) {
          connectedNodes.add(link.source);
          connectedLinks.add(`${link.source}-${link.target}`);
        }
      });
      
      if (!isHover) {
        setHighlightedNodes(connectedNodes);
        setHighlightedLinks(connectedLinks);
      }
      
      // Update visual highlights immediately for hover effects
      node.selectAll("circle, rect, polygon")
        .attr("opacity", (d) => {
          if (focusMode || isHover) {
            return connectedNodes.has(d.id) ? 1 : 0.2;
          }
          return 1;
        })
        .attr("stroke-width", (d) => {
          return connectedNodes.has(d.id) && d.id !== selectedNode ? 2 : d.id === selectedNode ? 3 : 1;
        });
      
      link
        .attr("stroke-width", (d) => {
          const linkId = `${d.source.id || d.source}-${d.target.id || d.target}`;
          return connectedLinks.has(linkId) ? 3 : 1.5;
        })
        .attr("opacity", (d) => {
          const linkId = `${d.source.id || d.source}-${d.target.id || d.target}`;
          if (focusMode || isHover) {
            return connectedLinks.has(linkId) ? 1 : 0.1;
          }
          return 1;
        });
    }
    
    // Function to reset highlights
    function resetHighlights() {
      if (!focusMode) {
        node.selectAll("circle, rect, polygon")
          .attr("opacity", 1)
          .attr("stroke-width", (d) => d.id === selectedNode ? 3 : 1);
        
        link
          .attr("stroke-width", 1.5)
          .attr("opacity", 1);
      }
    }
    
    // Helper functions for node shapes
    function getHexagonPoints(radius) {
      const points = [];
      for (let i = 0; i < 6; i++) {
        const angle = (i * Math.PI / 3) - (Math.PI / 6);
        points.push(`${radius * Math.cos(angle)},${radius * Math.sin(angle)}`);
      }
      return points.join(' ');
    }
    
    function getDiamondPoints(radius) {
      return `0,${-radius} ${radius},0 0,${radius} ${-radius},0`;
    }
    
    // Run the simulation for a bit to get a good initial layout
    for (let i = 0; i < 100; ++i) simulation.tick();
    
    return () => {
      simulation.stop();
    };
  }, [nodes, links, selectedNode, focusMode]);
  
  // Update highlights when selected node changes
  useEffect(() => {
    if (!selectedNode || !svgRef.current) return;

    const nodeElement = d3.select(svgRef.current).select(`[data-id="${selectedNode}"]`);
    if (!nodeElement.empty()) {
      const nodeData = nodeElement.datum();
      if (nodeData) {
        // Find all directly connected nodes and links
        const connectedNodes = new Set([nodeData.id]);
        const connectedLinks = new Set();
        
        // Process links to find connections
        const svgLinks = d3.select(svgRef.current).selectAll("line");
        svgLinks.each(function() {
          const link = d3.select(this);
          const source = link.attr("data-source");
          const target = link.attr("data-target");
          
          if (source === nodeData.id || target === nodeData.id) {
            if (source === nodeData.id) connectedNodes.add(target);
            if (target === nodeData.id) connectedNodes.add(source);
            connectedLinks.add(`${source}-${target}`);
          }
        });
        
        // Update state
        setHighlightedNodes(connectedNodes);
        setHighlightedLinks(connectedLinks);
        
        // Update visual styles
        const svgNodes = d3.select(svgRef.current).selectAll(".node");
        svgNodes.selectAll("circle, rect, polygon")
          .attr("opacity", (d) => {
            if (focusMode) {
              return connectedNodes.has(d.id) ? 1 : 0.2;
            }
            return 1;
          })
          .attr("stroke-width", (d) => {
            return connectedNodes.has(d.id) && d.id !== selectedNode ? 2 : d.id === selectedNode ? 3 : 1;
          });
        
        // Update links
        svgLinks
          .attr("stroke-width", function() {
            const link = d3.select(this);
            const linkId = `${link.attr("data-source")}-${link.attr("data-target")}`;
            return connectedLinks.has(linkId) ? 3 : 1.5;
          })
          .attr("opacity", function() {
            if (focusMode) {
              const link = d3.select(this);
              const linkId = `${link.attr("data-source")}-${link.attr("data-target")}`;
              return connectedLinks.has(linkId) ? 1 : 0.1;
            }
            return 1;
          });
      }
    }
  }, [selectedNode, focusMode, setHighlightedNodes, setHighlightedLinks]);
  
  return <svg ref={svgRef} className="flow-diagram-svg"></svg>;
};

// Module Structure Component using Tree Layout
const ModuleStructure = ({ nodes, links, modules, onNodeSelect }) => {
  const svgRef = useRef(null);
  
  useEffect(() => {
    if (!nodes || !modules || nodes.length === 0) return;
    
    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();
    
    const width = 800;
    const height = 600;
    
    // Create the SVG
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("height", height);
    
    // Create hierarchical structure
    const moduleNodes = {};
    const moduleParents = {};
    
    // Create module nodes
    modules.forEach(modulePath => {
      const parts = modulePath.split('/');
      let currentPath = '';
      
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        const parentPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        
        if (!moduleNodes[currentPath]) {
          moduleNodes[currentPath] = {
            id: currentPath,
            name: part,
            path: currentPath,
            type: 'module',
            children: []
          };
        }
        
        if (parentPath && moduleNodes[parentPath]) {
          moduleParents[currentPath] = parentPath;
          moduleNodes[parentPath].children.push(moduleNodes[currentPath]);
        }
      }
    });
    
    // Add file nodes to their modules
    nodes.filter(n => n.type === 'file').forEach(fileNode => {
      const filePath = fileNode.path;
      const lastSlashIndex = filePath.lastIndexOf('/');
      const moduleDir = lastSlashIndex > 0 ? filePath.substring(0, lastSlashIndex) : '';
      
      if (moduleDir && moduleNodes[moduleDir]) {
        moduleNodes[moduleDir].children.push({
          ...fileNode,
          children: []
        });
      } else if (!moduleDir) {
        // Root level files
        if (!moduleNodes['root']) {
          moduleNodes['root'] = {
            id: 'root',
            name: 'Project Root',
            path: '',
            type: 'module',
            children: []
          };
        }
        moduleNodes['root'].children.push({
          ...fileNode,
          children: []
        });
      }
    });
    
    // Find the root modules (those without parents)
    const rootModules = Object.values(moduleNodes).filter(
      module => !moduleParents[module.id]
    );
    
    // Create a single root if there are multiple root modules
    const hierarchyRoot = rootModules.length === 1 
      ? rootModules[0] 
      : { id: 'root', name: 'Project Root', children: rootModules, type: 'module' };
    
    // Generate the tree layout
    const tree = d3.tree().size([width - 100, height - 100]);
    const root = d3.hierarchy(hierarchyRoot);
    
    tree(root);
    
    // Create container for the tree
    const g = svg.append("g")
      .attr("transform", `translate(50, 50)`);
    
    // Add links between nodes
    g.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d3.linkHorizontal()
        .x(d => d.y) // Swap x and y to make tree horizontal
        .y(d => d.x)
      )
      .attr('fill', 'none')
      .attr('stroke', '#999')
      .attr('stroke-width', 1.5);
    
    // Add nodes
    const node = g.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.y}, ${d.x})`) // Swap x and y
      .on('click', (event, d) => {
        onNodeSelect(d.data.id);
        event.stopPropagation();
      });
    
    // Node symbols based on type
    node.each(function(d) {
      const g = d3.select(this);
      
      if (d.data.type === 'file') {
        g.append('rect')
          .attr('width', 20)
          .attr('height', 20)
          .attr('x', -10)
          .attr('y', -10)
          .attr('fill', '#4caf50')
          .attr('rx', 3);
          
        g.append('text')
          .attr('dy', 5)
          .attr('text-anchor', 'middle')
          .text('📄')
          .style('font-size', '14px');
      } else if (d.data.type === 'module') {
        g.append('rect')
          .attr('width', 24)
          .attr('height', 20)
          .attr('x', -12)
          .attr('y', -10)
          .attr('fill', '#ff9800')
          .attr('rx', 3);
          
        g.append('text')
          .attr('dy', 5)
          .attr('text-anchor', 'middle')
          .text('📁')
          .style('font-size', '14px');
      }
    });
    
    // Add labels
    node.append('text')
      .attr('dy', 25)
      .attr('text-anchor', 'middle')
      .text(d => d.data.name)
      .style('font-size', '10px')
      .style('fill', '#333');
    
    // Add zoom functionality
    const zoom = d3.zoom()
      .scaleExtent([0.1, 2])
      .on('zoom', event => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);
    
  }, [nodes, modules, onNodeSelect]);
  
  return <svg ref={svgRef} className="module-structure-svg"></svg>;
};

// Class Hierarchy Component
const ClassHierarchy = ({ nodes, links, onNodeSelect }) => {
  const svgRef = useRef(null);
  
  useEffect(() => {
    if (!nodes || !links || nodes.length === 0) return;
    
    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();
    
    // Filter only class nodes and inheritance links
    const classNodes = nodes.filter(node => node.type === 'class');
    
    if (classNodes.length === 0) {
      // No classes to display
      const svg = d3.select(svgRef.current)
        .attr("width", 400)
        .attr("height", 100);
      
      svg.append("text")
        .attr("x", 200)
        .attr("y", 50)
        .attr("text-anchor", "middle")
        .text("No class hierarchy to display")
        .style("font-size", "14px")
        .style("fill", "#666");
      
      return;
    }
    
    // Build inheritance relationships
    const classMap = {};
    classNodes.forEach(node => {
      classMap[node.name] = {
        ...node,
        children: []
      };
    });
    
    // Find inheritance relationships
    classNodes.forEach(node => {
      if (node.bases && node.bases.length > 0) {
        node.bases.forEach(baseName => {
          if (classMap[baseName]) {
            classMap[baseName].children.push(classMap[node.name]);
          }
        });
      }
    });
    
    // Find root classes (those not inheriting from any other class in our data)
    const rootClasses = Object.values(classMap).filter(cls => {
      if (!cls.bases || cls.bases.length === 0) return true;
      // Check if this class inherits only from external classes
      return !cls.bases.some(base => classMap[base]);
    });
    
    // Create hierarchy layout
    const width = 800;
    const height = 600;
    
    // Create the SVG
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
      .attr("width", width)
      .attr("height", height);
    
    // Create a group to center the hierarchy
    const g = svg.append("g")
      .attr("transform", `translate(${width/2}, 50)`);
    
    // If there are multiple root classes, create a virtual root
    const hierarchyRoot = rootClasses.length === 1 
      ? rootClasses[0] 
      : { id: 'root', name: 'Root', children: rootClasses, type: 'virtual' };
    
    // Create hierarchy layout
    const root = d3.hierarchy(hierarchyRoot);
    const treeLayout = d3.tree().size([width - 100, height - 100])
      .nodeSize([80, 100]); // Adjust node spacing
    
    treeLayout(root);
    
    // Add links between classes
    g.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d3.linkVertical()
        .x(d => d.x)
        .y(d => d.y)
      )
      .attr('fill', 'none')
      .attr('stroke', '#2196f3')
      .attr('stroke-width', 1.5);
    
    // Add nodes for each class
    const node = g.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', d => `node ${d.data.type}`)
      .attr('transform', d => `translate(${d.x}, ${d.y})`)
      .on('click', (event, d) => {
        if (d.data.id) onNodeSelect(d.data.id);
        event.stopPropagation();
      });
    
    // Don't show the virtual root if it exists
    node.filter(d => d.data.type !== 'virtual')
      .append('polygon')
      .attr('points', getHexagonPoints(20))
      .attr('fill', '#2196f3')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1.5);
    
    // Add labels for classes
    node.filter(d => d.data.type !== 'virtual')
      .append('text')
      .attr('dy', 5)
      .attr('text-anchor', 'middle')
      .text(d => d.data.name)
      .style('font-size', '12px')
      .style('fill', '#ffffff')
      .style('font-weight', 'bold');
    
    // Add method count
    node.filter(d => d.data.type !== 'virtual')
      .append('text')
      .attr('dy', 40)
      .attr('text-anchor', 'middle')
      .text(d => d.data.methods ? `${d.data.methods.length} methods` : '')
      .style('font-size', '10px')
      .style('fill', '#333');
    
    // Add file path as subtitle
    node.filter(d => d.data.type !== 'virtual')
      .append('text')
      .attr('dy', 55)
      .attr('text-anchor', 'middle')
      .text(d => d.data.path)
      .style('font-size', '9px')
      .style('fill', '#666');
    
    // Helper function for hexagon points
    function getHexagonPoints(radius) {
      const points = [];
      for (let i = 0; i < 6; i++) {
        const angle = (i * Math.PI / 3) - (Math.PI / 6);
        points.push(`${radius * Math.cos(angle)},${radius * Math.sin(angle)}`);
      }
      return points.join(' ');
    }
    
    // Add zoom functionality
    const zoom = d3.zoom()
      .scaleExtent([0.1, 2])
      .on('zoom', event => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);
  }, [nodes, links, onNodeSelect]);
  
  return <svg ref={svgRef} className="class-hierarchy-svg"></svg>;
};

export default Visualization;