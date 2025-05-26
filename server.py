# Interactive Feedback MCP
# Developed by Fábio Ferreira (https://x.com/fabiomlferreira)
# Inspired by/related to dotcursorrules.com (https://dotcursorrules.com/)
# Enhanced by Pau Oliva (https://x.com/pof) with ideas from https://github.com/ttommyth/interactive-mcp
import os
import sys
import json
import tempfile
import subprocess
from typing import Dict, List, Optional

from fastmcp import FastMCP
from pydantic import Field

# Initialize FastMCP server
mcp = FastMCP("Interactive Feedback MCP")

def launch_feedback_ui(summary: str, predefinedOptions: list[str] | None = None) -> dict[str, str]:
    # Create a temporary file for the feedback result
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name

    try:
        # Get the path to the feedback script relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        feedback_web_path = os.path.join(script_dir, "feedback_web.py")
        feedback_ui_path = os.path.join(script_dir, "feedback_ui.py")
        
        # Check environment preference and availability
        ui_preference = os.environ.get('INTERACTIVE_FEEDBACK_UI', 'auto').lower()
        has_display = os.environ.get('DISPLAY') is not None
        
        # Check if PySide6 is available for GUI
        has_pyside6 = False
        try:
            import PySide6
            has_pyside6 = True
        except ImportError:
            pass
        
        # Determine which interface to use
        script_path = None
        interface_type = "unknown"
        
        if ui_preference == 'web' and os.path.exists(feedback_web_path):
            script_path = feedback_web_path
            interface_type = "web"
        elif ui_preference == 'gui' and has_display and has_pyside6 and os.path.exists(feedback_ui_path):
            script_path = feedback_ui_path
            interface_type = "gui"
        elif ui_preference == 'auto':
            # Auto-select based on environment
            if os.path.exists(feedback_web_path):
                script_path = feedback_web_path
                interface_type = "web"
            elif has_display and has_pyside6 and os.path.exists(feedback_ui_path):
                script_path = feedback_ui_path
                interface_type = "gui"
        
        if not script_path:
            return {"interactive_feedback": "Error: No suitable feedback interface found"}
        
        # Prepare command arguments
        cmd = [sys.executable, script_path, "--prompt", summary, "--output-file", output_file]
        
        if predefinedOptions:
            options_str = "|||".join(predefinedOptions)
            cmd.extend(["--predefined-options", options_str])
        
        print(f"🚀 Launching {interface_type} feedback interface...", flush=True)
        
        # Run the feedback script
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Feedback script failed: {result.stderr}", flush=True)
            return {"interactive_feedback": "Error: Feedback collection failed"}
        
        # Read the result
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                feedback_result = json.load(f)
            return feedback_result
        else:
            return {"interactive_feedback": "Error: No feedback file generated"}
    
    except Exception as e:
        print(f"❌ Error in launch_feedback_ui: {e}", flush=True)
        return {"interactive_feedback": f"Error: {str(e)}"}
    
    finally:
        # Clean up temporary file
        if os.path.exists(output_file):
            try:
                os.unlink(output_file)
            except:
                pass

@mcp.tool()
def interactive_feedback(
    message: str = Field(description="The specific question for the user"),
    predefined_options: list = Field(default=None, description="Predefined options for the user to choose from (optional)"),
) -> Dict[str, str]:
    """Request interactive feedback from the user"""
    predefined_options_list = predefined_options if isinstance(predefined_options, list) else None
    return launch_feedback_ui(message, predefined_options_list)

if __name__ == "__main__":
    # Run with stdio transport
    mcp.run(transport="stdio")
