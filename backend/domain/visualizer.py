import os
import networkx as nx
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import tempfile
from config import settings

class GraphVisualizerStrategy(ABC):
    """Base strategy class for visualizing code analysis results"""
    
    @abstractmethod
    def visualize(self, analysis_results: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a visualization from analysis results
        
        Args:
            analysis_results: Dictionary with analysis data
            output_path: Optional path to save the visualization
            
        Returns:
            Path to the generated visualization
        """
        pass

class NetworkXVisualizer(GraphVisualizerStrategy):
    """Strategy for visualizing code dependencies using NetworkX"""
    
    def visualize(self, analysis_results: Dict[str, Dict], output_path: str = None) -> str:
        # Create directed graph
        G = nx.DiGraph()
        
        # Process each file's analysis
        for file_path, analysis in analysis_results.items():
            file_name = os.path.basename(file_path)
            
            # Add import nodes and edges
            if 'imports' in analysis:
                for imported_name, origin in analysis['imports'].items():
                    imported_node = f"{file_name}:{imported_name}"
                    G.add_node(imported_node, type='import')
                    G.add_edge(origin, imported_node, relationship='import')
            
            # Add function nodes and edges
            if 'functions' in analysis:
                for func_name, details in analysis['functions'].items():
                    func_node = f"{file_name}:{func_name}"
                    G.add_node(func_node, type='function', details=details)
                    
                    # Add edges for function calls
                    for called_func in details.get('calls', []):
                        G.add_edge(func_node, called_func, relationship='calls')
            
            # Add class nodes
            if 'classes' in analysis:
                for class_name, details in analysis['classes'].items():
                    class_node = f"{file_name}:{class_name}"
                    G.add_node(class_node, type='class', details=details)
                    
                    # Add inheritance edges
                    for base in details.get('bases', []):
                        G.add_edge(class_node, base, relationship='inherits')
        
        # Generate the visualization
        if output_path is None:
            output_path = os.path.join(settings.GRAPH_OUTPUT_DIR, 'dependency_graph.png')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create the layout
        pos = nx.spring_layout(G)
        
        # Set up the figure
        plt.figure(figsize=(12, 10))
        
        # Define node colors by type
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node].get('type', 'unknown')
            if node_type == 'function':
                node_colors.append('#ADD8E6')  # Light blue
            elif node_type == 'import':
                node_colors.append('#98FB98')  # Pale green
            elif node_type == 'class':
                node_colors.append('#FFA07A')  # Light salmon
            else:
                node_colors.append('#D3D3D3')  # Light grey
        
        # Draw the network
        nx.draw(
            G, pos, 
            with_labels=True,
            node_color=node_colors,
            node_size=2000,
            font_size=8,
            font_weight='bold',
            edge_color='gray'
        )
        
        # Add edge labels
        edge_labels = {(u, v): d['relationship'] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path

class D3Visualizer(GraphVisualizerStrategy):
    """Strategy for visualizing code dependencies using D3.js"""
    
    def visualize(self, analysis_results: Dict[str, Any], output_path: str = None) -> str:
        # Convert analysis results to D3-compatible JSON format
        nodes = []
        links = []
        node_map = {}  # To track node indices
        
        node_index = 0
        
        # Process each file's analysis to create nodes and links
        for file_path, analysis in analysis_results.items():
            file_name = os.path.basename(file_path)
            
            # Process functions
            if 'functions' in analysis:
                for func_name, details in analysis['functions'].items():
                    node_id = f"{file_name}:{func_name}"
                    nodes.append({
                        "id": node_id,
                        "name": func_name,
                        "file": file_name,
                        "type": "function"
                    })
                    node_map[node_id] = node_index
                    node_index += 1
                    
                    # Add links for function calls
                    for called_func in details.get('calls', []):
                        links.append({
                            "source": node_id,
                            "target": called_func,
                            "type": "calls"
                        })
        
        # If output path is provided, write the D3 JSON data
        if output_path is None:
            output_path = os.path.join(settings.GRAPH_OUTPUT_DIR, 'dependency_graph.json')
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create the D3 compatible JSON
        d3_data = {
            "nodes": nodes,
            "links": links
        }
        
        # Write the JSON to file
        import json
        with open(output_path, 'w') as f:
            json.dump(d3_data, f, indent=2)
        
        return output_path