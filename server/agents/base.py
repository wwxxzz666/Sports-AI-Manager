from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    agent_type: str = ""
    display_name: str = ""
    description: str = ""
    group: str = ""
    icon: str = ""

    @abstractmethod
    async def handle(self, message: str, attachments: list[str] = None) -> dict:
        """Handle a user message and return a response.

        Returns:
            dict with keys:
            - reply: str (natural language response)
            - structured: dict | None (structured data)
        """
        pass
