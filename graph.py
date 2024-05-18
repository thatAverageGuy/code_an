import networkx as nx
import matplotlib.pyplot as plt
import os

def create_dependency_graph(all_imports, all_functions):
    G = nx.DiGraph()
    
    for filepath, functions in all_functions.items():
        for func, details in functions.items():
            func_name = f"{os.path.basename(filepath)}:{func}"
            G.add_node(func_name, type='function', details=details)
            for called_func in details['calls']:
                called_func_name = f"{called_func}"
                G.add_edge(func_name, called_func_name, relationship='calls')

    for filepath, imports in all_imports.items():
        for imported, origin in imports.items():
            imported_name = f"{os.path.basename(filepath)}:{imported}"
            G.add_node(imported_name, type='import')
            G.add_edge(origin, imported_name, relationship='import')
    
    return G

def save_graph(G, output_path):
    pos = nx.spring_layout(G)
    labels = {node: node for node in G.nodes()}
    edge_labels = {(u, v): d['relationship'] for u, v, d in G.edges(data=True)}
    plt.figure(figsize=(12, 12))
    nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', edge_color='gray', node_size=2000, font_size=10, font_weight='bold')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path)
    plt.close()
