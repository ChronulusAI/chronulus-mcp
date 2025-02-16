import argparse
import logging
from importlib.metadata import version

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

mcp = FastMCP("chronulus-agents")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


def  main():
    """Chronulus AI: A platform for the forecasting and prediction. Predict anything."""
    parser = argparse.ArgumentParser(description="Chronulus MCP provides access for forecasting and prediction agents.")
    parser.parse_args()
    mcp.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler()])
    main()
