# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import tempfile
import subprocess

from typing import Annotated, Dict

from fastmcp import FastMCP
from pydantic import Field

# The log_level is necessary for Cline to work: https://github.com/jlowin/fastmcp/issues/81
mcp = FastMCP("Interactive Feedback MCP", log_level="ERROR")

def launch_feedback_ui(summary: str, predefinedOptions: list[str] | None = None) -> dict[str, str]:
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to the feedback script relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try GUI version first, fall back to CLI version
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")
        feedback_cli_path = os.path.join(script_dir, "feedback_cli.py")
        
        # Check if we have a display (GUI environment)
        has_display = os.environ.get('DISPLAY') is not None
        
        # Choose the appropriate script
        if has_display and os.path.exists(feedback_ui_path):
            script_path = feedback_ui_path
            use_cli = False
        else:
            script_path = feedback_cli_path
            use_cli = True

        # Run the feedback script as a separate process
        args = [
            sys.executable,
            "-u",
            script_path,
            "--prompt", summary,
            "--output-file", output_file,
            "--predefined-options", "|||".join(predefinedOptions) if predefinedOptions else ""
        ]
        
        if use_cli:
            # For CLI version, we need to allow interaction
            result = subprocess.run(
                args,
                check=False,
                shell=False,
                stdin=None,  # Allow stdin for user input
                stdout=None,  # Allow stdout for user interaction
                stderr=None   # Allow stderr for error messages
            )
        else:
            # For GUI version, suppress output as before
            result = subprocess.run(
                args,
                check=False,
                shell=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True
            )
            
        if result.returncode != 0:
            raise Exception(f"Failed to launch feedback interface: {result.returncode}")

        # Read the result from the temporary file
        with open(output_file, 'r') as f:
            result = json.load(f)
        os.unlink(output_file)
        return result
    except Exception as e:
        if os.path.exists(output_file):
            os.unlink(output_file)
        raise e

@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options for the user to choose from (optional)"),
) -> Dict[str, str]:
    """Request interactive feedback from the user"""
    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None
    return launch_feedback_ui(message, predefined_options_list)

if __name__ == "__main__":
    mcp.run(transport="stdio")
