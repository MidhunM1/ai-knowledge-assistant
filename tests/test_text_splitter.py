from langchain_core.documents import Document

from src.text_splitter import split_documents


def test_split_documents():
    document = Document(
        page_content="Python is a programming language. " * 100,
        metadata={"source": "sample.pdf", "page": 1}
    )

    chunks = split_documents([document])

    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)


def test_split_documents_preserves_metadata():
    document = Document(
        page_content="Artificial Intelligence " * 100,
        metadata={"source": "AI.pdf", "page": 3}
    )

    chunks = split_documents([document])

    assert all(chunk.metadata["source"] == "AI.pdf" for chunk in chunks)
    assert all(chunk.metadata["page"] == 3 for chunk in chunks)


def test_split_empty_document_list():
    chunks = split_documents([])

    assert chunks == []