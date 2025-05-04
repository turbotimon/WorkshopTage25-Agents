from pydantic import BaseModel


class GlobalContext(BaseModel):
    """
    Global context for our multi-agent system.
    This context is shared across all agents and can be used to store
    information that needs to be accessed by multiple agents.
    """

    current_time: str = ""
