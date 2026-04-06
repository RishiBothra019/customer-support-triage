import re
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

# ------------------------------------------------------------------
# Typed OpenEnv models
# ------------------------------------------------------------------
class Category(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    FEATURE_REQUEST = "feature_request"
    COMPLAINT = "complaint"
    OTHER = "other"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Action(BaseModel):
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    response: Optional[str] = None

class Observation(BaseModel):
    ticket_text: str
    step: int
    last_action_valid: bool
    feedback: str
    current_reward_so_far: float
    done: bool

class Reward(BaseModel):
    value: float

# ------------------------------------------------------------------
# Task definitions (gold standards and graders)
# ------------------------------------------------------------------
class Task:
    def __init__(self, task_id: str, description: str, ticket_text: str,
                 expected_category: Category, expected_priority: Priority,
                 response_keywords: List[str]):
        self.id = task_id
        self.description = description
        self.ticket_text = ticket_text
        self.expected_category = expected_category
        self.expected_priority = expected_priority
        self.response_keywords = [kw.lower() for kw in response_keywords]

TASKS = {
    "easy": Task(
        task_id="easy",
        description="Clear billing overcharge – agent must categorise as billing, high priority, and mention refund.",
        ticket_text="I was charged $49.99 twice for my monthly subscription. Please refund the duplicate charge immediately.",
        expected_category=Category.BILLING,
        expected_priority=Priority.HIGH,
        response_keywords=["refund", "duplicate", "credit", "apologiz"]
    ),
    "medium": Task(
        task_id="medium",
        description="Vague performance complaint – could be technical or general. Expected: technical, medium priority, suggest performance check.",
        ticket_text="Your app has become extremely slow lately. It takes forever to load my dashboard. Is something wrong with your servers?",
        expected_category=Category.TECHNICAL,
        expected_priority=Priority.MEDIUM,
        response_keywords=["slow", "performance", "investigat", "check", "server"]
    ),
    "hard": Task(
        task_id="hard",
        description="Long, contradictory feature request. Expected: feature_request, low priority, acknowledge suggestion.",
        ticket_text="""I have been using your product for two years. The UI is great but I really need the ability to export data to CSV. 
        I know you said it's not a priority, but many users ask for it. Also, the search filter sometimes resets – that's minor. 
        Please consider adding CSV export. Thanks.""",
        expected_category=Category.FEATURE_REQUEST,
        expected_priority=Priority.LOW,
        response_keywords=["csv", "export", "suggest", "consider", "feedback", "roadmap"]
    )
}

# ------------------------------------------------------------------
# Environment class
# ------------------------------------------------------------------
class MyEnvV4Env:
    def __init__(self):
        self.task: Optional[Task] = None
        self.step: int = 1
        self.actions: List[Action] = []
        self.rewards: List[float] = []
        self.done: bool = False
        self.last_action_valid: bool = True
        self.feedback: str = ""

    def reset(self, task_id: str = "easy") -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Unknown task: {task_id}. Choose from {list(TASKS.keys())}")
        self.task = TASKS[task_id]
        self.step = 1
        self.actions = []
        self.rewards = []
        self.done = False
        self.last_action_valid = True
        self.feedback = "New ticket. Step 1: choose category and priority."
        return self._get_observation()

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict]:
        if self.done:
            raise RuntimeError("Episode already finished. Call reset().")

        if self.step == 1:
            if action.category is None or action.priority is None:
                self.last_action_valid = False
                self.feedback = "Step 1 requires both 'category' and 'priority'."
                reward_val = -0.1
            else:
                self.last_action_valid = True
                cat_match = (action.category == self.task.expected_category)
                prio_match = (action.priority == self.task.expected_priority)
                reward_val = (0.25 if cat_match else 0.0) + (0.25 if prio_match else 0.0)
                self.feedback = f"Category {'✓' if cat_match else '✗'}, Priority {'✓' if prio_match else '✗'}. "
                if cat_match and prio_match:
                    self.feedback += "Good start! Now provide a response (step 2)."
                else:
                    self.feedback += "Not perfect – try to improve in next step."
            self.actions.append(action)
            self.rewards.append(reward_val)
            self.step = 2

        elif self.step == 2:
            if action.response is None or len(action.response.strip()) < 3:
                self.last_action_valid = False
                self.feedback = "Step 2 requires a non‑empty response (at least 3 characters)."
                reward_val = -0.1
            else:
                self.last_action_valid = True
                response_lower = action.response.lower()
                matches = sum(1 for kw in self.task.response_keywords if kw in response_lower)
                match_ratio = min(1.0, matches / len(self.task.response_keywords))
                reward_val = 0.5 * match_ratio
                self.feedback = f"Response matched {matches}/{len(self.task.response_keywords)} keywords."
            self.actions.append(action)
            self.rewards.append(reward_val)
            self.done = True
            self.feedback += " Episode finished."

        else:
            raise RuntimeError(f"Invalid step number: {self.step}")

        total_reward = sum(self.rewards)
        obs = self._get_observation()
        reward_obj = Reward(value=reward_val)
        info = {"final_score": self._compute_final_score()} if self.done else {}
        return obs, reward_obj, self.done, info

    def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.task.id if self.task else None,
            "step": self.step,
            "actions": [a.dict() for a in self.actions],
            "rewards": self.rewards,
            "done": self.done,
            "last_action_valid": self.last_action_valid,
            "feedback": self.feedback
        }

    def _get_observation(self) -> Observation:
        return Observation(
            ticket_text=self.task.ticket_text if self.task else "",
            step=self.step,
            last_action_valid=self.last_action_valid,
            feedback=self.feedback,
            current_reward_so_far=sum(self.rewards),
            done=self.done
        )

    def _compute_final_score(self) -> float:
        if len(self.actions) < 2:
            return 0.0
        act1 = self.actions[0]
        act2 = self.actions[1]
        cat_score = 0.25 if act1.category == self.task.expected_category else 0.0
        prio_score = 0.25 if act1.priority == self.task.expected_priority else 0.0
        if act2.response:
            resp_lower = act2.response.lower()
            matches = sum(1 for kw in self.task.response_keywords if kw in resp_lower)
            resp_score = 0.5 * min(1.0, matches / len(self.task.response_keywords))
        else:
            resp_score = 0.0
        return cat_score + prio_score + resp_score

    async def close(self):
        pass

    @classmethod
    async def from_docker_image(cls, image_name: str):
        return cls()
