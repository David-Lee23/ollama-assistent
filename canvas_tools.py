# canvas_tools.py

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Force reload environment variables to avoid caching issues
load_dotenv(override=True)

# Load your token and base URL from environment variables or hardcode here (for dev)
CANVAS_TOKEN = os.environ.get("CANVAS_API_TOKEN")
CANVAS_BASE_URL = os.environ.get("CANVAS_BASE_URL")  # e.g. https://youruniversity.instructure.com

HEADERS = {
    "Authorization": f"Bearer {CANVAS_TOKEN}"
}


def get_canvas_info(resource: str, filter: str = None, date: str = None):
    if not CANVAS_TOKEN or not CANVAS_BASE_URL:
        return "Canvas API not configured properly."

    # Map Canvas resources to their API endpoints
    if resource == "assignments":
        endpoint = f"{CANVAS_BASE_URL}/api/v1/users/self/todo"
    elif resource == "announcements":
        endpoint = f"{CANVAS_BASE_URL}/api/v1/announcements"
    elif resource == "calendar":
        endpoint = f"{CANVAS_BASE_URL}/api/v1/calendar_events"
    else:
        return f"Unsupported resource: {resource}"

    try:
        response = requests.get(endpoint, headers=HEADERS)
        if response.status_code != 200:
            return f"Error fetching Canvas data: {response.status_code}"

        data = response.json()

        # Simple filtering (start with "due today")
        if resource == "assignments" and date == "today":
            today = datetime.today().date()
            data = [
                item for item in data
                if "assignment" in item and item["assignment"]["due_at"] and
                   datetime.fromisoformat(item["assignment"]["due_at"].replace("Z", "")).date() == today
            ]

        # Format output
        items = [
            item.get("assignment", {}).get("name", "Unnamed assignment")
            for item in data
        ]

        return items or f"No {resource} found for {date or 'all'}."

    except Exception as e:
        return f"Unexpected error: {e}"
