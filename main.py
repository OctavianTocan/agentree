from PDFindex.pdf_index import index
import os
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("pdf_index.log")],
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
      # Set up argument parser
    parser = argparse.ArgumentParser(description='Process PDF or Markdown document and generate structure')
    parser.add_argument('--pdf_path', type=str, help='Path to the PDF file')
    # Parse arguments
    args = parser.parse_args()

    if not args.pdf_path:
      logger.error("No PDF file provided")
      raise ValueError("PDF file must be provided")
    else:
      # Process PDF file
      if not args.pdf_path.lower().endswith('.pdf'):
        logger.error("Invalid file extension: %s", args.pdf_path)
        raise ValueError("PDF file must have .pdf extension")
      if not os.path.isfile(args.pdf_path):
        logger.error("PDF file not found: %s", args.pdf_path)
        raise ValueError(f"PDF file not found: {args.pdf_path}")
      else:
        logger.info("Processing PDF: %s", args.pdf_path)
        # Index the PDF file.
        index(args.pdf_path)