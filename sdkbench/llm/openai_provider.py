"""OpenAI provider for SDK-Bench."""

from typing import Optional, Dict, Any
import time
import os
from .base import LLMProvider, LLMResponse, LLMConfig


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
        "gpt-4-1106-preview": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-4-32k": {"input": 60.00, "output": 120.00},
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-3.5-turbo-16k": {"input": 3.00, "output": 4.00},
    }

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI provider.

        Args:
            config: LLM configuration
        """
        # Use environment variable if API key not provided
        if not config.api_key:
            config.api_key = os.getenv("OPENAI_API_KEY")

        super().__init__(config)

        # Import OpenAI SDK
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url if config.base_url else None
            )
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Generate a response from OpenAI.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context

        Returns:
            LLMResponse object with generation details
        """
        start_time = time.time()

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Make API call
        try:
            # For newer models like gpt-5.1, use max_completion_tokens instead of max_tokens
            kwargs = {
                "model": self.config.model,
                "messages": messages,
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
            }

            # Try with max_completion_tokens first for newer models
            if "gpt-5" in self.config.model or "2025" in self.config.model:
                kwargs["max_completion_tokens"] = self.config.max_tokens
            else:
                kwargs["max_tokens"] = self.config.max_tokens

            response = self.client.chat.completions.create(**kwargs)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Extract token usage
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            # Calculate cost
            cost = self.calculate_cost(prompt_tokens, completion_tokens)

            # Extract content
            content = response.choices[0].message.content if response.choices else ""

            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                finish_reason=response.choices[0].finish_reason if response.choices else "stop",
                cost=cost,
                latency_ms=latency_ms,
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")

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
        """Calculate cost based on OpenAI pricing.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Cost in USD
        """
        # Don't validate model names - allow any model to be used
        # If model not in PRICING, just return 0.0 for cost calculation
        if self.config.model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[self.config.model]
        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost