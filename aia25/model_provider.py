import os
from agents import (
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
)
from openai import AsyncOpenAI


client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))


class OpenRouterModelProvider(ModelProvider):
    def get_model(self, model_name: str | None = None) -> Model:
        return OpenAIChatCompletionsModel(
            model=os.getenv("AGENT_MODEL"),
            openai_client=AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")
            ),
        )
