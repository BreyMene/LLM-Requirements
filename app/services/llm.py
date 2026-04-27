"""
Large Language Model (LLM) Integration Service

This module communicates with a local Ollama instance to generate AI responses.
It provides a simple interface for prompting a language model without managing
the model lifecycle directly.

Configuration:
- Backend: Ollama (must be running locally)
- Default Model: Mistral
- API Endpoint: http://localhost:11434/api/generate
"""

import requests

# Ollama API endpoint configuration
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate(prompt, model="mistral"):
    """
    Generate a text response from a language model using a custom prompt.
    
    Sends a prompt to a local Ollama instance and returns the generated response.
    The model processes the prompt and generates text based on its training.
    
    Args:
        prompt (str): The input prompt to send to the model.
                     Should include system instructions and task context.
        model (str, optional): Name of the Ollama model to use.
                              Defaults to "mistral".
                              Other options: "neural-chat", "llama2", "openhermes", etc.
    
    Returns:
        str: The generated text response from the model.
            Returns error message if the API call fails.
    
    Raises:
        No exceptions are raised. Errors are returned as strings in the response.
    
    Note:
        - Requires Ollama to be running locally (default: http://localhost:11434)
        - Uses non-streaming mode (stream=False) for complete responses
        - The model must be downloaded in Ollama first (e.g., ollama pull mistral)
    
    Example:
        >>> prompt = "Analyze this requirement: The system must be fast"
        >>> response = generate(prompt)
        >>> print(response)
        "The requirement lacks specificity..."
    """
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": prompt,
        "stream": False
    })

    data = response.json()
    return data.get("response", "Error generating response from model: ")