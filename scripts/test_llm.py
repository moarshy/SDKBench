#!/usr/bin/env python3
"""Test LLM integration with a sample task."""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sdkbench.llm import LLMConfig, AnthropicProvider, OpenAIProvider
from sdkbench.llm.prompt_builder import PromptBuilder
from sdkbench.llm.solution_generator import SolutionGenerator


def test_prompt_builder():
    """Test prompt building from metadata."""
    print("Testing Prompt Builder...")

    # Use a sample task
    sample_dir = Path("samples/task1_init_001")
    metadata_path = sample_dir / "expected" / "metadata.json"
    input_dir = sample_dir / "input"

    if not metadata_path.exists():
        print(f"❌ Sample not found: {metadata_path}")
        return False

    # Build prompt
    builder = PromptBuilder()
    system_prompt, user_prompt = builder.build_from_metadata(metadata_path, input_dir)

    print("✅ System prompt generated:")
    print(f"   Length: {len(system_prompt)} chars")
    print(f"   First 100 chars: {system_prompt[:100]}...")

    print("✅ User prompt generated:")
    print(f"   Length: {len(user_prompt)} chars")
    print(f"   First 100 chars: {user_prompt[:100]}...")

    return True


def test_solution_extraction():
    """Test solution file extraction from mock LLM response."""
    print("\nTesting Solution Extraction...")

    # Mock LLM response
    mock_response = """I'll help you add Clerk authentication to your Next.js application.

// filepath: app/layout.tsx
```typescript
import { ClerkProvider } from '@clerk/nextjs'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>{children}</body>
      </html>
    </ClerkProvider>
  )
}
```

// filepath: .env.local
```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_secret_here
```

This implementation wraps your application with the ClerkProvider component."""

    # Test extraction
    generator = SolutionGenerator()
    files = generator._extract_files_from_response(mock_response)

    print(f"✅ Extracted {len(files)} files:")
    for filepath, content in files.items():
        print(f"   - {filepath}: {len(content)} chars")

    return len(files) == 2


def test_llm_provider():
    """Test LLM provider with a simple prompt."""
    print("\nTesting LLM Provider (Mock Mode)...")

    # Create mock provider test
    class MockProvider:
        def __init__(self):
            self.config = LLMConfig(
                model="mock-model",
                temperature=0.1,
                max_tokens=1000,
                api_key="mock-key"
            )

        def generate(self, prompt, system_prompt=None):
            """Mock generation."""
            from sdkbench.llm.base import LLMResponse

            return LLMResponse(
                content="Mock response for testing",
                model="mock-model",
                tokens_used=100,
                prompt_tokens=50,
                completion_tokens=50,
                finish_reason="stop",
                cost=0.01,
                latency_ms=500.0
            )

    # Test mock provider
    provider = MockProvider()
    response = provider.generate("Test prompt", "Test system prompt")

    print(f"✅ Mock provider works:")
    print(f"   Model: {response.model}")
    print(f"   Tokens: {response.tokens_used}")
    print(f"   Cost: ${response.cost}")
    print(f"   Latency: {response.latency_ms}ms")

    return True


def test_full_pipeline():
    """Test the full pipeline with mock data."""
    print("\nTesting Full Pipeline...")

    # Create temp directory for output
    output_dir = Path("temp_test_output")
    output_dir.mkdir(exist_ok=True)

    try:
        # Generate mock solution
        generator = SolutionGenerator()
        mock_response = """
// filepath: app/test.tsx
```typescript
export default function Test() {
  return <div>Test Component</div>
}
```
"""
        solution_dir = generator.generate_solution(
            mock_response,
            output_dir,
            "test_sample",
            "mock_model"
        )

        print(f"✅ Solution generated at: {solution_dir}")

        # Check files were created
        files_created = list(solution_dir.rglob('*'))
        print(f"   Files created: {len(files_created)}")
        for f in files_created:
            if f.is_file():
                print(f"   - {f.relative_to(solution_dir)}")

        return True

    finally:
        # Cleanup
        import shutil
        if output_dir.exists():
            shutil.rmtree(output_dir)


def main():
    """Run all tests."""
    print("=" * 60)
    print("SDK-Bench LLM Integration Test")
    print("=" * 60)

    tests = [
        test_prompt_builder,
        test_solution_extraction,
        test_llm_provider,
        test_full_pipeline
    ]

    results = []
    for test in tests:
        try:
            success = test()
            results.append(success)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)

    test_names = [
        "Prompt Builder",
        "Solution Extraction",
        "LLM Provider",
        "Full Pipeline"
    ]

    for name, result in zip(test_names, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")

    total_passed = sum(results)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("🎉 All LLM integration tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Please fix before continuing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())