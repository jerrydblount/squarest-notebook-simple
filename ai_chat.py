"""
AI Chat module - supports multiple AI providers
"""

import os
from typing import List, Dict, Optional
from loguru import logger


def get_available_models() -> List[str]:
    """Get list of available AI models based on configured API keys"""
    models = []
    
    if os.getenv("OPENAI_API_KEY"):
        models.extend([
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ])
    
    if os.getenv("ANTHROPIC_API_KEY"):
        models.extend([
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307"
        ])
    
    if os.getenv("GOOGLE_API_KEY"):
        models.extend([
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ])
    
    # Default to a simple model if nothing configured
    if not models:
        models = ["No API keys configured - Please add keys in .env file"]
    
    return models


def chat_with_ai(
    prompt: str,
    model: str = "gpt-4o-mini",
    context: Optional[str] = None,
    history: Optional[List[Dict]] = None
) -> str:
    """
    Chat with an AI model
    
    Args:
        prompt: User's message
        model: Model name to use
        context: Optional context from sources
        history: Conversation history
    
    Returns:
        AI response text
    """
    
    # Check if we have API keys
    if "No API keys" in model:
        return "Please configure at least one AI provider API key in your .env file"
    
    # Build the full prompt
    full_prompt = ""
    if context:
        full_prompt = f"Context:\n{context[:4000]}\n\n"
    full_prompt += f"User: {prompt}"
    
    try:
        # OpenAI models
        if model.startswith("gpt"):
            return chat_with_openai(full_prompt, model, history)
        
        # Anthropic models
        elif model.startswith("claude"):
            return chat_with_anthropic(full_prompt, model, history)
        
        # Google models
        elif model.startswith("gemini"):
            return chat_with_google(full_prompt, model, history)
        
        else:
            return f"Model {model} not supported yet"
            
    except Exception as e:
        logger.error(f"Error in chat_with_ai: {e}")
        return f"Error: {str(e)}"


def chat_with_openai(prompt: str, model: str, history: Optional[List[Dict]] = None) -> str:
    """Chat using OpenAI API"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        raise


def chat_with_anthropic(prompt: str, model: str, history: Optional[List[Dict]] = None) -> str:
    """Chat using Anthropic API"""
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Convert history to Anthropic format
        messages = []
        if history:
            for msg in history:
                messages.append({
                    "role": msg["role"] if msg["role"] != "assistant" else "assistant",
                    "content": msg["content"]
                })
        messages.append({"role": "user", "content": prompt})
        
        response = client.messages.create(
            model=model,
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.content[0].text
        
    except Exception as e:
        logger.error(f"Anthropic error: {e}")
        raise


def chat_with_google(prompt: str, model: str, history: Optional[List[Dict]] = None) -> str:
    """Chat using Google Generative AI"""
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model_instance = genai.GenerativeModel(model)
        
        # Build conversation history
        chat_history = ""
        if history:
            for msg in history:
                role = "Human" if msg["role"] == "user" else "Assistant"
                chat_history += f"{role}: {msg['content']}\n"
        
        full_prompt = chat_history + f"Human: {prompt}\nAssistant:"
        
        response = model_instance.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Google AI error: {e}")
        raise
