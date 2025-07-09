# goodreads-mcp

A CLI tool for Goodreads MCP integration.

## Installation

### Prerequisites

If you don't have `uv` installed, first install it:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Clone the repository

```bash
git clone https://github.com/getgather-hub/mcp-getgather-goodreads.git
cd mcp-getgather-goodreads
```

## Usage

### CLI Commands

```bash
# Get books from Goodreads
uv run goodreads-mcp get-books --email your-email@example.com --password your-password

# Use a custom host (default: 127.0.0.1:8000)
uv run goodreads-mcp get-books --email your-email@example.com --password your-password --host myserver.com
```

### Using with Claude Desktop

To use goodreads-mcp as an MCP server in Claude Desktop:

1. First clone the repository:
   ```bash
   git clone https://github.com/getgather-hub/mcp-getgather-goodreads.git
   cd mcp-getgather-goodreads
   ```

2. Configure Claude Desktop by editing the config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

3. Add the following configuration:
   ```json
   {
     "mcpServers": {
       "goodreads": {
         "command": "uv",
         "args": [
           "--directory",
           "/path/to/mcp-getgather-goodreads",
           "run",
           "goodreads-mcp"
         ],
         "env": {
           "GOODREADS_EMAIL": "your-email@example.com",
           "GOODREADS_PASSWORD": "your-password",
           "GETGATHER_URL": "127.0.0.1:8000"
         }
       }
     }
   }
   ```

   Note: Replace `/path/to/mcp-getgather-goodreads` with the actual path where you cloned the repository.

4. Restart Claude Desktop

### Available MCP Tools

Once configured, the following tools will be available in Claude:

- **get_goodreads_books**: Get books from your Goodreads library

### Environment Variables

The MCP server requires these environment variables:

- `GOODREADS_EMAIL`: Your Goodreads account email
- `GOODREADS_PASSWORD`: Your Goodreads account password
- `GETGATHER_URL`: (Optional) Host URL for the service (default: 127.0.0.1:8000)
