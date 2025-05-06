from pydantic import BaseModel
from textwrap import dedent
import os
from agents import Agent, RunContextWrapper, GuardrailFunctionOutput, Runner, TResponseInputItem, input_guardrail
from agents.extensions.models.litellm_model import LitellmModel


class TopicCheckOutput(BaseModel):
    is_relevant: bool
    reasoning: str


guardrail_agent = Agent(
    name="Topic Check Guardrail",
    instructions=dedent(
        """
        You are an assistant that determines if user queries are relevant to either:
        1. Public transport (buses, trains, schedules, routes, etc.)
        2. Calendar appointments and scheduling
        3. Looking for a restaurant or a place to eat

        ONLY respond with a properly formatted JSON object with the following structure:
        {
            "is_relevant": true/false,
            "reasoning": "Your explanation here"
        }

        Set "is_relevant" to true ONLY if the query clearly relates to one or more of the topics.
        Provide brief reasoning for your decision in the "reasoning" field.

        IMPORTANT: Always respond with valid JSON format that can be parsed. Do not include any text before or after the JSON object.
        """
    ),
    model=LitellmModel(model="ollama/llama3.1", api_key=os.getenv("OPENROUTER_API_KEY")),
    output_type=TopicCheckOutput,
)


@input_guardrail
async def topic_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    result = result.final_output

    return GuardrailFunctionOutput(
        output_info=result.reasoning,
        tripwire_triggered=not result.is_relevant,
    )


OFF_TOPIC_MESSAGE = (
    "I'm specifically designed to help with public transport options and calendar appointments. "
    "Please ask me something related to these topics."
)
