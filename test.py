import os
import asyncio
import json
from dotenv import load_dotenv
from autogen_agentchat.ui import Console
from autogen_agentchat.teams import Swarm, SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.planner import create_planner_agent
from agents.web_search import create_web_search_agent
from agents.data_analyst import create_data_analyst_agent
from agents.programmer import create_programmer_agent
from tools.result_analysis import analyze_result_messages

load_dotenv()

model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    api_key=os.getenv("GEMINI_API_KEY"),
    parallel_tool_calls=False,  # type: ignore
)

text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=25)
termination = text_mention_termination | max_messages_termination

planning_agent = create_planner_agent(model_client)
web_search_agent = create_web_search_agent(model_client)
data_analyst_agent = create_data_analyst_agent(model_client)
programmer_agent = create_programmer_agent(model_client)

team = Swarm(
    [programmer_agent],
    termination_condition=termination,
)

task = "Write and test a simple program which adds two numbers"

def save_messages_to_file(messages, filename="saved_messages.json"):
    with open(filename, "w") as f:
        print(analyze_result_messages(messages))
        json.dump(messages, f, indent=2, default=lambda o: o.dump())

async def run_team_stream() -> None:
    try:
        task_result = await Console(team.run_stream(task=task))
        save_messages_to_file(task_result.messages, filename="saved_messages.json")
    except Exception as e:
        print(f"An error occurred during Console execution: {e}")

asyncio.run(run_team_stream())