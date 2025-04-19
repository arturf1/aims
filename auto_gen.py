import asyncio
from dotenv import load_dotenv
import os
import subprocess

# Load environment variables from .env file
load_dotenv()

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import ExternalTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient


async def write_code_to_file(filename: str, code: str) -> str:
    """
    Writes Python code to a file in the 'coding_output' directory.

    Args:
        filename (str): The name of the file to write to (e.g., 'my_script.py').
        code (str): The Python code to write.

    Returns:
        str: A message indicating success or failure.
    """
    try:
        # Ensure the directory exists
        os.makedirs("coding_output", exist_ok=True)
        filepath = os.path.join("coding_output", filename)
        with open(filepath, "w") as f:
            f.write(code)
        return f"Successfully wrote code to {filename}"
    except Exception as e:
        return f"Error writing to file: {e}"

async def execute_python_code(filename: str) -> str:
    """
    Executes a Python script located in the 'coding_output' directory.

    Args:
        filename (str): The name of the Python script to execute.

    Returns:
        str: The output of the script, or an error message if execution fails.
    """
    try:
        filepath = os.path.join("coding_output", filename)
        # Use subprocess.run for better control and error handling
        process = subprocess.run(["python", filepath], capture_output=True, text=True, check=True)
        return process.stdout.strip()  # Return only the output, stripped of extra whitespace
    except subprocess.CalledProcessError as e:
        return f"Error executing code: {e.stderr.strip()}"  # Return the error message from stderr
    except FileNotFoundError:
        return f"Error: File not found - {filename}.  Please ensure the file exists in the coding_output directory."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# Create an OpenAI model client.
# model_client = OpenAIChatCompletionClient(
#     model="gpt-3.5-turbo",
#     api_key=os.getenv("OPENAI_API_KEY"),  # Get API key from environment variable
# )
model_client = OpenAIChatCompletionClient(
    model="gemini-1.5-flash-8b",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Create the primary agent.
primary_agent = AssistantAgent(
    "primary",
    tools=[write_code_to_file, execute_python_code],
    model_client=model_client,
    system_message="You are a helpful AI assistant. Use tools to solve tasks.",
    reflect_on_tool_use=True,
)

# Create the critic agent.
critic_agent = AssistantAgent(
    "critic",
    model_client=model_client,
    system_message="You are a critic who always provide feedback.",
)

# Define a termination condition that stops the task if the critic approves.
text_termination = TextMentionTermination("APPROVE")

async def main():
    # Create a team with the primary and critic agents.
    print("Creating team...")
    team = RoundRobinGroupChat([primary_agent], termination_condition=text_termination, max_turns=1)
    print("Team created. Running task...")
    task=input("Write a test for the team:")
    while True:
        await Console(team.run_stream(task=task))
        # Get the user response.
        task = input("Enter your feedback (type 'exit' to leave): ")
        if task.lower().strip() == "exit":
            break

if __name__ == "__main__":
    print("Starting main...")
    asyncio.run(main())
