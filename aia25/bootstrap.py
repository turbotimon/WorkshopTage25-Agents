import logging
from os import getenv

import mlflow
from agents import set_default_openai_api, set_default_openai_client
from openai import AsyncOpenAI

logging.getLogger("openai.agents").setLevel(logging.CRITICAL)

custom_client = AsyncOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"), base_url=getenv("BASE_URL")
)
set_default_openai_client(custom_client)
set_default_openai_api("chat_completions")

# Enable auto tracing for OpenAI Agents SDK
mlflow.openai.autolog()

# Optional: Set a tracking URI and an experiment
mlflow.set_tracking_uri("http://localhost:5000")