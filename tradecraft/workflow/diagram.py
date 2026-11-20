"""Write the workflow diagram, generated from the graph itself.

    .venv/bin/python -m tradecraft.workflow.diagram

Writes docs/workflow-diagram.md (Mermaid; it renders on the repository page).
"""
import tempfile
from pathlib import Path

from .. import settings
from ..storage import Store
from .graph import Workflow

HEADER = """# Tradecraft workflow diagram

Generated from the LangGraph graph in `tradecraft/workflow/graph.py` by
`python -m tradecraft.workflow.diagram`. Do not edit by hand.

Solid arrows always run. Dotted arrows are choices: the user's action at a pause
(`*_pause`, `stage2_stopped`, `stage4_stopped`), the one-time return of a draft
(`validate` to `thesis`, `critic_check` to `critic`), or a stage stopping.
The three analysts run in parallel between `grades` and `analysts_done`.

```mermaid
"""


def main() -> None:
    with tempfile.TemporaryDirectory() as d:
        text = Workflow(Store(Path(d) / "diagram.sqlite3")).mermaid()
    out = settings.ROOT / "docs" / "workflow-diagram.md"
    out.write_text(HEADER + text.strip() + "\n```\n")
    print(f"wrote {out.relative_to(settings.ROOT)}")


if __name__ == "__main__":
    main()
