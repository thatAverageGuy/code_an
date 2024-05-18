from flask import Flask, request, jsonify, send_file, after_this_request
from werkzeug.utils import secure_filename
import os
import traceback
import zipfile
import tempfile
from utils import get_python_files, clone_github_repo, cleanup_temp_dir, generate_summary_github, generate_summary
from analyzer import analyze_files
from graph import create_dependency_graph, save_graph

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route('/upload', methods=['POST'])
def upload_project():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    
    # Create a temporary directory to extract the uploaded zip file
    temp_dir = tempfile.mkdtemp()
    try:
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Extract the uploaded zip file
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Process the Python files in the extracted directory
        python_files = get_python_files(temp_dir)
        all_imports, all_functions = analyze_files(python_files)
        G = create_dependency_graph(all_imports, all_functions)
        
        output_path = os.path.join('graph', 'project_structure.png')
        save_graph(G, output_path)
        
        # Generate summary
        summary = generate_summary(all_imports, all_functions, temp_dir)
        
        return jsonify({
            'status': 'success',
            'message': 'Project analyzed successfully. Graph saved in the graph directory.',
            'graph_path': os.path.abspath(output_path),
            'summary': summary
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cleanup_temp_dir(temp_dir)

@app.route('/github', methods=['POST'])
def github_project():
    data = request.json
    github_url = data.get('github_url')

    if not github_url:
        return jsonify({'status': 'error', 'message': 'GitHub URL is required'}), 400

    try:
        temp_dir = clone_github_repo(github_url)
        python_files = get_python_files(temp_dir)
        all_imports, all_functions = analyze_files(python_files)
        G = create_dependency_graph(all_imports, all_functions)
        
        output_path = os.path.join('graph', 'project_structure.png')
        save_graph(G, output_path)
        
        summary = generate_summary_github(all_imports, all_functions, github_url, temp_dir)
        
        return jsonify({
            'status': 'success',
            'message': 'Project analyzed successfully. Graph saved in the graph directory.',
            'graph_path': os.path.abspath(output_path),
            'summary': summary
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cleanup_temp_dir(temp_dir)


@app.route('/graph', methods=['GET'])
def get_graph():
    graph_path = os.path.join(tempfile.gettempdir(), 'dependency_graph.png')
    return send_file(graph_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
