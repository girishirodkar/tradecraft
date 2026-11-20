"""Tradecraft: personal options research tool (on-demand mode, stages 1 to 4).

Places no orders and gives no investment advice.
"""
import os

# LangGraph pulls in LangSmith, which can send traces to an outside service when
# tracing is switched on in the environment. Traces stay local: force it off.
for _name in ("LANGSMITH_TRACING", "LANGSMITH_TRACING_V2", "LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2"):
    os.environ[_name] = "false"
