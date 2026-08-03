"""Agentree MCP server.

This server provides an MCP endpoint for indexing PDF files into a nested section Tree.

It can be run with:

```bash
python -m agentree.mcp.server
```

It will start an MCP server on port 8000.
"""

from fastmcp import FastMCP

from agentree.indexing import index

mcp = FastMCP('agentree')


@mcp.tool
def index_pdf(path: str) -> str:
  """Index a PDF file into a nested section Tree.

  Args:
    path: The path to the PDF file to index.

  Returns:
    The indexed Tree.
  """
  return str(index(path))


if __name__ == '__main__':
  mcp.run()
