from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4
from pipeline import read_document
from tqdm import tqdm
import chromadb


client = chromadb.Client()
# Chunking the document


def chunking(doc: str):
    """ Chunk the text of the document and returning a list of chunks.
    
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    return text_splitter.split_text(doc)


def doc_chunks(path: list):
    """ Takes the Path of the files and returns the chunks
    """
    all_chunks = []
    for doc in tqdm(path):
        document_string = read_document(doc)
        chunks = chunking(document_string)
        for i in chunks:
            all_chunks.append({
                "id": f"{doc}_chunk_{uuid4()}",
                "document": chunks,
                "metadata": {
                    "source": doc,
                    "chunk_index": i
                }
            })
    return all_chunks

def document_collection(chunked_documents: list):
    """Collection from the chunked documents.
    """
    collection = client.create_collection(name="my_docs")

    for i in range(0, len(chunked_documents)):
        collection.add(
                ids = [c["id"] for c in chunked_documents],
                document = [c["document"] for c in chunked_documents],
                metadata = [c["metadata"] for c in chunked_documents],
                )
    return collection
