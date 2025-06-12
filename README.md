The MCP (Model Control Protocol) is a powerful hosting protocol designed to decouple AI Agents from the tools they use, enabling flexibility and modularity in AI-driven applications. By using an MCP Server, an AI Agent can dynamically discover and utilize tools to fulfill user requests. This article will guide you through creating your first MCP Server, registering a tool function, and configuring an AI Agent like Claude Desktop to interact with it. We’ll use Python and Anthropic’s mcp library to build a simple, general-purpose MCP Server.

If you’re not a Medium subscriber, click here to read the full article.


What is MCP?
MCP is a protocol that allows an AI Agent to communicate with a set of tools hosted on an MCP Server. When a user submits a query to the Agent, it retrieves available tools from the MCP Server, converts them into a format the AI model can understand, and sends them along with the user’s request. The AI model then decides which tool to call and returns a response that guides the Agent to execute the appropriate tool function. This decoupling ensures that both the Agent and the tools can be modified independently, enhancing flexibility and scalability.

Prerequisites
Before we begin, ensure you have the following:

Python 3.8+ installed.
A package manager like pip, Poetry, or UV (we’ll use UV in this guide).
An AI Agent application, such as Claude Desktop, for testing the MCP Server.
Basic familiarity with Python and JSON.
To create the McpAgent project by UV command:

uv init McpAgent
cd McpAgent
This creates a project structure optimized for Python development:

McpAgent/
├── .git/              # Git repository for version control
├── .gitignore         # Ignores files like .env and __pycache__
├── .python-version    # Specifies Python version (e.g., 3.12)
├── main.py            # Entry point for the application
├── pyproject.toml     # Project metadata and dependencies
├── README.md          # Project documentation
├── uv.lock            # Lock file for reproducible dependency versions
The uv tool ensures consistent dependency management and virtual environment creation, making the project portable across systems.

Step 1: Writing a Tool Function
Let’s start by creating a simple tool function that returns the current device’s system information. This function will serve as the tool our MCP Server hosts.

Here’s an example implementation of a tool function that retrieves system information: tools.py

import platform
import json

def get_host_info() -> str:
    """
    Retrieves system information about the current device.
    
    Returns:
        str: A JSON string containing system information such as CPU count and architecture.
    """
    system_info = {
        "os": platform.system(),
        "architecture": platform.machine(),
        "platform": platform.platform()
    }
    return json.dumps(system_info)

if __name__ == "__main__":
    print(get_host_info())
Key Points for Tool Functions
Clear Naming and Parameters: Use descriptive function names and parameters. For example, get_host_info clearly indicates its purpose.
Type Hints: Include type hints (e.g., -> str) to help the AI model understand the function’s input and output types.
Docstrings: If the function’s purpose isn’t immediately clear from its name, add a detailed docstring. The AI model can parse docstrings to better understand the tool’s functionality.
Return Format: The function should return a string (e.g., JSON) that the AI model can process. In this case, we use json.dumps to convert a dictionary into a JSON string.
You can test the function by running it using the uv command, which printing its output:

uv run tools.py
This might output something like:

{
  "os": "Darwin", 
  "architecture": "arm64", 
  "platform": "macOS-15.4.1-arm64-arm-64bit"
}
Step 2: Setting Up the MCP Server
Now, let’s create the MCP Server using Anthropic’s mcp library. The server will host the get_host_info tool and make it available to an AI Agent.

Install the MCP Library
First, install the mcp library. If you’re using UV, run:

uv add mcp
This updates the pyproject.toml file with the following configuration:

[project]
name = "mcpagent"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "mcp>=1.9.1",
]
Create the MCP Server
Here’s the code to set up a basic MCP Server: main.py

from mcp.server.fastmcp import FastMCP
import tools

# Create an MCP instance
mcp = FastMCP("System Info Service")

# Register the tool function
mcp.add_tool(tools.get_host_info)

# Start the MCP Server in stdio mode
def main() -> None:
  mcp.run("stdio")

if __name__ == "__main__":
    main()
Explanation
FastMCP: This is the main class from the mcp library. The constructor takes a service name (e.g., “system_info_service”). The name is arbitrary but should be descriptive.
add_tool: Registers the get_host_info function with the MCP Server. You can call add_tool multiple times to register additional tools.
run: Starts the MCP Server. The mode parameter specifies the communication mode:
stdio: Uses standard input/output for local communication. It’s simple but requires the Agent and Server to run on the same machine.
SSE: Uses Server-Sent Events over HTTP, suitable for cloud deployment but requires handling authentication and authorization.
For this guide, we’ll use stdio for simplicity.

Alternative: Using a Decorator
If the tool function is defined in the same file as the MCP Server, you can register it using a decorator: main.py

from mcp.server.fastmcp import FastMCP
import platform
import json

mcp = FastMCP("System Info Service")

@mcp.tool
def get_host_info() -> str:
    """
    Retrieves system information about the current device.
    
    Returns:
        str: A JSON string containing system information such as CPU count and architecture.
    """
    system_info = {
        "os": platform.system(),
        "architecture": platform.machine(),
        "platform": platform.platform()
    }
    return json.dumps(system_info)

mcp.run(mode="stdio")
The @mcp.tool decorator achieves the same result as mcp.add_tool(get_host_info).

Step 3: Configuring the AI Agent
To test the MCP Server, we’ll use Claude Desktop, a user-friendly AI Agent that supports MCP. The configuration process is similar for other Agents like Cline.


Steps to Configure Claude Desktop
Open Settings: In Claude Desktop, navigate to the settings menu.
Access Developer Settings: Click on “Developer” and then “Edit Config” to open the configuration file directory.

3. Edit the MCP Configuration File: Claude Desktop will open a directory containing its configuration files. Locate or create the MCP configuration file (e.g., claude_desktop_config.json).

4. Add the MCP Server Details: Specify the command to launch the MCP Server. Since we’re using UV, the configuration might look like this: mcp_config.json

{
  "mcpServers": {
    "hostInfoMcp": {
      "command": "/ABSOLUTE/PATH/TO/UV/uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/MCPAgent/FOLDER/",
        "run",
        "main.py"
      ]
    }
  }
}
⚠️ Important: Make sure the command points to the exact UV (e.g. “/Users/username/.local/bin/uv” in macOS). Also make sure to use the full absolute path to the script (e.g. “/Users/username/projects/McpAgent”).

name: Matches the name provided to the FastMCP constructor (“hostInfoMcp”).
command: Specifies how to run the MCP Server (e.g., uv run python main.py).
args: arguments of the command.
5. Save and Restart: Save the configuration file and restart Claude Desktop.

Step 4: Testing the MCP Server
Once configured, Claude Desktop should detect the MCP Server and its registered tools (e.g., hostInfoMcp). Follow these steps to test it:

Open Claude Desktop’s Chat Interface: You should see the “hostInforMcp” tool listed in the interface.

2. Ask a Question: Enter a query like, “What is the CPU architecture of my computer?”

3. Tool Invocation: Claude Desktop will display a dialog indicating that the AI model wants to call get_host_info. Click “Allow” to proceed.


4. View Results: The Agent will execute the tool, retrieve the system information, and display the AI’s response based on the tool’s output.

For example, the AI might respond:


The response is generated by the AI model using the JSON output from get_host_info.