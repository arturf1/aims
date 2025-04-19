
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100

def create_data_analyst_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        "DataAnalystAgent",
        description="An agent for performing calculations.",
        model_client=model_client,
        tools=[percentage_change_tool],
        handoffs=["PlanningAgent"],
        system_message="""
        You are a data analyst.
        Given the tasks you have been assigned, you should analyze the data.
        Your only tool is percentage_change_tool - use it for data analysis.
        You make only one search call at a time.
        If you don't see data or task is complete, always handoff back to PlanningAgent by doing a function call.
        """,
    ) 
