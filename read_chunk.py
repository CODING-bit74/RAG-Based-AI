# Import the requests library to make HTTP requests
import requests

# Make a POST request to the local Ollama API endpoint for generating embeddings
# This connects to a locally running Ollama server on port 11434
def create_embedding(text):
    response = requests.post("http://localhost:11434/api/embeddings", json={
        # Specify the embedding model to use (bge-m3 is a multilingual embedding model)
        "model": "bge-m3",
        # The text to generate embeddings for (will be converted to vector representation)
        "prompt": text
    })
    embedding=response.json()["embedding"]
    return embedding

embedding = create_embedding("Python is a great programming language.")
print(embedding)   

    


