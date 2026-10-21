import json

import typer
from rich import print

from etl.pipeline import run_pipeline

app = typer.Typer(help="Client legacy document ETL and vector indexing")


@app.command()
def ingest(
    input_dir: str,
    backend: str = typer.Option("chroma", help="chroma or qdrant"),
    dry_run: bool = typer.Option(False, help="Extract/chunk only; do not index"),
    output_manifest: str = typer.Option("", help="Optional JSONL chunk manifest"),
):
    """Extract, chunk, embed in batches, and index a directory."""
    result = run_pipeline(input_dir, backend, dry_run, output_manifest or None)
    print(json.dumps(result, indent=2))
    if result["errors"]:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
