from src.embeddings import get_embeddings


def test_get_embeddings():

    embeddings = get_embeddings()

    assert embeddings is not None
    