import logging
import os

import typer

from PDFindex.pdf_index import index

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s %(levelname)s %(name)s: %(message)s',
  handlers=[logging.StreamHandler(), logging.FileHandler('pdf_index.log')],
)
logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def main(
  pdf_path: str = typer.Option(..., '--pdf_path', help='Path to the PDF file'),
) -> None:
  """Process a PDF document and generate its structure."""
  if not pdf_path.lower().endswith('.pdf'):
    logger.error('Invalid file extension: %s', pdf_path)
    raise ValueError('PDF file must have .pdf extension')
  if not os.path.isfile(pdf_path):
    logger.error('PDF file not found: %s', pdf_path)
    raise ValueError(f'PDF file not found: {pdf_path}')

  logger.info('Processing PDF: %s', pdf_path)
  index(pdf_path)


if __name__ == '__main__':
  app()
