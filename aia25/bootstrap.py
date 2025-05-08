from __future__ import annotations
import os, base64, nest_asyncio, logfire, dotenv
from pathlib import Path

# Load environment variables from .env file
dotenv.load_dotenv(Path(__file__).parent.parent / ".env", override=True)

if os.getenv("LANGFUSE_TRACING_ACTIVE", "false") == "true":
    # Configure tracing with Langfuse
    pub, sec = os.getenv("LANGFUSE_PUBLIC_KEY"), os.getenv("LANGFUSE_SECRET_KEY")
    if pub and sec:
        auth = base64.b64encode(f"{pub}:{sec}".encode()).decode()
        os.environ.setdefault(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            f"{os.getenv('LANGFUSE_HOST','')}/api/public/otel",
        )
        os.environ.setdefault("OTEL_EXPORTER_OTLP_HEADERS", f"Authorization=Basic {auth}")

    nest_asyncio.apply()

    logfire.configure(service_name="AIA25", send_to_logfire=False)
    logfire.instrument_openai_agents()
