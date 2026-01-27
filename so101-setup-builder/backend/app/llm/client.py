from typing import Any

from app.config import get_settings

settings = get_settings()


class GeminiClient:
    """Client for Google Gemini API."""

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self.api_key = settings.gemini_api_key
        self._client = None

    def _get_client(self):
        """Lazy initialization of Gemini client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not configured")

            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package not installed")

        return self._client

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response from the model."""
        client = self._get_client()

        # Build full prompt with system context
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            response = client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )
            return response.text

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Have a conversation with the model."""
        client = self._get_client()

        try:
            # Start chat session
            chat = client.start_chat(history=self._format_history(history))

            # Add system prompt as first message if provided
            if system_prompt and not history:
                chat.send_message(f"System: {system_prompt}")

            response = chat.send_message(
                message,
                generation_config={"temperature": temperature},
            )
            return response.text

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")

    def _format_history(
        self,
        history: list[dict[str, str]] | None,
    ) -> list[dict[str, Any]]:
        """Format history for Gemini API."""
        if not history:
            return []

        formatted = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            formatted.append({
                "role": role,
                "parts": [msg.get("content", "")],
            })
        return formatted

    async def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Generate response with function calling."""
        client = self._get_client()

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        try:
            response = client.generate_content(
                full_prompt,
                tools=tools,
            )

            # Check for function calls
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call"):
                        return {
                            "type": "function_call",
                            "name": part.function_call.name,
                            "args": dict(part.function_call.args),
                        }

            return {
                "type": "text",
                "content": response.text,
            }

        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
