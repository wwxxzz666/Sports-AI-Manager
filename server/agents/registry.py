from agents.base import BaseAgent
from agents.find_game import FindGameAgent
from agents.workout_checkin import WorkoutCheckinAgent
from agents.find_coach import FindCoachAgent
from agents.motion_analysis import MotionAnalysisAgent
from agents.ai_rating import AIRatingAgent
from agents.go_out_prep import GoOutPrepAgent
from agents.rehab_coach import RehabCoachAgent
from agents.food_calories import FoodCaloriesAgent
from agents.user_profile import UserProfileAgent
from agents.weekly_report import WeeklyReportAgent
from agents.leave_replacement import LeaveReplacementAgent

# Agent registry
_AGENT_MAP: dict[str, type[BaseAgent]] = {
    "find-game": FindGameAgent,
    "workout-checkin": WorkoutCheckinAgent,
    "find-coach": FindCoachAgent,
    "motion-analysis": MotionAnalysisAgent,
    "ai-rating": AIRatingAgent,
    "go-out-prep": GoOutPrepAgent,
    "rehab-coach": RehabCoachAgent,
    "food-calories": FoodCaloriesAgent,
    "user-profile": UserProfileAgent,
    "weekly-report": WeeklyReportAgent,
    "leave-replacement": LeaveReplacementAgent,
}

# Singleton instances
_agent_instances: dict[str, BaseAgent] = {}


def get_agent(agent_type: str) -> BaseAgent | None:
    """Get an agent instance by type."""
    if agent_type not in _agent_instances:
        agent_class = _AGENT_MAP.get(agent_type)
        if agent_class:
            _agent_instances[agent_type] = agent_class()
    return _agent_instances.get(agent_type)


def list_agents() -> list[dict]:
    """List all available agents."""
    return [
        {
            "id": agent_cls.agent_type,
            "name": agent_cls.display_name,
            "description": agent_cls.description,
            "group": agent_cls.group,
            "icon": agent_cls.icon,
        }
        for agent_cls in _AGENT_MAP.values()
    ]
