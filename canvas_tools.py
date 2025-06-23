import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Force reload environment variables to avoid caching issues
load_dotenv(override=True)

# Load Canvas credentials from environment variables
CANVAS_TOKEN = os.environ.get("CANVAS_API_TOKEN")
CANVAS_BASE_URL = os.environ.get("CANVAS_BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
}

def _check_canvas_config():
    """Helper function to check if Canvas is configured"""
    if not CANVAS_TOKEN or not CANVAS_BASE_URL:
        return False, "Canvas API not configured properly. Check your .env file."
    return True, None

def _make_canvas_request(endpoint):
    """Helper function to make Canvas API requests"""
    is_configured, error_msg = _check_canvas_config()
    if not is_configured:
        return None, error_msg
    
    try:
        response = requests.get(f"{CANVAS_BASE_URL}{endpoint}", headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None, f"Canvas API error: {response.status_code} - {response.text[:100]}"
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, "Canvas API request timed out"
    except Exception as e:
        return None, f"Unexpected error: {e}"

def get_assignments(due_date: str = None, status: str = None):
    """
    Get Canvas assignments from the TODO list
    
    Args:
        due_date: Filter by due date - 'today', 'tomorrow', 'this_week', or specific date (YYYY-MM-DD)
        status: Filter by status - 'overdue', 'upcoming' (default: all)
    
    Returns:
        List of assignments or error message
    """
    data, error = _make_canvas_request("/api/v1/users/self/todo")
    if error:
        return error
    
    if not data:
        return "No assignments found."
    
    assignments = []
    today = datetime.now().date()
    
    for item in data:
        if "assignment" not in item:
            continue
            
        assignment = item["assignment"]
        assignment_name = assignment.get("name", "Unnamed assignment")
        due_at = assignment.get("due_at")
        
        # Parse due date
        due_date_obj = None
        if due_at:
            try:
                due_date_obj = datetime.fromisoformat(due_at.replace("Z", "")).date()
            except:
                pass
        
        # Apply date filter
        if due_date:
            if due_date.lower() == "today" and due_date_obj != today:
                continue
            elif due_date.lower() == "tomorrow" and due_date_obj != (today + timedelta(days=1)):
                continue
            elif due_date.lower() == "this_week":
                week_end = today + timedelta(days=(6 - today.weekday()))
                if not due_date_obj or due_date_obj > week_end:
                    continue
            elif due_date not in ["today", "tomorrow", "this_week"]:
                try:
                    target_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                    if due_date_obj != target_date:
                        continue
                except:
                    pass  # Invalid date format, include all
        
        # Apply status filter
        if status:
            if status.lower() == "overdue" and (not due_date_obj or due_date_obj >= today):
                continue
            elif status.lower() == "upcoming" and due_date_obj and due_date_obj < today:
                continue
        
        # Format assignment info
        due_str = due_date_obj.strftime("%m/%d/%Y") if due_date_obj else "No due date"
        assignments.append(f"{assignment_name} (Due: {due_str})")
    
    return assignments if assignments else f"No assignments found matching the criteria."

def get_announcements(unread_only: bool = False, course_id: str = None):
    """
    Get Canvas announcements
    
    Args:
        unread_only: Only return unread announcements (default: False)
        course_id: Get announcements for specific course (default: all courses)
    
    Returns:
        List of announcements or error message
    """
    endpoint = "/api/v1/announcements"
    params = []
    
    if course_id:
        params.append(f"context_codes[]=course_{course_id}")
    
    if params:
        endpoint += "?" + "&".join(params)
    
    data, error = _make_canvas_request(endpoint)
    if error:
        return error
    
    if not data:
        return "No announcements found."
    
    announcements = []
    for announcement in data:
        title = announcement.get("title", "Untitled announcement")
        posted_date = announcement.get("posted_at", "")
        
        # Parse posted date
        if posted_date:
            try:
                posted_obj = datetime.fromisoformat(posted_date.replace("Z", ""))
                posted_str = posted_obj.strftime("%m/%d/%Y")
            except:
                posted_str = "Unknown date"
        else:
            posted_str = "Unknown date"
        
        # Apply unread filter (Canvas API doesn't always provide read status reliably)
        announcements.append(f"{title} (Posted: {posted_str})")
    
    return announcements if announcements else "No announcements found."

def get_calendar_events(start_date: str = None, end_date: str = None):
    """
    Get Canvas calendar events
    
    Args:
        start_date: Start date for events - 'today', 'tomorrow', or specific date (YYYY-MM-DD)
        end_date: End date for events (default: same as start_date or today)
    
    Returns:
        List of calendar events or error message
    """
    today = datetime.now().date()
    
    # Parse start_date
    if start_date:
        if start_date.lower() == "today":
            start_obj = today
        elif start_date.lower() == "tomorrow":
            start_obj = today + timedelta(days=1)
        else:
            try:
                start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            except:
                start_obj = today
    else:
        start_obj = today
    
    # Parse end_date
    if end_date:
        try:
            end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except:
            end_obj = start_obj
    else:
        end_obj = start_obj
    
    endpoint = f"/api/v1/calendar_events?start_date={start_obj}&end_date={end_obj}"
    
    data, error = _make_canvas_request(endpoint)
    if error:
        return error
    
    if not data:
        return f"No calendar events found for {start_obj.strftime('%m/%d/%Y')}."
    
    events = []
    for event in data:
        title = event.get("title", "Untitled event")
        start_at = event.get("start_at", "")
        
        # Parse event time
        if start_at:
            try:
                start_time_obj = datetime.fromisoformat(start_at.replace("Z", ""))
                time_str = start_time_obj.strftime("%I:%M %p")
            except:
                time_str = "All day"
        else:
            time_str = "All day"
        
        events.append(f"{title} at {time_str}")
    
    return events if events else f"No calendar events found for the specified date range."

def get_courses():
    """
    Get list of current Canvas courses
    
    Returns:
        List of courses or error message
    """
    endpoint = "/api/v1/courses?enrollment_state=active"
    
    data, error = _make_canvas_request(endpoint)
    if error:
        return error
    
    if not data:
        return "No courses found."
    
    courses = []
    for course in data:
        course_name = course.get("name", "Unnamed course")
        course_code = course.get("course_code", "")
        
        if course_code:
            courses.append(f"{course_code}: {course_name}")
        else:
            courses.append(course_name)
    
    return courses if courses else "No active courses found."
