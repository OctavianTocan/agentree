from agentree.indexing.pdf_io import tag_physical_indices


def test_tags_each_page_with_its_physical_index():
  page_list = [('first page text', 10), ('second page text', 10)]

  pages = tag_physical_indices(page_list)

  assert len(pages) == 2
  assert '<physical_index_1>' in pages[0].content
  assert 'first page text' in pages[0].content
  assert '<physical_index_2>' in pages[1].content
  assert 'second page text' in pages[1].content


def test_start_index_offsets_the_physical_index():
  page_list = [('only page', 5)]

  pages = tag_physical_indices(page_list, start_index=7)

  assert '<physical_index_7>' in pages[0].content
