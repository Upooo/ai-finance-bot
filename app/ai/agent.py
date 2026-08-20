import json

from groq import AsyncGroq


SYSTEM_PROMPT = """
Kamu adalah Idol AI, AI Assistant yang berjalan di Telegram.

Kamu dapat digunakan di:
1. PRIVATE CHAT
2. GROUP / SUPERGROUP

PRIVATE CHAT:
- Bantu user secara personal.
- Bisa ngobrol biasa.
- Jangan mengarang tindakan Telegram yang belum dilakukan.

GROUP CHAT:
- Kamu adalah AI Group Assistant.
- Kamu membantu pengelolaan group.
- Jika user meminta tindakan nyata dan tool tersedia, gunakan tool.
- Jangan hanya menjelaskan cara melakukannya.
- Jangan mengklaim tindakan berhasil sebelum tool berhasil.
- Jangan pernah mengarang Telegram user ID.

REPLY TARGET:
Jika user mengatakan:
- "dia"
- "orang ini"
- "adminin dia"
- "ban dia"
- "mute dia"
- "cabut admin dia"

dan tersedia REPLY TARGET, gunakan user_id dari reply tersebut.

Jangan mengarang user_id.

TOOLS:
- adminin → promote_user
- cabut admin / turunin → demote_user
- ban → ban_user
- unban → unban_user
- mute → mute_user
- unmute → unmute_user
- hapus pesan → delete_message
- siapa admin → get_group_admins
- info group → get_group_info
- ambil link group → create_invite_link

PERMISSION:
Kamu bukan Owner Telegram.
Tindakan tetap mengikuti permission Telegram user dan bot.

GAYA:
- Bahasa Indonesia natural.
- Santai.
- Cerdas.
- Tidak kaku.
- Bisa mengikuti gaya bicara user.
- Jawaban tidak perlu panjang.
"""


class AIAgent:

    def __init__(self, api_key: str):

        self.client = AsyncGroq(
            api_key=api_key
        )

        self.model = "openai/gpt-oss-120b"

    def get_tools(self):

        return [

            {
                "type": "function",
                "function": {
                    "name": "get_group_info",
                    "description": (
                        "Mendapatkan informasi "
                        "group Telegram."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "get_group_admins",
                    "description": (
                        "Mendapatkan daftar "
                        "owner dan administrator group."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "promote_user",
                    "description": (
                        "Menjadikan user sebagai "
                        "administrator group."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": (
                                    "Telegram user ID target."
                                ),
                            }
                        },
                        "required": [
                            "user_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "demote_user",
                    "description": (
                        "Menghapus status administrator "
                        "user."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "user_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "ban_user",
                    "description": (
                        "Ban user dari group."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "user_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "unban_user",
                    "description": (
                        "Membuka ban user."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "user_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "mute_user",
                    "description": (
                        "Mute user sehingga "
                        "tidak dapat mengirim pesan."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "user_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "unmute_user",
                    "description": (
                        "Mengembalikan kemampuan "
                        "user untuk mengirim pesan."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "user_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "delete_message",
                    "description": (
                        "Menghapus pesan tertentu."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "message_id"
                        ],
                    },
                },
            },

            {
                "type": "function",
                "function": {
                    "name": "create_invite_link",
                    "description": (
                        "Membuat invite link group."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                    },
                },
            },
        ]

    async def decide(
        self,
        text: str,
        context: dict,
    ):

        prompt = f"""
TELEGRAM CONTEXT:

{json.dumps(
    context,
    ensure_ascii=False,
    indent=2
)}

USER MESSAGE:

{text}
"""

        response = await self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            tools=self.get_tools(),

            tool_choice="auto",

            temperature=0.3,
        )

        message = response.choices[0].message

        if message.tool_calls:

            calls = []

            for tool_call in message.tool_calls:

                calls.append({
                    "name": tool_call.function.name,
                    "args": json.loads(
                        tool_call.function.arguments
                    ),
                })

            return {
                "type": "tool_calls",
                "calls": calls,
            }

        return {
            "type": "text",
            "text": message.content or "",
        }

    async def final_response(
        self,
        text: str,
        context: dict,
        results: list,
    ):

        prompt = f"""
USER MESSAGE:

{text}

TELEGRAM CONTEXT:

{json.dumps(
    context,
    ensure_ascii=False,
    indent=2
)}

TOOL RESULTS:

{json.dumps(
    results,
    ensure_ascii=False,
    indent=2
)}

Buat jawaban singkat dan natural.

Jika tindakan berhasil:
- Konfirmasi bahwa tindakan berhasil.

Jika tindakan gagal:
- Jelaskan kegagalannya secara jujur.

Jangan mengarang hasil.
"""

        response = await self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.3,
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        )
