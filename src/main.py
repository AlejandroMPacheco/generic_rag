from chunks import collection, document_collection
from pipeline import read_document, read_dir

documents = read_dir("../Docs/")
document = documents[0]

if __name__ == "__main__":
    chunk_collection = collection(documents)
