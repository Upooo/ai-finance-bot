TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_group_info",
            "description": "Mendapatkan informasi group Telegram.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_group_admins",
            "description": "Mendapatkan daftar admin group.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "promote_user",
            "description": "Jadikan user sebagai admin group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "Telegram user ID target.",
                    }
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "demote_user",
            "description": "Hapus status admin user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ban_user",
            "description": "Ban user dari group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unban_user",
            "description": "Buka ban user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mute_user",
            "description": "Mute user sehingga tidak bisa kirim pesan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Durasi mute dalam menit. Default 10.",
                    },
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unmute_user",
            "description": "Unmute user agar bisa kirim pesan lagi.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_message",
            "description": "Hapus pesan tertentu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "integer"}
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_invite_link",
            "description": "Buat invite link group.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pin_message",
            "description": "Pin pesan di group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "integer"}
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unpin_message",
            "description": "Unpin pesan. Tanpa message_id = unpin semua.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "integer",
                        "description": "ID pesan. Kosongkan untuk unpin semua.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_chat_title",
            "description": "Ganti judul/nama group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Judul baru group.",
                    }
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_chat_description",
            "description": "Ganti deskripsi group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Deskripsi baru.",
                    }
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "warn_user",
            "description": "Beri warning ke user yang melanggar aturan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "reason": {
                        "type": "string",
                        "description": "Alasan warning.",
                    },
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_warnings",
            "description": "Cek jumlah warning user (24 jam terakhir).",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"}
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_strict_mode",
            "description": "Aktifkan/nonaktifkan mode tegas (moderasi otomatis group).",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "true = aktif, false = nonaktif.",
                    }
                },
                "required": ["enabled"],
            },
        },
    },
]
