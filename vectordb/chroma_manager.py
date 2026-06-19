import chromadb


def get_client(path: str = "chroma_db") -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=path)


def get_or_create_collection(client, name: str = "hbt_knowledge"):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def drop_and_recreate(client, name: str = "hbt_knowledge"):
    try:
        client.delete_collection(name)
    except Exception:
        pass
    return client.create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )