from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import sys
from pathlib import Path
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import the model
sys.path.append(str(Path(__file__).parent.parent))

from model.main import (
    run_prompt, 
    convert_upn_to_png, 
    prompt1, 
    prompt2, 
    prompt3, 
    prompt4, 
    prompt5,
    save_result
)

app = Flask(__name__)
CORS(app)

# Configure upload folder for temporary files
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/collaborative-editor')
def collaborative_editor():
    """Serve the collaborative document editor interface."""
    return render_template('collaborative-editor.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_workflow():
    """API endpoint to start the workflow analysis process."""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '').strip()
        
        if not user_input:
            return jsonify({'error': 'User input is required'}), 400
        
        # Create a temporary directory for this analysis session
        session_id = f"session_{int(os.urandom(4).hex(), 16)}"
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save user input to a temporary file
        user_input_file = os.path.join(session_dir, 'user_input.txt')
        with open(user_input_file, 'w') as f:
            f.write(user_input)
        
        # Step 1: Extract raw requirements
        print("Starting Step 1...")
        step1_result = run_prompt(
            prompt1,
            context_files=[Path(session_dir) / "user_input.txt"]
        )
        
        # Save step 1 result first
        step1_file = os.path.join(session_dir, "step1_raw_requirements.json")
        with open(step1_file, 'w') as f:
            f.write(step1_result)
        
        # Step 2: Create user story
        print("Starting Step 2...")
        step2_result = run_prompt(
            prompt2,
            context_files=[
                Path("../context-data/user_story_q.json"),
                Path(session_dir) / "step1_raw_requirements.json"
            ]
        )
        
        # Save step 2 result
        step2_file = os.path.join(session_dir, "step2_user_story.json")
        with open(step2_file, 'w') as f:
            f.write(step2_result)
        
        # Parse step 2 result to check for questions
        print('DEBUG: About to parse step2_result:', repr(step2_result))
        if not step2_result.strip():
            print('ERROR: LLM returned empty response for step2_result')
            return jsonify({'error': 'LLM returned empty response for user story'}), 500
        
        try:
            step2_data = json.loads(step2_result)
        except json.JSONDecodeError as e:
            print('ERROR: Failed to parse step2_result:', repr(step2_result))
            return jsonify({'error': f'Failed to parse user story JSON: {e}', 'raw': step2_result}), 500
        questions = step2_data.get('questions_for_user', [])
        
        return jsonify({
            'session_id': session_id,
            'step1_result': step1_result,
            'step2_result': step2_data.get('user_story', {}),
            'questions': questions,
            'status': 'ready_for_questions' if questions else 'ready_for_diagram'
        })
        
    except Exception as e:
        print(f"Error in analyze_workflow: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/answer-questions', methods=['POST'])
def answer_questions():
    """API endpoint to handle user answers to clarification questions."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answers = data.get('answers', [])
        
        if not session_id or not answers:
            return jsonify({'error': 'Session ID and answers are required'}), 400
        
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session not found'}), 404
        
        # Load previous results
        step2_file = os.path.join(session_dir, "step2_user_story.json")
        with open(step2_file, 'r') as f:
            step2_result = f.read()
        
        # Process each answer
        current_result = step2_result
        for answer in answers:
            question = answer.get('question')
            user_answer = answer.get('answer')
            
            if question and user_answer:
                prompt3_with_answer = f'{prompt3}\n\nQuestion: {question}\n\nUser answer: {user_answer}'
                current_result = run_prompt(
                    prompt3_with_answer,
                    context_files=[
                        Path("../context-data/user_story_q.json"),
                        Path(session_dir) / "step2_user_story.json"
                    ]
                )
                
                # Update the step2 file with the new result
                with open(step2_file, 'w') as f:
                    f.write(current_result)
        
        # Parse the final result
        print('DEBUG: About to parse current_result:', repr(current_result))
        if not current_result.strip():
            print('ERROR: LLM returned empty response for current_result')
            return jsonify({'error': 'LLM returned empty response for clarification'}), 500
        
        try:
            final_data = json.loads(current_result)
        except json.JSONDecodeError as e:
            print('ERROR: Failed to parse current_result:', repr(current_result))
            return jsonify({'error': f'Failed to parse clarification JSON: {e}', 'raw': current_result}), 500
        questions = final_data.get('questions_for_user', [])
        
        return jsonify({
            'user_story': final_data.get('user_story', {}),
            'questions': questions,
            'status': 'ready_for_questions' if questions else 'ready_for_diagram'
        })
        
    except Exception as e:
        print(f"Error in answer_questions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-diagram', methods=['POST'])
def generate_diagram():
    """API endpoint to generate the UPN diagram."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        if not os.path.exists(session_dir):
            return jsonify({'error': 'Session not found'}), 404
        
        # Step 4: Generate UPN diagram
        print("Starting Step 4...")
        step4_result = run_prompt(
            prompt4,
            context_files=[
                Path("../context-data/process_diagrams.json"),
                Path("../context-data/saleforce_flow_caps.json"),
                Path(session_dir) / "step2_user_story.json"
            ]
        )
        
        # Save step 4 result
        step4_file = os.path.join(session_dir, "step4_upn_diagram.json")
        with open(step4_file, 'w') as f:
            f.write(step4_result)
        
        # Debug: Print the raw response
        print(f"Step 4 raw result: {step4_result[:200]}...")
        
        # Parse the UPN diagram with better error handling
        print('DEBUG: About to parse step4_result:', repr(step4_result))
        if not step4_result.strip():
            print('ERROR: LLM returned empty response for step4_result')
            return jsonify({'error': 'LLM returned empty response for UPN diagram'}), 500
        
        try:
            step4_data = json.loads(step4_result)
            upn_diagram = step4_data.get('upn_diagram', {})
            
            # Debug: Print the structure of step4_data
            print(f"DEBUG: step4_data keys: {list(step4_data.keys())}")
            print(f"DEBUG: upn_diagram type: {type(upn_diagram)}")
            print(f"DEBUG: upn_diagram value: {repr(upn_diagram)}")
            
            # If upn_diagram is a string, try to parse it as JSON
            if isinstance(upn_diagram, str) and upn_diagram.strip():
                try:
                    upn_diagram = json.loads(upn_diagram)
                except json.JSONDecodeError:
                    print(f"WARNING: upn_diagram is a string but not valid JSON: {repr(upn_diagram)}")
                    upn_diagram = {}
            
            # If upn_diagram is still not a dict, create a fallback
            if not isinstance(upn_diagram, dict):
                print(f"WARNING: upn_diagram is not a dict, creating fallback. Type: {type(upn_diagram)}")
                upn_diagram = {
                    "steps": [
                        {
                            "id": "start",
                            "type": "Record Event", 
                            "label": "Process Started",
                            "actor": "System",
                            "next_step_ids": ["end"]
                        },
                        {
                            "id": "end",
                            "type": "End",
                            "label": "Process Completed", 
                            "actor": "System",
                            "next_step_ids": []
                        }
                    ]
                }
                
        except json.JSONDecodeError as e:
            print('ERROR: Failed to parse step4_result:', repr(step4_result))
            return jsonify({'error': f'Failed to parse UPN diagram JSON: {e}', 'raw': step4_result}), 500
        
        # Convert structured UPN to Mermaid diagram string
        mermaid_diagram = convert_upn_to_mermaid(upn_diagram)
        
        # Save Mermaid diagram
        mermaid_file = os.path.join(session_dir, "workflow_diagram.mmd")
        with open(mermaid_file, 'w') as f:
            f.write(mermaid_diagram)
        
        # Step 5: Generate technical specification
        print("Starting Step 5...")
        step5_result = run_prompt(
            prompt5,
            context_files=[
                Path("../context-data/saleforce_flow_caps.json"),
                Path(session_dir) / "step4_upn_diagram.json"
            ]
        )
        
        # Save step 5 result
        step5_file = os.path.join(session_dir, "step5_tech_spec.json")
        with open(step5_file, 'w') as f:
            f.write(step5_result)
        
        # Parse step 5 result with error handling
        print('DEBUG: About to parse step5_result:', repr(step5_result))
        if not step5_result.strip():
            print('ERROR: LLM returned empty response for step5_result')
            tech_spec = {'error': 'LLM returned empty response for technical spec'}
        else:
            try:
                tech_spec = json.loads(step5_result)
            except json.JSONDecodeError as e:
                print('ERROR: Failed to parse step5_result:', repr(step5_result))
                tech_spec = {'error': f'Failed to parse technical spec JSON: {e}', 'raw': step5_result}
        
        return jsonify({
            'upn_diagram': upn_diagram,
            'mermaid_diagram': mermaid_diagram,
            'tech_spec': tech_spec,
            'status': 'complete'
        })
        
    except Exception as e:
        print(f"Error in generate_diagram: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagram/<session_id>/<filename>')
def serve_diagram(session_id, filename):
    """Serve the generated diagram file."""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png')
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """Clean up temporary files for a session."""
    try:
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
        return jsonify({'message': 'Session cleaned up successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def convert_upn_to_mermaid(upn_diagram: dict) -> str:
    """Convert structured UPN diagram to Mermaid flowchart string."""
    print("Converting UPN to Mermaid diagram...")
    print(f"DEBUG: Input upn_diagram type: {type(upn_diagram)}")
    print(f"DEBUG: Input upn_diagram: {repr(upn_diagram)}")
    
    if not upn_diagram or not isinstance(upn_diagram, dict):
        print(f"ERROR: Invalid upn_diagram - type: {type(upn_diagram)}, value: {repr(upn_diagram)}")
        raise ValueError("UPN diagram must be a valid dictionary")
    
    steps = upn_diagram.get('steps', [])
    if not steps:
        print(f"WARNING: No steps found in UPN diagram. Available keys: {list(upn_diagram.keys())}")
        # Create a minimal fallback diagram
        return """flowchart TD
    start["📥 Process Started"]
    end["🏁 Process Completed"]
    start --> end"""
    
    # Start Mermaid flowchart
    mermaid_lines = ["flowchart TD"]
    
    # Add nodes
    for step in steps:
        step_id = step.get('id', '')
        step_type = step.get('type', '')
        step_label = step.get('label', '')
        step_actor = step.get('actor', '')
        
        if not step_id:
            continue
            
        # Format node based on type
        if step_type == 'Record Event':
            mermaid_lines.append(f'    {step_id}["📥 {step_label}"]')
        elif step_type == 'Do':
            mermaid_lines.append(f'    {step_id}["⚙️ {step_label}"]')
        elif step_type == 'Wait':
            mermaid_lines.append(f'    {step_id}["⏱️ {step_label}"]')
        elif step_type == 'Check':
            condition = step.get('condition', '')
            mermaid_lines.append(f'    {step_id}{{"🔍 {step_label}"}}')
        elif step_type == 'Notify':
            mermaid_lines.append(f'    {step_id}["📧 {step_label}"]')
        elif step_type == 'End':
            mermaid_lines.append(f'    {step_id}["🏁 {step_label}"]')
        else:
            mermaid_lines.append(f'    {step_id}["{step_label}"]')
    
    # Add connections
    for step in steps:
        step_id = step.get('id', '')
        next_step_ids = step.get('next_step_ids', [])
        step_type = step.get('type', '')
        step_condition = step.get('condition', '')
        
        if not next_step_ids:
            continue
            
        if step_type == 'Check' and len(next_step_ids) == 2:
            # Decision point with two paths
            mermaid_lines.append(f'    {step_id} -->|Yes| {next_step_ids[0]}')
            mermaid_lines.append(f'    {step_id} -->|No| {next_step_ids[1]}')
        else:
            # Single path
            for next_id in next_step_ids:
                mermaid_lines.append(f'    {step_id} --> {next_id}')
    
    mermaid_diagram = '\n'.join(mermaid_lines)
    print(f"✓ Mermaid diagram generated ({len(mermaid_lines)} lines)")
    return mermaid_diagram

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003) 