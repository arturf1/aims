
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

# Note: This example uses mock tools instead of real APIs for demonstration purposes
def search_web_tool(query: str) -> str:
    result = ""
    if "2006-2007" in query:
        result += """Here are the total points scored by Miami Heat players in the 2006-2007 season:
        Udonis Haslem: 844 points
        Dwayne Wade: 1397 points
        James Posey: 550 points
        ...
        """
    if "2007-2008" in query:
        result += "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    if "2008-2009" in query:
        result += "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    if result == "":
        result += "No data found."
    return result


def create_web_search_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    return AssistantAgent(
        "WebSearchAgent",
        description="An agent for searching information on the web.",
        tools=[search_web_tool],
        model_client=model_client,
        handoffs=["PlanningAgent"],
        system_message="""
        You are a web search agent.
        Your only tool is search_web_tool - use it to find information.
        You make only one search call at a time.
        Once you have the results, you never do calculations based on them.
        Always handoff back to PlanningAgent after your search call is complete.
        """,
    )
