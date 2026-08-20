import json
import re

from groq import AsyncGroq

from app.ai.prompts import (
    PRIVATE_PROMPT,
    GROUP_PROMPT,
    MODERATION_CHECK_PROMPT,
)
from app.ai.tools import TOOLS
from app.storage.memory import get_history


DEFAULT_MODEL = "openai/gpt-oss-120b"
MAX_TOOL_ROUNDS = 5


class AIAgent:

    def __init__(self, api_key: str, model: str = None):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model or DEFAULT_MODEL

    async def chat(
        self,
        text: str,
        context: dict,
        chat_id: int,
        execute_tool_fn=None,
    ) -> str:
        """Multi-turn agent loop. Returns final text response."""

        is_group = context.get("chat", {}).get("type") in [
            "group",
            "supergroup",
        ]
        system_prompt = GROUP_PROMPT if is_group else PRIVATE_PROMPT

        context_str = json.dumps(context, ensure_ascii=False, indent=2)

        # Get chat history
        history = await get_history(chat_id)

        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]

        # Add history (skip last entry — it is the current message)
        for msg in history[:-1] if history else []:
            messages.append(msg)

        # Current message with full Telegram context
        user_content = (
            f"TELEGRAM CONTEXT:\n{context_str}\n\n"
            f"USER MESSAGE:\n{text}"
        )
        messages.append({"role": "user", "content": user_content})

        # ---- Agent loop ----
        for _round in range(MAX_TOOL_ROUNDS):
            try:
                kwargs = dict(
                    model=self.model,
                    messages=messages,
                    temperature=0.4,
                    max_tokens=1024,
                )
                if is_group:
                    kwargs["tools"] = TOOLS
                    kwargs["tool_choice"] = "auto"

                response = await self.client.chat.completions.create(
                    **kwargs
                )
            except Exception as e:
                print(f"[AI ERROR] {e}", flush=True)
                return "Maaf, lagi error nih. Coba lagi nanti ya."

            choice = response.choices[0]
            message = choice.message

            # No tool calls → return text
            if not message.tool_calls:
                return message.content or ""

            # Append assistant message with tool calls
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                }
            )

            # Execute each tool call
            for tc in message.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                print(f"[TOOL] {name} ARGS={args}", flush=True)

                if execute_tool_fn:
                    result = await execute_tool_fn(name, args)
                else:
                    result = {"error": "No tool executor"}

                print(f"[TOOL RESULT] {result}", flush=True)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(
                            result, ensure_ascii=False
                        ),
                    }
                )

        return "Maaf, terlalu banyak langkah. Coba perintah yang lebih sederhana."

    async def check_moderation(self, text: str) -> dict:
        """Lightweight content moderation check."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": MODERATION_CHECK_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": f"Pesan: {text}",
                    },
                ],
                temperature=0.1,
                max_tokens=150,
            )
            content = response.choices[0].message.content or "{}"
            # Extract JSON from response
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                result = json.loads(match.group())
            else:
                result = {}
            return {
                "category": result.get("category", "CLEAN"),
                "confidence": result.get("confidence", 0.0),
                "reason": result.get("reason", ""),
            }
        except Exception:
            return {
                "category": "CLEAN",
                "confidence": 0.0,
                "reason": "error",
            }
