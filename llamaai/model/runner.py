from llamaai.model.Generation import LlamaModel
from llamaai.model.RedisQueries import handle_queries

if __name__ == "__main__":
    # Test Model Functionality
    prompt = "Answer this question concisely. Stop when you are done: What is punctuated equilibrium?"
    LlamaModel.initialize()
    LlamaModel.query_model(prompt)

    # Start Runner
    handle_queries()
