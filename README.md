# Customer Support Ticket Triage – OpenEnv Environment

A real‑world environment where an AI agent learns to classify and respond to customer support tickets.  
Built to the **OpenEnv** specification, with three difficulty levels (easy, medium, hard), partial rewards, and programmatic graders.

## Environment Description

The agent receives a customer support ticket (text). In **Step 1** it must choose a **category** (`billing`, `technical`, `feature_request`, `complaint`, `other`) and a **priority** (`high`, `medium`, `low`). In **Step 2** it writes a short response.  
Rewards are given after each step:
- Step 1: up to 0.5 (0.25 for correct category, 0.25 for correct priority)
- Step 2: up to 0.5 based on keyword matches in the response

Invalid actions (e.g., missing fields) receive a small penalty (-0.1).  
The final score (0.0–1.0) is computed by a deterministic grader that compares the agent’s actions against the gold standard for each task.

## Action & Observation Spaces

### Action
```json
{
  "category": "billing|technical|feature_request|complaint|other",
  "priority": "high|medium|low",
  "response": "string (free text)"
}
