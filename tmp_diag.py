import json
import urllib.request

base = 'http://127.0.0.1:8000'

req = urllib.request.Request(
    base + '/tasks',
    data=json.dumps({'title': 'diag task', 'due_date': '2000-01-01'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
with urllib.request.urlopen(req) as resp:
    task = json.loads(resp.read().decode())
    task_id = task['id']
print('created', task)

req = urllib.request.Request(
    base + '/tasks/' + task_id,
    data=json.dumps({'status': 'Done'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PATCH',
)
with urllib.request.urlopen(req) as resp:
    done_task = json.loads(resp.read().decode())
print('done', done_task)

req = urllib.request.Request(
    base + '/tasks/' + task_id,
    data=json.dumps({'status': 'InProgress'}).encode(),
    headers={'Content-Type': 'application/json'},
    method='PATCH',
)
with urllib.request.urlopen(req) as resp:
    updated_task = json.loads(resp.read().decode())
print('inprogress', updated_task)
