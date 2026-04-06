FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY my_env_v4.py openenv.yaml server.py ./

ENV PORT=7860
EXPOSE $PORT

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
