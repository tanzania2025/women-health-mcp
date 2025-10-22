# Women's Health MCP Project - Claude Code Context

## Python Path Configuration

**IMPORTANT:** When creating or updating Claude Desktop MCP server configurations, always use the **full path** to Python.

For this project, use Anaconda Python:
- ✅ Correct: `"command": "/Users/dgordon/anaconda3/bin/python"`
- ❌ Incorrect: `"command": "python"` or `"command": "python3"`

Claude Desktop cannot resolve short commands like `python` without the full path because `/Users/dgordon/anaconda3/bin` is not in Claude Desktop's default PATH.

### Example Configuration

```json
{
  "mcpServers": {
    "my-server": {
      "command": "/Users/dgordon/anaconda3/bin/python",
      "args": [
        "/Users/dgordon/womens_health_mcp/my_server.py"
      ]
    }
  }
}
```

## Project Structure

This project contains multiple MCP servers for women's health research:
- `pubmed_server.py` - PubMed article search and retrieval
- `asrm_server.py` - ASRM practice guidelines
- `sart_ivf_server.py` - SART IVF success calculator

## Testing MCP Servers

Before adding to Claude Desktop config, test servers with:
```bash
python /path/to/server.py
```

Or test specific functions:
```bash
python -c "from server_name import function_name; print('✓ Imports successfully')"
```
