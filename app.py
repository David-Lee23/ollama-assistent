#!/usr/bin/env python3
"""
Flask Web Interface for Student Assistant Agent
Main application file with routes and API endpoints
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import os
import json
from memory import (
    log_message, get_conversation_messages, search_memory, 
    get_message_count, clear_history, get_conversation_summary
)
from chat_tools import run_chat_message
from canvas_tools import get_assignments, get_announcements, get_calendar_events, get_courses

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

@app.route('/')
def index():
    """Main dashboard page"""
    message_count = get_message_count()
    summary = get_conversation_summary()
    
    return render_template('dashboard.html', 
                         message_count=message_count,
                         summary=summary)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Process the message through the agent
        response = run_chat_message(message)
        
        # Return the response
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'message_count': get_message_count()
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
        
        if not term:
            return jsonify({'error': 'Search term cannot be empty'}), 400
        
        results = search_memory(term, limit=limit)
        
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
            'term': term
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/status', methods=['GET'])
def api_memory_status():
    """Get memory statistics and summary"""
    try:
        message_count = get_message_count()
        summary = get_conversation_summary()
        recent_messages = get_conversation_messages(limit=5)
        
        return jsonify({
            'message_count': message_count,
            'summary': summary,
            'recent_messages': recent_messages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/clear', methods=['POST'])
def api_memory_clear():
    """Clear all memory"""
    try:
        clear_history()
        return jsonify({
            'success': True,
            'message': 'Memory cleared successfully',
            'message_count': 0
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
    
    app.run(debug=True, host='0.0.0.0', port=5000) 