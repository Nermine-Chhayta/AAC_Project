import json
import urllib.request

base = 'http://127.0.0.1:8000/tasks'
items = [
    {'title': 'Draft UI', 'description': 'Prepare the board', 'status': 'ToDo', 'priority': 'High', 'assignee': 'Ada'},
    {'title': 'Review API', 'description': 'Check task payloads', 'status': 'InProgress', 'priority': 'Medium', 'assignee': 'Sam'},
    {'title': 'Ship release', 'description': 'Finalize deployment', 'status': 'Done', 'priority': 'Low', 'assignee': 'Lee'},
]

for item in items:
    req = urllib.request.Request(
        base,
        data=json.dumps(item).encode(),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req) as response:
        print(response.status)
