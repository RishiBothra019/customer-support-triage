#!/usr/bin/env python3
import os
import json
import requests
from openai import OpenAI
from typing import Dict, Any, List

ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
if not API_KEY:
    raise ValueError("Missing API key: set OPENAI_API_KEY or HF_TOKEN")

TASKS = ["easy", "medium", "hard"]
MAX_STEPS = 2
TEMPERATURE = 0.7

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: str | None):
    err_str = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err_str}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

SYSTEM_PROMPT_STEP1 = """You are a customer support agent. Given a ticket, you must classify it into one category and one priority.
Categories: billing, technical, feature_request, complaint, other.
Priorities: high, medium, low.
Reply with a JSON object: {"category": "...", "priority": "..."}."""

SYSTEM_PROMPT_STEP2 = """You are a customer support agent. Write a short, helpful response to the user's ticket.
Keep it polite, concise, and address the core issue. Do not include extra commentary."""

def get_step1_action(ticket_text: str) -> Dict[str, str]:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_STEP1},
            {"role": "user", "content": f"Ticket:\n{ticket_text}\n\nOutput JSON with category and priority."}
        ],
        temperature=TEMPERATURE,
        max_tokens=100,
    )
    content = response.choices[0].message.content.strip()
    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        data = json.loads(content)
        return {"category": data.get("category", "other"), "priority": data.get("priority", "medium")}
    except:
        return {"category": "other", "priority": "medium"}

def get_step2_response(ticket_text: str, feedback: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_STEP2},
            {"role": "user", "content": f"Ticket:\n{ticket_text}\n\nPrevious feedback: {feedback}\n\nWrite your response."}
        ],
        temperature=TEMPERATURE,
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()

def run_episode(task_name: str) -> tuple[bool, int, float, List[float]]:
    resp = requests.post(f"{ENV_URL}/reset", json={"task": task_name})
    resp.raise_for_status()
    obs = resp.json()
    ticket_text = obs["ticket_text"]
    rewards = []
    steps_taken = 0
    done = False
    error = None

    # Step 1
    action1 = get_step1_action(ticket_text)
    step1_action = {"category": action1["category"], "priority": action1["priority"]}
    step_resp = requests.post(f"{ENV_URL}/step", json={"action": step1_action})
    step_resp.raise_for_status()
    data = step_resp.json()
    reward = data["reward"]
    done = data["done"]
    rewards.append(reward)
    steps_taken += 1
    log_step(step=1, action=json.dumps(step1_action), reward=reward, done=done, error=error)

    if not done:
        obs = data["observation"]
        feedback = obs["feedback"]
        response_text = get_step2_response(ticket_text, feedback)
        step2_action = {"response": response_text}
        step_resp = requests.post(f"{ENV_URL}/step", json={"action": step2_action})
        step_resp.raise_for_status()
        data = step_resp.json()
        reward = data["reward"]
        done = data["done"]
        rewards.append(reward)
        steps_taken += 1
        log_step(step=2, action=response_text[:80], reward=reward, done=done, error=error)

    final_score = data.get("info", {}).get("final_score", 0.0)
    success = final_score >= 0.5
    return success, steps_taken, final_score, rewards

def main():
    for task in TASKS:
        log_start(task=task, env="customer_support_triage", model=MODEL_NAME)
        try:
            success, steps, score, rewards = run_episode(task)
        except Exception as e:
            log_end(success=False, steps=0, score=0.0, rewards=[])
            raise
        log_end(success=success, steps=steps, score=score, rewards=rewards)

if __name__ == "__main__":
    main()
