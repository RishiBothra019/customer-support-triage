---
title: "Customer Support Triage Environment"
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
app_file: server.py
---

# Customer Support Ticket Triage - OpenEnv Environment

[![Hugging Face Space](https://img.shields.io/badge/🤗-Space-blue)](https://huggingface.co/spaces/rishibothra/customer-support-triage)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-green)](https://github.com/openenv)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents
- [Environment Description](#environment-description)
- [Real-World Application](#real-world-application)
- [Task Difficulty Levels](#task-difficulty-levels)
- [Action Space](#action-space)
- [Observation Space](#observation-space)
- [Reward Function](#reward-function)
- [Grader Logic](#grader-logic)
- [Setup Instructions](#setup-instructions)
- [Usage Examples](#usage-examples)
- [Baseline Scores](#baseline-scores)
- [Validation](#validation)
- [Deployment](#deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Citation](#citation)

## 🎯 Environment Description

This environment simulates a **real-world customer support ticket triage system** where an AI agent acts as a support agent. The agent must:

1. **Classify** incoming customer tickets by category and priority
2. **Respond** with appropriate, helpful messages

The environment is designed for training and evaluating AI agents on practical customer service skills that humans perform daily in support roles.

### Why This Matters
- Customer support agents handle millions of tickets daily
- Proper triage reduces response time by 40-60%
- Automated triage saves companies $15-30B annually
- This environment bridges the gap between game-like tasks and real business applications

## 💼 Real-World Application

In actual customer support workflows, agents must:
- **Quickly categorize** issues (billing, technical, feature requests, complaints)
- **Prioritize** based on urgency and impact
- **Craft responses** that address customer needs while following company guidelines

This environment captures all three aspects with progressive difficulty levels.

## 🎮 Task Difficulty Levels

| Task | Difficulty | Description | Expected Category | Expected Priority | Response Keywords | Success Threshold |
|------|------------|-------------|-------------------|-------------------|-------------------|-------------------|
| **Easy** | ⭐ | Clear billing overcharge with explicit refund request | `billing` | `high` | refund, duplicate, credit, apologiz | ≥ 0.7 |
| **Medium** | ⭐⭐ | Vague performance complaint requiring diagnosis | `technical` | `medium` | slow, performance, investigat, check, server | ≥ 0.6 |
| **Hard** | ⭐⭐⭐ | Long, nuanced feature request with minor bug mention | `feature_request` | `low` | csv, export, suggest, consider, feedback, roadmap | ≥ 0.5 |

### Task Details

#### Easy Task: Billing Overcharge
**Ticket Text:** 
> "I was charged $49.99 twice for my monthly subscription. Please refund the duplicate charge immediately."

**Success Criteria:** 
- Correct category (`billing`) and priority (`high`)
- Response mentions refund, duplicate charge, or credit

#### Medium Task: Performance Complaint
**Ticket Text:**
> "Your app has become extremely slow lately. It takes forever to load my dashboard. Is something wrong with your servers?"

**Success Criteria:**
- Correct category (`technical`) and priority (`medium`)
- Response acknowledges performance issues and suggests investigation

#### Hard Task: Feature Request
**Ticket Text:**
> "I have been using your product for two years. The UI is great but I really need the ability to export data to CSV. I know you said it's not a priority, but many users ask for it. Also, the search filter sometimes resets – that's minor. Please consider adding CSV export. Thanks."

**Success Criteria:**
- Correct category (`feature_request`) and priority (`low`)
- Response acknowledges the feature request positively

## 🎬 Action Space

The agent takes actions as a JSON object with the following schema:

```json
{
  "category": "billing | technical | feature_request | complaint | other",
  "priority": "high | medium | low",
  "response": "string (free text, 3+ characters)"
}
{
  "category": "billing|technical|feature_request|complaint|other",
  "priority": "high|medium|low",
  "response": "string (free text)"
}
customer-support-triage/
├── .github/
│   └── workflows/
│       └── validate.yml          # GitHub Action to auto-validate on push
├── src/
│   ├── __init__.py
│   ├── env/
│   │   ├── __init__.py
│   │   ├── my_env_v4.py
│   │   └── openenv.yaml
│   └── server/
│       ├── __init__.py
│       └── server.py
├── scripts/
│   ├── validate-submission.sh    # Validator script
│   ├── local_test.sh              # Quick local test script
│   └── run_inference.sh           # Wrapper for inference.py
├── tests/
│   ├── __init__.py
│   ├── test_env.py                # Unit tests for environment
│   └── test_server.py             # Unit tests for API
├── inference.py                    # Baseline inference script (root)
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt            # Dev dependencies
├── README.md
├── .gitignore
├── .env.example                    # Environment variables template
├── docker-compose.yml              # For local development
├── Makefile                        # Common commands shortcut
└── LICENSE                         # MIT or Apache-2.0
