

class EmbeddingService():
    def __init__(self):
        pass

    def get_local_embedding_model(self, model_name: str) -> SentenceTransformer:
        try: 
            model = SentenceTransformer(model_name)



