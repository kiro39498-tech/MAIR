"""
Central configuration for the Material Availability & Inventory Replenishment
Agent backend. Values are overridable via environment variables / .env so the
same code runs unchanged across dev, CI, and production.
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv_if_present() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)


_load_dotenv_if_present()


class Settings:
    # --- Data source --------------------------------------------------
    # Phase 1 uses the CSV connector. Swapping to SAP/SQL/Fabric later only
    # means implementing a new Connector (see connectors/base_connector.py)
    # and changing DATA_SOURCE — nothing above the connector layer changes.
    data_source: str = os.getenv("DATA_SOURCE", "csv")
    csv_data_dir: str = os.getenv(
        "CSV_DATA_DIR", str(Path(__file__).resolve().parent.parent / "data" / "csv")
    )
    db_path: str = os.getenv(
        "DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "replenishment.db")
    )

    # --- Azure OpenAI ----------------------------------------------------
    # Used only by agents for explanation / copilot wording — never for the
    # deterministic calculations in analytics/. See core principle in the
    # approach doc: "AI never performs inventory or manufacturing calculations."
    azure_openai_endpoint: str | None = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str | None = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "preview")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    # --- MCP ---------------------------------------------------------------
    # Phase 1 spawns the MCP server as a local stdio subprocess from the
    # agents. Swap to MCPStreamableHTTPTool + mcp_server_url once the MCP
    # server is deployed as its own service.
    mcp_server_command: str = os.getenv("MCP_SERVER_COMMAND", "python")
    mcp_server_args: list[str] = ["-m", "mcp_server.server"]

    # --- API -----------------------------------------------------------
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    cors_origins: list[str] = [
        origin.strip(" '\"") for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://localhost:8081"
        ).split(",")
    ]
    api_base_url: str = os.getenv("API_BASE_URL") or f"http://localhost:{api_port}"
    frontend_base_url: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:8080")

    # --- Notifications -------------------------------------------------
    notify_email_to: str | None = os.getenv("NOTIFY_EMAIL_TO")
    notify_email_from: str | None = os.getenv("NOTIFY_EMAIL_FROM")
    smtp_host: str = os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER") or "smtp.gmail.com"
    smtp_port: int = int(os.getenv("SMTP_PORT") or "587")
    smtp_username: str | None = os.getenv("SMTP_USERNAME") or os.getenv("SMTP_EMAIL")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    notify_statuses: set[str] = {"Shortage"}


    # --- Business thresholds (deterministic engine tuning knobs) --------
    # See analytics/health_classification.py for how these are applied.
    shortage_ratio_of_safety_stock: float = 0.4
    near_reorder_lower_ratio_of_rop: float = 0.9
    near_reorder_upper_ratio_of_rop: float = 1.3
    excess_ratio_of_max_stock: float = 1.15


settings = Settings()
