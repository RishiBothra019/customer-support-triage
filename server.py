import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from my_env_v4 import MyEnvV4Env, Action, Observation, Reward, TASKS

app = FastAPI(title="Customer Support Triage Environment")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

env = MyEnvV4Env()

class ResetRequest(BaseModel):
    task: str = "easy"

class StepRequest(BaseModel):
    action: Dict[str, Any]

class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any]

@app.get("/")
def root():
    return {"status": "Customer Support Triage Environment is running"}

@app.post("/reset")
def reset(req: ResetRequest = None):
    # Handle empty body or missing task by defaulting to "easy"
    task = "easy"
    if req and req.task:
        task = req.task
    if task not in TASKS:
        raise HTTPException(400, f"Unknown task. Choose from {list(TASKS.keys())}")
    obs = env.reset(task)
    return obs.dict()

@app.post("/step")
def step(req: StepRequest):
    try:
        action = Action(**req.action)
    except Exception as e:
        raise HTTPException(400, f"Invalid action: {str(e)}")
    obs, reward, done, info = env.step(action)
    return StepResponse(
        observation=obs.dict(),
        reward=reward.value,
        done=done,
        info=info
    )

@app.get("/state")
def get_state():
    return env.state()

@app.get("/tasks")
def list_tasks():
    return {"tasks": list(TASKS.keys()), "details": {k: v.description for k, v in TASKS.items()}}
