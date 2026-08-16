"""Skill-driven agent for any OpenAI-compatible endpoint.

Run locally:
  OPENAI_BASE_URL=https://api.example.com/v1 OPENAI_API_KEY=... OPENAI_MODEL=... \
    uv run --with 'pydantic-ai-harness[skills]' --with openai python harness_agent.py

Databricks alternative:
  # OPENAI_BASE_URL=https://<workspace>.cloud.databricks.com/serving-endpoints
  # OPENAI_API_KEY=$(databricks auth token --host https://<workspace>.cloud.databricks.com | jq -r .access_token)

For a scheduled job, install pydantic-ai-harness[skills] and openai, then use the
platform's execution-context token instead of a local credential.
"""
import os
import pathlib

from pydantic_ai import Agent
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai_harness.skills import Skills

SKILLS_DIR = pathlib.Path(__file__).parent / "skills"


def build_agent(
    base_url: str | None = None,
    api_key: str | None = None,
    model_name: str | None = None,
) -> Agent:
    """Build the agent from explicit values or standard environment variables."""
    resolved_base_url = base_url or os.environ["OPENAI_BASE_URL"]
    resolved_api_key = api_key or os.environ["OPENAI_API_KEY"]
    resolved_model = model_name or os.environ["OPENAI_MODEL"]

    model = OpenAIChatModel(
        resolved_model,
        provider=OpenAIProvider(base_url=resolved_base_url, api_key=resolved_api_key),
    )
    return Agent(
        model,
        capabilities=[Skills(SKILLS_DIR)],
        instructions=(
            "You are running headlessly. Skip freshness and update steps. Never ask the user "
            "questions; decide and proceed. Keep data requests small."
        ),
    )


agent = build_agent()


# Narrow tools are the default for unattended runs. Add only the operations the task needs.
@agent.tool_plain
def lookup_record(record_id: str) -> str:
    """Return one record from the application's data source."""
    raise NotImplementedError("Connect this narrow tool to the project's data source")


# For trusted local runs of skills with bundled adapters, replace narrow tools with:
# from pydantic_ai_harness.filesystem import FileSystem
# from pydantic_ai_harness.shell import Shell
# Then add Shell() and FileSystem() to capabilities in build_agent.

result = agent.run_sync(
    "TODO: state the task goal, not the steps; the skills carry the procedure."
)

# Trace verification. Filter by isinstance, not exact class-name strings: skill loads are
# typed subclasses and otherwise disappear from the trace.
lines, skill_loaded = [], False
for message in result.all_messages():
    for part in message.parts:
        if isinstance(part, ToolCallPart):
            lines.append(f"CALL[{part.__class__.__name__}] {part.tool_name}\nARGS: {str(part.args)[:300]}")
            skill_loaded |= part.tool_name == "load_capability"
        elif isinstance(part, ToolReturnPart):
            lines.append(f"RET[{part.__class__.__name__}] {part.tool_name}\nCONTENT: {str(part.content)[:300]}")
        elif part.__class__.__name__ in ("TextPart", "UserPromptPart"):
            lines.append(f"{part.__class__.__name__}: {str(part.content)[:300]}")
pathlib.Path("trace.txt").write_text("\n\n".join(lines))

print(result.output)
print(f"\n--- skill_loaded={skill_loaded}  usage={result.usage}  (full trace: trace.txt)")
