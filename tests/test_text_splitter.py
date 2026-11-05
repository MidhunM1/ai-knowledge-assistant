from langchain_core.documents import Document

from src.text_splitter import split_documents


def test_split_documents():

    text = "Artificial Intelligence " * 200

    documents = [
        Document(
            page_content=text,
            metadata={
                "source": "sample.pdf",
                "page": 1
            }
        )
    ]

    chunks = split_documents(documents)

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk.page_content) <= 1000

    assert chunks[0].metadata["source"] == "sample.pdf"
    assert chunks[0].metadata["page"] == 1