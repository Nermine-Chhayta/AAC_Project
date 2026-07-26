def test_frontend_can_load_tasks_and_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Draft UI",
            "description": "Prepare the board",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Ada",
        },
    )
    assert response.status_code == 201

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    body = list_response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Draft UI"

    update_response = client.patch(
        f"/tasks/{body[0]['id']}",
        json={"status": "InProgress"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "InProgress"
