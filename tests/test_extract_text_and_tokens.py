from pathlib import Path

from PDFindex.indexing.pdf_index import extract_text_and_tokens

SAMPLE_PDF = Path(__file__).parent.parent / 'examples' / 'documents' / 'q1-fy25-earnings.pdf'


def test_returns_one_entry_per_page_with_positive_token_counts():
  page_list = extract_text_and_tokens(str(SAMPLE_PDF))

  assert len(page_list) > 0
  for text, token_count in page_list:
    assert isinstance(text, str)
    assert token_count > 0
