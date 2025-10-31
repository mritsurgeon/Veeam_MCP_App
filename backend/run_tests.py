#!/usr/bin/env python3
"""Run the LLM adapter test harness.

This script validates connections to different LLM providers.
You can run it with specific providers or test all available providers.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_harness import AdapterTestHarness


async def main():
    """Main entry point for test harness."""
    print("Starting LLM Adapter Test Harness...")
    print("=" * 80)

    harness = AdapterTestHarness()

    # Load configurations from environment or config file
    configs = {}

    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        configs["openai"] = {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        }
        print("✓ OpenAI API key found")

    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        configs["anthropic"] = {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        }
        print("✓ Anthropic API key found")

    # Ollama (no API key needed, but check if server is accessible)
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    configs["ollama"] = {
        "model": os.getenv("OLLAMA_MODEL", "llama2"),
        "base_url": ollama_url,
    }
    print(f"✓ Ollama configured for {ollama_url}")

    if not configs:
        print("\n⚠️  No API keys found in environment variables.")
        print("Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or configure Ollama to test adapters.")
        print("\nExample:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  python run_tests.py")
        return

    print(f"\nTesting {len(configs)} provider(s)...\n")

    # Test all configured providers
    results = await harness.test_all_adapters(configs)

    # Print results
    harness.print_results()

    # Summary
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful

    print(f"\nSummary: {successful} successful, {failed} failed")


if __name__ == "__main__":
    asyncio.run(main())

