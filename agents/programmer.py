from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
import subprocess

def save_python_code(filename: str, code: str) -> str:
    """Saves the provided Python code to a file."""
    try:
        with open(filename, "w") as f:
            f.write(code)
        return f"Python code saved to '{filename}' successfully."
    except Exception as e:
        return f"Error saving Python code to '{filename}': {e}"

def execute_python_code(filename: str) -> str:
    """Executes the Python code in the specified file."""
    try:
        result = subprocess.run(["python", filename], capture_output=True, text=True, check=True)
        return f"Execution of '{filename}' successful:\nStdout:\n{result.stdout}\nStderr:\n{result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"Error executing '{filename}':\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}"
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"An unexpected error occurred during execution: {e}"

def create_programmer_agent(model_client: OpenAIChatCompletionClient) -> AssistantAgent:
    """Creates a programmer agent with tools to save and execute Python code."""
    return AssistantAgent(
        name="ProgrammerAgent",
        description="An agent capable of writing, saving, and executing Python code.",
        model_client=model_client,
        tools=[save_python_code, execute_python_code],
        handoffs=["PlanningAgent"],
        system_message="""
        You are a helpful programmer agent.
        You can write Python code to solve tasks.
        You have two primary tools:
        1. 'save_python_code(filename: str, code: str)': Saves the given Python code to the specified filename.
        2. 'execute_python_code(filename: str)': Executes the Python code in the specified file and returns the output.

        When you need to write and run Python code:
        1. First, carefully write the complete Python code to address the user's request.
        2. Use the 'save_python_code' tool to save the code to a file (e.g., 'temp_script.py').
        3. Use the 'execute_python_code' tool with the filename you used in the previous step to run the code.
        4. Report the output of the executed code to the user.

        Remember to consider potential errors and handle them gracefully in your code.
        Only execute code that is directly relevant to the user's request.
        Do not execute arbitrary or potentially harmful code.
        Always handoff back to PlanningAgent by doing a function call.
        Use TERMINATE when all tasks are accomplished.
        """,
    )