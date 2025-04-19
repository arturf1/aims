
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

def create_planner_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        "PlanningAgent",
        description="An agent for planning tasks.",
        model_client=model_client,
        handoffs=["WebSearchAgent","DataAnalystAgent", "ProgrammerAgent"],
        system_message="""
        You are a planning agent.
        Your job is to break down complex tasks into smaller, manageable subtasks and delegate them to specialized agents:
        - WebSearchAgent: Searches for information
        - DataAnalystAgent: Performs calculations
        - ProgrammerAgent: An agent capable of writing, saving, and executing Python code

        Always send your plan first in the following format, then alawys handoff to appropriate agent.
            1. <agent> : <task>
        Just write the plan. Do not do any of the tasks yourself. 
        Always handoff to a single agent at a time.
        Summarize results. 
        Use TERMINATE when all tasks are accomplished. Never TERMINATE in your first message. 
        """
    ) 
