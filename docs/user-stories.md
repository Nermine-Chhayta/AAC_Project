Feature 1: Due dates + overdue filter
user stories:
Story 1

As a team member, I want to assign a due date when creating a task so that I know when the task should be completed.

Acceptance Criteria:

* A due date is optional when creating a task.
* If provided, the due date is saved with the task.
* The task list displays the due date for tasks that have one.
* An invalid date format returns HTTP 422.

Story 2

As a team member, I want to update a task's due date so that I can keep deadlines accurate as plans change.

Acceptance Criteria:

* A task's due date can be added, changed, or removed.
* A valid updated due date is saved successfully.
* The updated due date is reflected in the task list.
* An invalid date format returns HTTP 422.

Story 3

As a team member, I want overdue and completed tasks to be clearly identified so that I can easily distinguish tasks that require attention from those that have already been finished.

Acceptance Criteria:

* A task is marked as overdue when its due date has passed and its status is not Done.
* Tasks without a due date are never marked as overdue.
* A task is no longer marked as overdue if its due date is updated to a future date.
* Tasks with status Done display a completed indicator instead of an overdue indicator, even if the due date has passed.

Story 4

As a team member, I want to filter tasks by overdue status so that I can focus only on tasks that require urgent action.

Acceptance Criteria:

* An overdue filter returns only tasks whose due dates have passed.
* Tasks without a due date are excluded from the overdue filter.
* Tasks that are not overdue are excluded from the filtered results.
* If no overdue tasks exist, the filter returns an empty list.

Story 5

As a team member, I want to view due dates on task cards so that I can easily track upcoming deadlines.

Acceptance Criteria:

* Tasks with a due date display the due date on their card.
* Tasks without a due date do not display a due date field.
* Overdue tasks display a visible overdue indicator.
* Changes to a task's due date are reflected immediately after the task is updated.

edits: chatgpt was prompted to edit story 3 to make it clearer that completed tasks are marked as completed

######

Feature 2: Search + combined filters
user stories:
story 1

As a team member, I want to search tasks by keyword so that I can quickly find a specific task by its title or description.

Acceptance Criteria:

* Searching matches text within the task title or description.
* A search with no matching tasks returns HTTP 200 with an empty list.
* Search results are displayed above the board without hiding the column layout.

Story 2

As a team member, I want to filter tasks by status so that I can view only the tasks in a stage I care about.

Acceptance Criteria:

* Selecting a status filter returns only tasks matching that status.
* Applying a status filter with no matching tasks returns HTTP 200 with an empty list.
* Columns remain visible with their empty states when a filter yields no results.

Story 3

As a team member, I want to filter tasks by priority so that I can focus on high-priority work first.

Acceptance Criteria:
* Selecting a priority filter returns only tasks matching that priority.
* Submitting an invalid priority value returns HTTP 422.
* The filter bar clearly indicates which priority is currently active.

Story 4

As a team member, I want to combine search with status and priority filters so that I can narrow results to exactly what I need.

Acceptance Criteria:

* Combined filters are applied using AND logic (all conditions must match).
* A combination with no matching tasks returns HTTP 200 with an empty list.
* An invalid value in any combined filter returns HTTP 422.

Story 5 

As a team member, I want to clear all active search and filter criteria so that I can 
quickly return to viewing the full task board.

Acceptance Criteria:

* Clearing filters removes all applied search and filter parameters.
* After clearing, all tasks are displayed across their respective columns.
* The filter/search bar resets to its default, empty state.

edits: asked chatGpt to add a story about filtering by asignee
Story 6

* A dropdown lists distinct assignees, populated from the full (unfiltered) task
  list, not the currently filtered view.
* Selecting an assignee filters the board to that assignee (exact match, backend
  already case-insensitive).
* No matches → columns remain visible with empty states.
* A "no filter" / blank default option is available and means no assignee filter is applied.
* Combines with search/status/priority using AND logic.