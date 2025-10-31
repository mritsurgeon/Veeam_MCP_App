"""Test harness for validating LLM adapter connections.

This module provides utilities to test and validate connections
to different LLM providers without requiring full API credentials.
"""

import asyncio
from typing import Dict, List, Optional

from app.core.adapter_factory import AdapterFactory
from app.core.schemas import Message, MessageRole


class AdapterTestHarness:
    """Test harness for validating LLM adapter connections."""

    def __init__(self):
        """Initialize test harness."""
        self.results: List[Dict] = []

    async def test_adapter(
        self,
        provider: str,
        config: Optional[Dict] = None,
        model: Optional[str] = None,
        test_message: str = "Hello, can you respond with just 'OK'?",
    ) -> Dict:
        """Test a single adapter.

        Args:
            provider: Provider name.
            config: Optional provider config.
            model: Optional model name override.
            test_message: Test message to send.

        Returns:
            Dictionary with test results.
        """
        result = {
            "provider": provider,
            "model": model,
            "status": "unknown",
            "error": None,
            "response_time": None,
            "response_preview": None,
            "capabilities": None,
        }

        try:
            import time

            # Create adapter
            adapter = AdapterFactory.create(provider, config=config, model=model)
            result["model"] = adapter.config.model

            # Get capabilities
            capabilities = adapter.get_capabilities()
            result["capabilities"] = capabilities.dict()

            # Health check
            start_time = time.time()
            is_healthy = await adapter.health_check()
            health_check_time = time.time() - start_time

            if not is_healthy:
                result["status"] = "unhealthy"
                result["error"] = "Health check failed"
                return result

            # Test chat completion
            messages = [Message(role=MessageRole.USER, content=test_message)]
            start_time = time.time()
            response = await adapter.chat(messages, stream=False)
            response_time = time.time() - start_time

            result["status"] = "success"
            result["response_time"] = response_time
            result["response_preview"] = (
                response.content[:100] if response.content else None
            )

            # Cleanup
            await adapter.close()

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    async def test_all_adapters(
        self, configs: Optional[Dict[str, Dict]] = None
    ) -> List[Dict]:
        """Test all supported adapters.

        Args:
            configs: Optional dictionary mapping provider names to configs.

        Returns:
            List of test results for each provider.
        """
        providers = AdapterFactory.get_supported_providers()
        results = []

        for provider in providers:
            provider_config = configs.get(provider) if configs else None
            result = await self.test_adapter(provider, config=provider_config)
            results.append(result)
            self.results.append(result)

        return results

    def print_results(self):
        """Print test results in a readable format."""
        print("\n" + "=" * 80)
        print("LLM Adapter Test Results")
        print("=" * 80)

        for result in self.results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"\n{status_icon} {result['provider'].upper()}")
            print(f"   Model: {result.get('model', 'N/A')}")
            print(f"   Status: {result['status']}")

            if result["response_time"]:
                print(f"   Response Time: {result['response_time']:.2f}s")

            if result["capabilities"]:
                caps = result["capabilities"]
                print(f"   Streaming: {caps.get('supports_streaming', False)}")
                print(f"   Tools: {caps.get('supports_tools', False)}")

            if result["error"]:
                print(f"   Error: {result['error']}")

            if result["response_preview"]:
                print(f"   Preview: {result['response_preview']}...")

        print("\n" + "=" * 80)


async def main():
    """Main function for running test harness."""
    harness = AdapterTestHarness()

    # You can provide configs here or load from file
    configs = {
        # Example:
        # "openai": {
        #     "api_key": os.getenv("OPENAI_API_KEY"),
        #     "model": "gpt-4",
        # },
    }

    await harness.test_all_adapters(configs)
    harness.print_results()


if __name__ == "__main__":
    asyncio.run(main())

