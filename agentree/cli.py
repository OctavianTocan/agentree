"""CLI entrypoint for indexing a PDF into a section tree."""

from pathlib import Path

import typer
from loguru import logger

from agentree.indexing import index
from agentree.logging_config import configure_logging
from agentree.models import Tree

configure_logging()

app = typer.Typer()


@app.command()
@logger.catch(reraise=True)
def main(
  pdf_path: str = typer.Option(..., '--pdf_path', help='Path to the PDF file'),
  out_dir: str = typer.Option('output', '--out_dir', help='Directory to write the tree JSON into'),
) -> None:
  """Process a PDF document and generate its structure.

  Args:
    pdf_path: Path to the PDF file to index.
    out_dir: Directory the tree JSON is written into.

  Raises:
    ValueError: If `pdf_path` is not a `.pdf` file, or does not exist.

  """
  if not pdf_path.lower().endswith('.pdf'):
    logger.error('Invalid file extension: {}', pdf_path)
    msg = 'PDF file must have .pdf extension'
    raise ValueError(msg)
  if not Path(pdf_path).is_file():
    logger.error('PDF file not found: {}', pdf_path)
    msg = f'PDF file not found: {pdf_path}'
    raise ValueError(msg)

  logger.bind(pdf_path=pdf_path).info('Processing PDF')
  # TODO: Persist to a real store (init_db, store_document, --db_path) once
  # storage is wired; this JSON dump is the stopgap.
  # TODO: MCP server entrypoint is separate (see TODO.md); this CLI stays the
  # indexer front door.
  tree: Tree = index(pdf_path)
  out_path = save_tree(tree, out_dir)
  logger.bind(out_path=str(out_path)).info('Wrote tree JSON')


def save_tree(tree: Tree, out_dir: str) -> Path:
  """Write the tree as JSON to ``<out_dir>/<doc_name>.json``, overwriting any existing file.

  Args:
    tree: The assembled index to serialise.
    out_dir: Directory to write into; created if absent.

  Returns:
    Path of the file written.

  """
  directory = Path(out_dir)
  directory.mkdir(parents=True, exist_ok=True)
  out_path = directory / f'{Path(tree.doc_name).stem}.json'
  out_path.write_text(tree.model_dump_json(indent=2))
  return out_path


if __name__ == '__main__':
  app()
