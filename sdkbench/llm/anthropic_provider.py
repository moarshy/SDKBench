"""Anthropic Claude provider for SDK-Bench."""

from typing import Optional, Dict, Any
import time
import os
from .base import LLMProvider, LLMResponse, LLMConfig


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
        "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},  # Claude Haiku 4.5
    }

    def __init__(self, config: LLMConfig):
        """Initialize Anthropic provider.

        Args:
            config: LLM configuration
        """
        super().__init__(config)

        # Use environment variable if API key not provided
        if not config.api_key:
            config.api_key = os.getenv("ANTHROPIC_API_KEY")

        # Import Anthropic SDK
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=config.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Install with: pip install anthropic"
            )

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from Claude.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            LLMResponse object with generation details
        """
        start_time = time.time()

        # Build messages
        messages = [{"role": "user", "content": prompt}]

        # Make API call
        try:
            # Claude Haiku 4.5 doesn't allow both temperature and top_p
            create_params = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
            }

            if system_prompt:
                create_params["system"] = system_prompt

            # Only add top_p if not using Haiku 4.5
            if "haiku-4-5" not in self.config.model:
                create_params["top_p"] = self.config.top_p

            response = self.client.messages.create(**create_params)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Extract token usage
            usage = response.usage if hasattr(response, 'usage') else None
            prompt_tokens = usage.input_tokens if usage else 0
            completion_tokens = usage.output_tokens if usage else 0
            total_tokens = prompt_tokens + completion_tokens

            # Calculate cost
            cost = self.calculate_cost(prompt_tokens, completion_tokens)

            # Extract content
            content = response.content[0].text if response.content else ""

            return LLMResponse(
                content=content,
                model=self.config.model,
                tokens_used=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=response.stop_reason if hasattr(response, 'stop_reason') else "stop",
                cost=cost,
                latency_ms=latency_ms,
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {str(e)}")

    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        validation_fn: Optional[callable] = None
    ) -> LLMResponse:
        """Generate with retry logic and optional validation.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            validation_fn: Optional function to validate response

        Returns:
            LLMResponse object
        """
        last_error = None

        for attempt in range(self.config.retry_count):
            try:
                # Generate response
                response = self.generate(prompt, system_prompt)

                # Validate if function provided
                if validation_fn:
                    if not validation_fn(response.content):
                        if attempt < self.config.retry_count - 1:
                            time.sleep(self.config.retry_delay * (attempt + 1))
                            continue
                        else:
                            raise ValueError("Response failed validation after all retries")

                return response

            except Exception as e:
                last_error = e
                if attempt < self.config.retry_count - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    continue

        raise RuntimeError(f"Failed after {self.config.retry_count} attempts: {last_error}")

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on Claude pricing.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Cost in USD
        """
        if self.config.model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[self.config.model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost