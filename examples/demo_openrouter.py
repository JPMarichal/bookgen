#!/usr/bin/env python3
"""
Demo script for OpenRouter API Client
Shows basic usage and features of the OpenRouter integration
"""
from src.services.openrouter_client import OpenRouterClient, OpenRouterException
from src.config.openrouter_config import OpenRouterConfig


def main():
    """Demo of OpenRouter client usage"""
    
    print("=" * 60)
    print("OpenRouter API Client Demo")
    print("=" * 60)
    
    # Initialize client (uses environment variables by default)
    print("\n1. Initializing client...")
    try:
        client = OpenRouterClient()
        print(f"   ✓ Client initialized with model: {client.config.model}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        print("   Please set OPENROUTER_API_KEY environment variable")
        return
    
    # Basic text generation
    print("\n2. Testing text generation...")
    try:
        response = client.generate_text(
            prompt="Say hello in a creative way",
            max_tokens=50
        )
        print(f"   Response: {response[:100]}...")
    except OpenRouterException as e:
        print(f"   ✗ Error: {e}")
        print("   (This is expected if API key is invalid)")
    
    # Text generation with system prompt
    print("\n3. Testing with system prompt...")
    try:
        response = client.generate_text(
            prompt="Explain AI in one sentence",
            system_prompt="You are a helpful technical assistant",
            temperature=0.5
        )
        print(f"   Response: {response[:100]}...")
    except OpenRouterException as e:
        print(f"   ✗ Error: {e}")
    
    # Get usage statistics
    print("\n4. Usage statistics:")
    stats = client.get_usage_stats()
    print(f"   Total requests: {stats['requests']}")
    print(f"   Successful: {stats['successful_requests']}")
    print(f"   Failed: {stats['failed_requests']}")
    print(f"   Total tokens used: {stats['total_tokens']}")
    print(f"   Success rate: {stats['success_rate'] * 100:.1f}%")
    
    # Streaming example (commented out as it requires valid API)
    print("\n5. Streaming support available:")
    print("   Use client.generate_text_streaming() for long responses")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
