from PDFindex.pdf_index import count_tokens


def test_counts_roughly_four_characters_per_token():
    assert count_tokens("aaaa") == 1
    assert count_tokens("aaaaaaaa") == 2


def test_empty_text_has_zero_tokens():
    assert count_tokens("") == 0
