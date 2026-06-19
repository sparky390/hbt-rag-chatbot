from chromadb import Client


def create_chroma_client():
    return Client()


def persist_collection(collection, path):
    # TODO: save the Chroma collection to disk
    pass
