# Reflection

Across both features, I used three AI tools with distinct roles. ChatGPT drafted
initial user stories and acceptance criteria, which I reviewed and edited myself
before treating them as final — for example, tightening Story 3 in Feature 1 so
completed tasks are explicitly marked as completed rather than just not flagged
as overdue. Claude turned those confirmed user stories into structured,
constrained implementation prompts, including plan-first instructions and
explicit scope boundaries, and was also used to reason through smaller design
decisions before they became prompts, such as whether the assignee filter in
Feature 2 should be free text or a dropdown. GitHub Copilot, in VS Code agent
mode, generated the actual backend and frontend code for both features.

**Where AI helped most** was Feature 1's backend implementation. With clear
context and constraints in the prompt, Copilot's plan correctly proposed
computing overdue status at request time instead of storing it, which meant the
"no longer overdue after date change" requirement was satisfied automatically
rather than needing extra logic to keep a stored field in sync. All tests
passed without rework.

**Where AI slowed me down** was an early prompt in Feature 1 that simply said
to implement the plan "without changing the older code." That instruction was
too vague for Copilot to act on reliably — it wasn't clear whether it meant not
touching existing files at all, not changing behavior, or not refactoring while
editing shared code. I had to stop, rewrite it as an explicit additive-only
constraint (no changes to existing endpoint behavior, no refactoring while
editing shared files, stop and ask before breaking an existing test), and
re-send it before implementation could proceed cleanly. The rework cost time
that a more precise first prompt would have avoided.

**Where my review changed the result** was a business-logic bug in Feature 1:
when a task's status was changed from Done back to InProgress, the "Completed"
indicator stayed visible instead of clearing, because the indicator wasn't being
re-derived correctly after the status change. I asked the AI to diagnose the
root cause and propose a fix plan before touching any code, reviewed the
diagnosis, and only then approved the implementation. Without that check, the
app would have shipped with a misleading indicator on any task moved out of Done.

Working across two features reinforced that the plan-first, constraint-first
workflow keeps AI output scoped and easy to review, and that manual
verification — pytest plus manual browser testing — is still necessary to
catch logic bugs that automated tests and AI-generated plans don't always
surface on their own.