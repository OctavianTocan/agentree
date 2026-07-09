"""CLI entrypoint for indexing a PDF into a section tree."""

import os

import typer
from loguru import logger

from pdfindex.indexing import index
from pdfindex.logging_config import configure_logging

configure_logging()

app = typer.Typer()


@app.command()
@logger.catch(reraise=True)
def main(
  pdf_path: str = typer.Option(..., '--pdf_path', help='Path to the PDF file'),
) -> None:
  """Process a PDF document and generate its structure."""
  if not pdf_path.lower().endswith('.pdf'):
    logger.error('Invalid file extension: {}', pdf_path)
    raise ValueError('PDF file must have .pdf extension')
  if not os.path.isfile(pdf_path):
    logger.error('PDF file not found: {}', pdf_path)
    raise ValueError(f'PDF file not found: {pdf_path}')

  logger.bind(pdf_path=pdf_path).info('Processing PDF')
  # TODO: Persist the result once index() returns Tree (+ pages): init_db,
  # store_document, and optionally print doc_id. Today the return value is
  # discarded. Also add a --db_path (or corpus/) flag when wiring storage.
  # TODO: MCP server entrypoint is separate (see TODO.md); this CLI stays the
  # indexer front door.
  index(pdf_path)


if __name__ == '__main__':
  app()
