from datetime import date, timedelta


def create_filter_task(
    client,
    title,
    description="",
    status="ToDo",
    priority="Medium",
    assignee=None,
    due_date=None,
):
    payload = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
    }
    if assignee is not None:
        payload["assignee"] = assignee
    if due_date is not None:
        payload["due_date"] = due_date

    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "Write tests",
        "description": "Cover task routes",
        "status": "ToDo",
        "priority": "High",
        "assignee": "Ada",
    }

    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "Write tests"
    assert body["description"] == "Cover task routes"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Ada"
    assert body["created_at"]
    assert body["updated_at"]


def test_create_task_with_due_date_returns_201_and_saves_due_date(client):
    response = client.post(
        "/tasks",
        json={"title": "Due soon", "due_date": "2030-01-01"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == "2030-01-01"
    assert body["task_state"] == "active"


def test_create_task_invalid_due_date_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad date", "due_date": "not-a-date"})

    assert response.status_code == 422


def test_patch_update_due_date_allows_add_change_and_remove(client, created_task):
    update_response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"due_date": "2030-01-01"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["due_date"] == "2030-01-01"

    change_response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"due_date": "2035-01-01"},
    )
    assert change_response.status_code == 200
    assert change_response.json()["due_date"] == "2035-01-01"

    remove_response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"due_date": None},
    )
    assert remove_response.status_code == 200
    assert remove_response.json()["due_date"] is None


def test_task_state_is_overdue_for_past_due_date_and_completed_for_done(client):
    past_due = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    future_due = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    overdue_response = client.post("/tasks", json={"title": "Overdue task", "due_date": past_due})
    assert overdue_response.status_code == 201
    assert overdue_response.json()["task_state"] == "overdue"

    future_response = client.post("/tasks", json={"title": "Future task", "due_date": future_due})
    assert future_response.status_code == 201
    assert future_response.json()["task_state"] == "active"

    done_response = client.post(
        "/tasks",
        json={"title": "Done task", "status": "Done", "due_date": past_due},
    )
    assert done_response.status_code == 201
    assert done_response.json()["task_state"] == "completed"


def test_list_tasks_filter_by_overdue_returns_only_overdue_tasks(client):
    past_due = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    future_due = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    client.post("/tasks", json={"title": "Overdue", "due_date": past_due})
    client.post("/tasks", json={"title": "Future", "due_date": future_due})
    client.post("/tasks", json={"title": "No due date"})

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Overdue"
    assert body[0]["task_state"] == "overdue"


def test_list_tasks_search_matches_title_case_insensitive(client):
    create_filter_task(client, "Write API tests")
    create_filter_task(client, "Review docs")

    response = client.get("/tasks", params={"q": "api"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Write API tests"


def test_list_tasks_search_matches_description_case_insensitive(client):
    create_filter_task(client, "Backend work", description="Add keyword filters")
    create_filter_task(client, "Frontend work", description="Polish empty states")

    response = client.get("/tasks", params={"q": "KEYWORD"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Backend work"


def test_list_tasks_search_no_match_returns_empty_list(client):
    create_filter_task(client, "Write API tests", description="Cover task routes")

    response = client.get("/tasks", params={"q": "billing"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_empty_search_returns_unfiltered_list(client):
    create_filter_task(client, "First task")
    create_filter_task(client, "Second task")

    response = client.get("/tasks", params={"q": "   "})

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["First task", "Second task"]


def test_list_tasks_filter_by_status_returns_only_matches(client):
    create_filter_task(client, "Todo task", status="ToDo")
    create_filter_task(client, "Progress task", status="InProgress")

    response = client.get("/tasks", params={"status": "InProgress"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Progress task"
    assert body[0]["status"] == "InProgress"


def test_list_tasks_invalid_status_returns_422(client):
    create_filter_task(client, "Todo task")

    response = client.get("/tasks", params={"status": "Blocked"})

    assert response.status_code == 422


def test_list_tasks_filter_by_priority_no_match_returns_empty_list(client):
    create_filter_task(client, "Medium task", priority="Medium")

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_invalid_priority_returns_422(client):
    create_filter_task(client, "Medium task")

    response = client.get("/tasks", params={"priority": "Urgent"})

    assert response.status_code == 422


def test_list_tasks_filter_by_assignee_exact_case_insensitive_match(client):
    create_filter_task(client, "Ada task", assignee="Ada")
    create_filter_task(client, "Grace task", assignee="Grace")

    response = client.get("/tasks", params={"assignee": "ada"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Ada task"
    assert body[0]["assignee"] == "Ada"


def test_list_tasks_filter_by_assignee_does_not_substring_match(client):
    create_filter_task(client, "Ada task", assignee="Ada Lovelace")

    response = client.get("/tasks", params={"assignee": "Ada"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_unknown_assignee_returns_empty_list(client):
    create_filter_task(client, "Ada task", assignee="Ada")

    response = client.get("/tasks", params={"assignee": "Grace"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_empty_assignee_returns_unfiltered_list(client):
    create_filter_task(client, "Assigned task", assignee="Ada")
    create_filter_task(client, "Unassigned task")

    response = client.get("/tasks", params={"assignee": "   "})

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Assigned task", "Unassigned task"]


def test_list_tasks_no_params_returns_full_unfiltered_list(client):
    first = create_filter_task(client, "First task")
    second = create_filter_task(client, "Second task")

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == [first, second]


def test_list_tasks_combines_all_filters_with_and_logic(client):
    create_filter_task(
        client,
        "Write search tests",
        description="Backend filter coverage",
        status="InProgress",
        priority="High",
        assignee="Ada",
    )
    create_filter_task(
        client,
        "Write search docs",
        description="Backend filter coverage",
        status="InProgress",
        priority="Low",
        assignee="Ada",
    )
    create_filter_task(
        client,
        "Write search tests",
        description="Frontend filter coverage",
        status="ToDo",
        priority="High",
        assignee="Ada",
    )

    response = client.get(
        "/tasks",
        params={
            "q": "search",
            "status": "InProgress",
            "priority": "High",
            "assignee": "ada",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Write search tests"
    assert body[0]["priority"] == "High"


def test_list_tasks_combined_filters_no_match_returns_empty_list(client):
    create_filter_task(
        client,
        "Write search tests",
        status="InProgress",
        priority="High",
        assignee="Ada",
    )

    response = client.get(
        "/tasks",
        params={
            "q": "search",
            "status": "InProgress",
            "priority": "Low",
            "assignee": "ada",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_combined_filters_invalid_status_returns_422(client):
    create_filter_task(client, "Write search tests", assignee="Ada")

    response = client.get(
        "/tasks",
        params={
            "q": "missing",
            "status": "Blocked",
            "priority": "High",
            "assignee": "Nobody",
        },
    )

    assert response.status_code == 422


def test_list_tasks_combined_filters_invalid_priority_returns_422(client):
    create_filter_task(client, "Write search tests", assignee="Ada")

    response = client.get(
        "/tasks",
        params={
            "q": "missing",
            "status": "ToDo",
            "priority": "Urgent",
            "assignee": "Nobody",
        },
    )

    assert response.status_code == 422


def test_list_tasks_combines_search_assignee_and_overdue(client):
    past_due = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    future_due = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    create_filter_task(
        client,
        "Renew certificate",
        description="Security maintenance",
        assignee="Ada",
        due_date=past_due,
    )
    create_filter_task(
        client,
        "Renew docs",
        description="Security maintenance",
        assignee="Ada",
        due_date=future_due,
    )
    create_filter_task(
        client,
        "Renew certificate",
        description="Security maintenance",
        assignee="Grace",
        due_date=past_due,
    )

    response = client.get(
        "/tasks",
        params={"q": "security", "assignee": "ADA", "overdue": "true"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Renew certificate"
    assert body[0]["assignee"] == "Ada"
    assert body[0]["task_state"] == "overdue"


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={"priority": "Low"})

    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "bad priority", "priority": "Urgent"})

    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "extra field", "unknown": "value"})

    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    low_response = client.post("/tasks", json={"title": "low task", "priority": "Low"})
    high_response = client.post("/tasks", json={"title": "high task", "priority": "High"})
    assert low_response.status_code == 201
    assert high_response.status_code == 201

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "high task"
    assert body[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")

    assert response.status_code == 200
    assert response.json() == created_task


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    missing_id = "missing-task-id"

    response = client.get(f"/tasks/{missing_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Task with id {missing_id} not found"}


def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": "updated title"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created_task["id"]
    assert body["title"] == "updated title"
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]
    assert body["created_at"] == created_task["created_at"]


def test_patch_not_found_returns_404(client):
    missing_id = "missing-task-id"

    response = client.patch(f"/tasks/{missing_id}", json={"title": "updated"})

    assert response.status_code == 404
    assert response.json() == {"detail": f"Task with id {missing_id} not found"}


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "InProgress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "Done"},
    )

    assert response.status_code == 422
    assert "Invalid status transition from ToDo to Done" in response.json()["detail"]


def test_patch_same_status_allows_other_field_updates(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"status": "ToDo", "assignee": "Grace"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ToDo"
    assert body["assignee"] == "Grace"


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")

    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    missing_id = "missing-task-id"

    response = client.delete(f"/tasks/{missing_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": f"Task with id {missing_id} not found"}
