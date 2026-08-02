# My AI Coding Playbook

This document captures how I use AI for the course final project, and how I maintain ownership of the work.

## AI Ownership
- I use AI as an assistant, not as the final decision-maker.
- I write prompts, select outputs, and validate every result.
- I own the code, tests, documentation, and final submission evidence.
- I never let AI change app logic without manual verification.
- Evidence: I ran `python -m pytest -q`, verified `/health`, built and ran the Docker image, and updated release and AI review documentation.

## 1. When I reach for AI first
- planning a feature or task
- writing user stories and business rules
- drafting documentation and workflow text
- suggesting CI and Docker configuration

## 2. When I do not reach for AI
- manual checking and testing
- reviewing code for correctness
- personal reflection and ownership decisions

## 3. My non-negotiables
- I lead AI.
- Context is required before asking.
- Good prompts produce better output.

## 4. My review rules
- Confirm generated answers match the app requirements.
- Verify tests actually run and pass.
- Check AI claims for correctness before accepting them.

## 5. What I am still figuring out
- What AI can safely automate versus what I must verify.
- How to keep prompts precise and minimal.
- How to capture AI use while preserving ownership.

---

## Decision Card
- New feature planning: ChatGPT
- Code review: Cursor
- Debugging: Copilot
- Infrastructure: Claude code CLI
- Never paste credentials into AI tools.
- I own my code and my logic.
