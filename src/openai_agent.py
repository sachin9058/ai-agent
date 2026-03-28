try:
    from agent_toolset import ConstructionAdvisorToolset
except ImportError:
    from .agent_toolset import ConstructionAdvisorToolset


def create_agent():
    """Create OpenAI agent and its tools"""
    toolset = ConstructionAdvisorToolset()
    tools = toolset.get_tools()

    return {
        'tools': tools,
        'system_prompt': """You are a Smart Construction Advisor AI.

Your job is to:
- Analyze construction queries
- Estimate realistic costs
- Suggest materials
- Identify risks
- Provide practical advice

Always respond clearly and in structured format.
""",
    }