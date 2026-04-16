from sentence_transformers import SentenceTornsformer
import faiss
import numpy as np

model  SentenceTransformer('all-MiniLM-L6-v2')

class VectorStore:
    def __init__(self):
        self.index = faiss.IndexFlatL2(384)
        self.data =[]
    def add(self, text):
        embedding = model.encode([text])
        self.index.add(np.array(embedding))
        self.data.append(text)

    def search(self, query):
        embedding = model.encode([query])
        D, I = self.index.search(np.array(embedding), k=3)

        return [self.data[i] for i in I[0]]