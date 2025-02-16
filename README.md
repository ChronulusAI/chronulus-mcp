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