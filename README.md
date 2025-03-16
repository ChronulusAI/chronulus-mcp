<div align="center">
<img width="150px" src="https://www.chronulus.com/brand-assets/chronulus-logo-blue-on-alpha-square.png" alt="Chronulus AI">
    <h1 align="center">MCP Server for Chronulus</h1>
    <h3 align="center">Chat with Chronulus AI Forecasting & Prediction Agents in Claude</h3>
</div>




### Quickstart: Claude for Desktop

#### Install 

Claude for Desktop is currently available on macOS and Windows.

Install Claude for Desktop [here](https://claude.ai/download)

#### Configuration

Follow the general instructions [here](https://modelcontextprotocol.io/quickstart/user) to configure the Claude desktop client.

You can find your Claude config at one of the following locations:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Then choose one of the following methods that best suits your needs and add it to your `claude_desktop_config.json`



<details>
<summary>Using pip</summary>

(Option 1) Install release from PyPI

```bash 
pip install chronulus-mcp
```


(Option 2) Install from Github

```bash 
git clone https://github.com/ChronulusAI/chronulus-mcp.git
cd chronulus-mcp
pip install .
```



```json 
{
  "mcpServers": {
    "chronulus-agents": {
      "command": "python",
      "args": ["-m", "chronulus_mcp"],
      "env": {
        "CHRONULUS_API_KEY": "<YOUR_CHRONULUS_API_KEY>"
      }
    }
  }
}
```

Note, if you get an error like "MCP chronulus-agents: spawn python ENOENT", 
then you most likely need to provide the absolute path to `python`. 
For example `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` instead of just `python`

</details>


<details>
<summary>Using docker</summary>

Here we will build a docker image called 'chronulus-mcp' that we can reuse in our Claude config.

```bash 
git clone https://github.com/ChronulusAI/chronulus-mcp.git
cd chronulus-mcp
 docker build . -t 'chronulus-mcp'
```

In your Claude config, be sure that the final argument matches the name you give to the docker image in the build command.

```json 
{
  "mcpServers": {
    "chronulus-agents": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "CHRONULUS_API_KEY", "chronulus-mcp"],
      "env": {
        "CHRONULUS_API_KEY": "<YOUR_CHRONULUS_API_KEY>"
      }
    }
  }
}
```

</details>

<details>
<summary>Using uvx</summary>

`uvx` will pull the latest version of `chronulus-mcp` from the PyPI registry, install it, and then run it.


```json 
{
  "mcpServers": {
    "chronulus-agents": {
      "command": "uvx",
      "args": ["chronulus-mcp"],
      "env": {
        "CHRONULUS_API_KEY": "<YOUR_CHRONULUS_API_KEY>"
      }
    }
  }
}
```

Note, if you get an error like "MCP chronulus-agents: spawn uvx ENOENT", then you most likely need to either:
1. [install uv](https://docs.astral.sh/uv/getting-started/installation/) or
2. Provide the absolute path to `uvx`. For example `/Users/username/.local/bin/uvx` instead of just `uvx`

</details>

#### Additional Servers (Filesystem, Fetch, etc)

In our demo, we use third-party servers like [fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) and [filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem).

For details on installing and configure third-party server, please reference the documentation provided by the server maintainer.

Below is an example of how to configure filesystem and fetch alongside Chronulus in your `claude_desktop_config.json`: 

```json 
{
  "mcpServers": {
    "chronulus-agents": {
      "command": "uvx",
      "args": ["chronulus-mcp"],
      "env": {
        "CHRONULUS_API_KEY": "<YOUR_CHRONULUS_API_KEY>"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/AIWorkspace"
      ]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
} 
```


#### Claude Preferences

To streamline your experience using Claude across multiple sets of tools, it is best to add your preferences to under Claude Settings. 

You can upgrade your Claude preferences in a couple ways:

* From Claude Desktop: `Settings -> General -> Claude Settings -> Profile (tab)`
* From [claude.ai/settings](https://claude.ai/settings): `Profile (tab)`

Preferences are shared across both Claude for Desktop and Claude.ai (the web interface). So your instruction need to work across both experiences.

Below are the preferences we used to achieve the results shown in our demos:

```
## Tools-Dependent Protocols
The following instructions apply only when tools/MCP Servers are accessible.

### Filesystem - Tool Instructions
- Do not use 'read_file' or 'read_multiple_files' on binary files (e.g., images, pdfs, docx) .
- When working with binary files (e.g., images, pdfs, docx) use 'get_info' instead of 'read_*' tools to inspect a file.

### Chronulus Agents - Tool Instructions
- When using Chronulus, prefer to use input field types like TextFromFile, PdfFromFile, and ImageFromFile over scanning the files directly.
- When plotting forecasts from Chronulus, always include the Chronulus-provided forecast explanation below the plot and label it as Chronulus Explanation.
```