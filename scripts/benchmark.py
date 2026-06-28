import time
from app.ai.groq_client import GroqClient

def main():
    print("Benchmarking AI Orchestration Layer Latency...")
    client = GroqClient()
    
    start = time.time()
    res = client.generate_json("Output empty JSON", "Test")
    end = time.time()
    
    print(f"Groq API JSON Mode Latency: {(end-start)*1000:.2f}ms")

if __name__ == "__main__":
    main()

