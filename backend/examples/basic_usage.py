"""Example usage of LLM adapters.

This script demonstrates how to use the adapter system to interact
with different LLM providers.
"""

import asyncio
import os

from app.core.adapter_factory import AdapterFactory
from app.core.schemas import Message, MessageRole


async def example_openai():
    """Example: Using OpenAI adapter."""
    print("\n" + "=" * 80)
    print("OpenAI Example")
    print("=" * 80)

    try:
        # Create adapter
        config = {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
        }
        adapter = AdapterFactory.create("openai", config=config)

        # Create messages
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.USER, content="What is 2+2?"),
        ]

        # Send chat request
        response = await adapter.chat(messages, stream=False)
        print(f"\nResponse: {response.content}")
        print(f"Model: {response.model}")
        print(f"Tokens: {response.usage}")

        await adapter.close()

    except Exception as e:
        print(f"Error: {e}")


async def example_anthropic():
    """Example: Using Anthropic adapter."""
    print("\n" + "=" * 80)
    print("Anthropic Example")
    print("=" * 80)

    try:
        config = {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": "claude-3-5-sonnet-20241022",
            "base_url": "https://api.anthropic.com",
        }
        adapter = AdapterFactory.create("anthropic", config=config)

        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            Message(role=MessageRole.USER, content="Explain quantum computing in one sentence."),
        ]

        response = await adapter.chat(messages, stream=False)
        print(f"\nResponse: {response.content}")
        print(f"Model: {response.model}")

        await adapter.close()

    except Exception as e:
        print(f"Error: {e}")


async def example_ollama():
    """Example: Using Ollama adapter."""
    print("\n" + "=" * 80)
    print("Ollama Example")
    print("=" * 80)

    try:
        config = {
            "model": "llama2",
            "base_url": "http://localhost:11434",
        }
        adapter = AdapterFactory.create("ollama", config=config)

        # Check if Ollama is available
        is_healthy = await adapter.health_check()
        if not is_healthy:
            print("⚠️  Ollama server is not accessible. Is it running?")
            return

        # List available models
        models = await adapter.list_models()
        print(f"\nAvailable models: {models}")

        messages = [
            Message(role=MessageRole.USER, content="Hello! Can you introduce yourself?"),
        ]

        response = await adapter.chat(messages, stream=False)
        print(f"\nResponse: {response.content}")

        await adapter.close()

    except Exception as e:
        print(f"Error: {e}")


async def example_streaming():
    """Example: Streaming responses."""
    print("\n" + "=" * 80)
    print("Streaming Example (OpenAI)")
    print("=" * 80)

    try:
        config = {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
        }
        adapter = AdapterFactory.create("openai", config=config)

        messages = [
            Message(role=MessageRole.USER, content="Count from 1 to 5, one number per line."),
        ]

        print("\nStreaming response:")
        print("-" * 40)

        async for chunk in adapter.chat(messages, stream=True):
            if chunk.content:
                print(chunk.content, end="", flush=True)
            if chunk.finished:
                break

        print("\n" + "-" * 40)
        await adapter.close()

    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Run all examples."""
    print("LLM Adapter Usage Examples")
    print("=" * 80)

    # Check which providers are available
    if os.getenv("OPENAI_API_KEY"):
        await example_openai()
        await example_streaming()
    else:
        print("\n⚠️  OPENAI_API_KEY not set, skipping OpenAI examples")

    if os.getenv("ANTHROPIC_API_KEY"):
        await example_anthropic()
    else:
        print("\n⚠️  ANTHROPIC_API_KEY not set, skipping Anthropic examples")

    # Ollama doesn't need API key, just check if server is running
    await example_ollama()


if __name__ == "__main__":
    asyncio.run(main())

