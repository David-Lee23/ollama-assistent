#!/usr/bin/env python3
"""
Flask Web Interface for Student Assistant Agent
Main application file with routes and API endpoints
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
import json
import secrets
from memory import (
    log_message, get_conversation_messages, search_memory, 
    get_message_count, clear_history, get_conversation_summary,
    create_project, get_projects, get_project, update_project, delete_project,
    get_project_summary, generate_project_summary
)
from chat_tools import run_chat_message
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route('/')
def index():
    """Main dashboard page"""
    message_count = get_message_count()
    summary = get_conversation_summary()
    projects = get_projects()
    
    return render_template('dashboard.html', 
                         message_count=message_count,
                         summary=summary,
                         projects=projects)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        project_id = data.get('project_id')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Process the message through the agent
        response = run_chat_message(message, project_id)
        
        # Return the response
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'message_count': get_message_count(project_id),
            'project_id': project_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Project Management Endpoints
@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    """Get all projects"""
    try:
        projects = get_projects()
        return jsonify({'projects': projects})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
def api_create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        system_prompt = data.get('system_prompt', '').strip()
        
        if not name:
            return jsonify({'error': 'Project name cannot be empty'}), 400
        
        project_id = create_project(name, description, system_prompt)
        project = get_project(project_id)
        
        return jsonify({
            'success': True,
            'project': project,
            'message': f'Project "{name}" created successfully'
        }), 201
        
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'A project with this name already exists'}), 400
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>', methods=['GET'])
def api_get_project(project_id):
    """Get a specific project"""
    try:
        project = get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({'project': project})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def api_update_project(project_id):
    """Update a project"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        system_prompt = data.get('system_prompt')
        
        success = update_project(project_id, name, description, system_prompt)
        if not success:
            return jsonify({'error': 'Project not found'}), 404
        
        project = get_project(project_id)
        return jsonify({
            'success': True,
            'project': project,
            'message': 'Project updated successfully'
        })
        
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'A project with this name already exists'}), 400
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    """Delete a project"""
    try:
        # Don't allow deleting the default project (id=1)
        if project_id == 1:
            return jsonify({'error': 'Cannot delete the default project'}), 400
        
        success = delete_project(project_id)
        if not success:
            return jsonify({'error': 'Project not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>/summary', methods=['GET'])
def api_get_project_summary(project_id):
    """Get a project's summary"""
    try:
        project = get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        summary = get_project_summary(project_id)
        return jsonify({
            'project_id': project_id,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>/summary', methods=['POST'])
def api_generate_project_summary(project_id):
    """Generate a new summary for a project"""
    try:
        project = get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Check if project has enough messages
        message_count = get_message_count(project_id)
        if message_count < 5:
            return jsonify({'error': 'Project needs at least 5 messages to generate a summary'}), 400
        
        summary = generate_project_summary(project_id)
        if not summary:
            return jsonify({'error': 'Failed to generate summary'}), 500
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'summary': summary,
            'message': 'Project summary generated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/search', methods=['POST'])
def api_memory_search():
    """Search memory with manual query"""
    try:
        data = request.get_json()
        term = data.get('term', '').strip()
        limit = data.get('limit', 10)
        project_id = data.get('project_id')
        
        if not term:
            return jsonify({'error': 'Search term cannot be empty'}), 400
        
        results = search_memory(term, limit=limit, project_id=project_id)
        
        # Format results for JSON response
        formatted_results = []
        for role, content, timestamp in results:
            formatted_results.append({
                'role': role,
                'content': content,
                'timestamp': timestamp
            })
        
        return jsonify({
            'results': formatted_results,
            'count': len(formatted_results),
            'term': term,
            'project_id': project_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/status', methods=['GET'])
def api_memory_status():
    """Get memory statistics and summary"""
    try:
        project_id = request.args.get('project_id', type=int)
        
        message_count = get_message_count(project_id)
        summary = get_conversation_summary(project_id=project_id)
        recent_messages = get_conversation_messages(limit=5, project_id=project_id)
        
        return jsonify({
            'message_count': message_count,
            'summary': summary,
            'recent_messages': recent_messages,
            'project_id': project_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/clear', methods=['POST'])
def api_memory_clear():
    """Clear all memory"""
    try:
        data = request.get_json() or {}
        project_id = data.get('project_id')
        
        clear_history(project_id)
        
        return jsonify({
            'success': True,
            'message': 'Memory cleared successfully',
            'message_count': 0,
            'project_id': project_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/canvas/assignments', methods=['GET'])
def api_canvas_assignments():
    """Get Canvas assignments"""
    try:
        due_date = request.args.get('due_date')
        status = request.args.get('status')
        
        kwargs = {}
        if due_date:
            kwargs['due_date'] = due_date
        if status:
            kwargs['status'] = status
        
        assignments = get_assignments(**kwargs)
        return jsonify({'assignments': assignments})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/canvas/announcements', methods=['GET'])
def api_canvas_announcements():
    """Get Canvas announcements"""
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        course_id = request.args.get('course_id')
        
        kwargs = {'unread_only': unread_only}
        if course_id:
            kwargs['course_id'] = course_id
        
        announcements = get_announcements(**kwargs)
        return jsonify({'announcements': announcements})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/canvas/events', methods=['GET'])
def api_canvas_events():
    """Get Canvas calendar events"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        kwargs = {}
        if start_date:
            kwargs['start_date'] = start_date
        if end_date:
            kwargs['end_date'] = end_date
        
        events = get_calendar_events(**kwargs)
        return jsonify({'events': events})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/canvas/courses', methods=['GET'])
def api_canvas_courses():
    """Get Canvas courses"""
    try:
        courses = get_courses()
        return jsonify({'courses': courses})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/status', methods=['GET'])
def api_system_status():
    """Get system status and health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'memory_count': get_message_count(),
            'version': '1.0.0'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure templates and static directories exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("🚀 Starting Student Assistant Web Interface...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🧠 Memory status:", get_message_count(), "messages stored")
    
    app.run(debug=False, host='0.0.0.0', port=5000) 