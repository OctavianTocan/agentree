from PDFindex.indexing.pdf_index import process


def test_tags_each_page_with_its_physical_index():
  page_list = [('first page text', 10), ('second page text', 10)]

  chunk_texts = process(page_list)

  assert len(chunk_texts) == 1
  assert '<physical_index_1>' in chunk_texts[0]
  assert 'first page text' in chunk_texts[0]
  assert '<physical_index_2>' in chunk_texts[0]
  assert 'second page text' in chunk_texts[0]


def test_start_index_offsets_the_physical_index():
  page_list = [('only page', 5)]

  chunk_texts = process(page_list, start_index=7)

  assert '<physical_index_7>' in chunk_texts[0]
