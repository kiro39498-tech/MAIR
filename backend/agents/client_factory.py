"""
Chat client factory. Centralizes Azure OpenAI configuration so every agent
constructs its client the same way, and so tests can swap in a stub without
touching agent code.
"""
from __future__ import annotations

from agent_framework.openai import OpenAIChatClient
from config.settings import settings


def get_azure_openai_client() -> OpenAIChatClient:
    if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
        raise RuntimeError(
            "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set to run "
            "agents live. Analytics and MCP tools work without them — only the "
            "agent reasoning/explanation layer needs Azure OpenAI."
        )
    return OpenAIChatClient(
        model=settings.azure_openai_deployment,
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
    )


def get_mcp_tool():
    """The single MCP connection every agent uses. Spawns the MCP server as a
    stdio subprocess (Phase 1). Swap to MCPStreamableHTTPTool(url=...) once
    the MCP server runs as its own deployed service."""
    from agent_framework import MCPStdioTool
    return MCPStdioTool(
        name="material-availability-mcp",
        command=settings.mcp_server_command,
        args=settings.mcp_server_args,
    )
