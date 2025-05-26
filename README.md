# 🗣️ Interactive Feedback MCP

Simple [MCP Server](https://modelcontextprotocol.io/) to enable a human-in-the-loop workflow in AI-assisted development tools like [Cursor](https://www.cursor.com), [Cline](https://cline.bot) and [Windsurf](https://windsurf.com). This server allows you to easily provide feedback directly to the AI agent, bridging the gap between AI and you.

**Note:** This server is designed to run locally alongside the MCP client (e.g., Claude Desktop, Cursor), as it needs direct access to the user's operating system to display the feedback interface.

## ✨ Features

- **💬 Interactive Feedback**: Ask clarifying questions and get user responses
- **🌐 Web Interface**: Modern, responsive web-based interface with Markdown support
- **🖼️ GUI Interface**: Native desktop application (when available)
- **📱 Multi-platform**: Works on Windows, macOS, Linux (including ARM64)
- **🎯 Predefined Options**: Support for multiple-choice questions with custom options
- **⌨️ Keyboard Shortcuts**: Quick submission with Ctrl+Enter

## 💡 Why Use This?

In environments like Cursor, every prompt you send to the LLM is treated as a distinct request — and each one counts against your monthly limit (e.g. 500 premium requests). This becomes inefficient when you're iterating on vague instructions or correcting misunderstood output, as each follow-up clarification triggers a full new request.

This MCP server introduces a workaround: it allows the model to pause and request clarification before finalizing the response. Instead of completing the request, the model triggers a tool call (`interactive_feedback`) that opens an interactive feedback window. You can then provide more detail or ask for changes — and the model continues the session, all within a single request.

Under the hood, it's just a clever use of tool calls to defer the completion of the request. Since tool calls don't count as separate premium interactions, you can loop through multiple feedback cycles without consuming additional requests.

Essentially, this helps your AI assistant _ask for clarification instead of guessing_, without wasting another request. That means fewer wrong answers, better performance, and less wasted API usage.

- **💰 Reduced Premium API Calls:** Avoid wasting expensive API calls generating code based on guesswork.
- **✅ Fewer Errors:** Clarification _before_ action means less incorrect code and wasted time.
- **⏱️ Faster Cycles:** Quick confirmations beat debugging wrong guesses.
- **🎮 Better Collaboration:** Turns one-way instructions into a dialogue, keeping you in control.

## 🛠️ Tools

This server exposes the following tool via the Model Context Protocol (MCP):

- `interactive_feedback`: Asks the user a question and returns their answer. Can display predefined options for quick selection.

### Example Usage

```python
# Simple question
interactive_feedback(
    message="Do you approve this code change?"
)

# Multiple choice question
interactive_feedback(
    message="Which approach should we use?",
    predefined_options=["Option A", "Option B", "Option C"]
)

# Markdown-formatted question
interactive_feedback(
    message="""## Code Review

Please review the following changes:

- Added error handling
- Improved performance
- Updated documentation

**Do you want to proceed?**"""
)
```

## 📦 Installation

1. **Prerequisites:**
   - Python 3.11 or newer
   - [uv](https://github.com/astral-sh/uv) (Python package manager). Install it with:
     - Windows: `pip install uv`
     - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
     - macOS: `brew install uv`

2. **Get the code:**
   - Clone this repository:
     ```bash
     git clone https://github.com/pauoliva/interactive-feedback-mcp.git
     cd interactive-feedback-mcp
     ```
   - Or download the source code.

3. **Install dependencies:**
   ```bash
   uv sync
   ```

## 🖥️ Environment Support

This MCP server automatically adapts to your environment and supports multiple interface modes:

- **🌐 Web Mode**: Modern web-based interface with full Markdown support, beautiful styling, and responsive design (recommended)
- **🖼️ GUI Mode**: Native desktop application using PySide6 (when available)

### Interface Selection

The server automatically chooses the best interface, but you can override this with the `INTERACTIVE_FEEDBACK_UI` environment variable:

```bash
# Force web interface (recommended)
export INTERACTIVE_FEEDBACK_UI=web

# Force GUI interface
export INTERACTIVE_FEEDBACK_UI=gui

# Auto-detect (default, prioritizes web)
export INTERACTIVE_FEEDBACK_UI=auto
```

**Recommendation**: Use `web` mode for the best experience - it provides beautiful Markdown rendering, responsive design, and works consistently across all platforms.

### Platform Compatibility

- **✅ Windows**: Full Web and GUI support
- **✅ macOS**: Full Web and GUI support  
- **✅ Linux x86_64**: Full Web and GUI support
- **✅ Linux ARM64** (Raspberry Pi, etc.): Web support, GUI support with compatible PySide6 version (6.6.x+)

**Note for ARM64 Linux users**: If you encounter PySide6 compatibility issues, the server will automatically fall back to Web mode. For GUI support on ARM64, ensure you have PySide6 6.6.0 or newer.

## ⚙️ Configuration

### For Cursor IDE

Add the following configuration to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/interactive-feedback-mcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

### For Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

**Remember to change the `/path/to/interactive-feedback-mcp` path to the actual path where you cloned the repository on your system.**

### Recommended Rules

Add the following to your AI assistant's custom rules (in Cursor Settings > Rules > User Rules):

```
If requirements or instructions are unclear use the tool interactive_feedback to ask clarifying questions to the user before proceeding, do not make assumptions. Whenever possible, present the user with predefined options through the interactive_feedback MCP tool to facilitate quick decisions.

Whenever you're about to complete a user request, call the interactive_feedback tool to request user feedback before ending the process. If the feedback is empty you can end the request and don't call the tool in loop.
```

This will ensure your AI assistant always uses this MCP server to request user feedback when the prompt is unclear and before marking the task as completed.

## 🧪 Testing

Test the MCP server functionality:

```bash
uv run python test_mcp_server.py
```

Test the web interface directly:

```bash
uv run python feedback_web.py --prompt "Test question" --output-file result.json
```

## 📁 Project Structure

```
interactive-feedback-mcp/
├── server.py              # Main MCP server
├── feedback_web.py        # Web interface implementation
├── feedback_ui.py         # GUI interface implementation
├── test_mcp_server.py     # MCP protocol tests
├── DEVELOPMENT_NOTES.md   # Development experience summary
├── pyproject.toml         # Project configuration
└── README.md             # This file
```

## 🔒 Security

- All user interfaces run locally
- No data is transmitted to external servers
- Temporary files are automatically cleaned up
- User approval required for all feedback requests

## 🛠️ Development

### Requirements

- Python 3.10+
- FastMCP 2.0+
- Optional: PySide6 (for GUI interface)

### Running in Development

```bash
# Install with development dependencies
uv sync --extra gui

# Run the server
uv run server.py

# Run tests
uv run python test_mcp_server.py
```

## 📚 Documentation

- [Development Notes](doc/development.md) - Detailed development experience and best practices
- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Cursor MCP Guide](https://docs.cursor.com/context/model-context-protocol)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

Developed by Fábio Ferreira ([@fabiomlferreira](https://x.com/fabiomlferreira)).

Enhanced by Pau Oliva ([@pof](https://x.com/pof)) with ideas from Tommy Tong's [interactive-mcp](https://github.com/ttommyth/interactive-mcp).

---

**Note**: This is a simplified version focused on core interactive feedback functionality. Advanced features like image processing and MCP Sampling are not included due to current limitations in Cursor's MCP support.