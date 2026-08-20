TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_group_info",
            "description": "Mendapatkan informasi group Telegram termasuk jumlah member.",
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
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "demote_user",
            "description": "Cabut admin user dari group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
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
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unban_user",
            "description": "Unban user dari group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mute_user",
            "description": "Mute user di group. Bisa set durasi dalam menit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                    "duration_minutes": {"type": "integer", "description": "Durasi mute dalam menit (default 10)."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unmute_user",
            "description": "Unmute user di group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_message",
            "description": "Hapus pesan di group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_id": {"type": "integer", "description": "ID pesan yang mau dihapus."},
                },
                "required": ["message_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_invite_link",
            "description": "Buat link undangan group.",
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
                    "message_id": {"type": "integer", "description": "ID pesan yang mau di-pin."},
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
                    "message_id": {"type": "integer", "description": "ID pesan (opsional, kosong = unpin semua)."},
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
                    "title": {"type": "string", "description": "Judul baru group."},
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
                    "description": {"type": "string", "description": "Deskripsi baru group."},
                },
                "required": ["description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "warn_user",
            "description": "Kasih warning ke user yang melanggar aturan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                    "reason": {"type": "string", "description": "Alasan warning."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_warnings",
            "description": "Cek jumlah warning user dalam 24 jam terakhir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_warnings",
            "description": "Reset semua warning user di group ini.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Telegram user ID target."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_strict_mode",
            "description": "Aktifkan/matikan mode tegas (moderasi otomatis).",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "true = aktif, false = nonaktif."},
                },
                "required": ["enabled"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_chat_mode",
            "description": "Aktifkan/matikan mode ngobrol (bot tetap nyambung di topik yang sama setelah dipanggil).",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "true = aktif, false = nonaktif."},
                },
                "required": ["enabled"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "toggle_nimbrung",
            "description": "Aktifkan/matikan mode nimbrung (bot proaktif ikut obrolan tanpa dipanggil).",
            "parameters": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "true = aktif, false = nonaktif."},
                },
                "required": ["enabled"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_voice_chat",
            "description": "Buka/mulai obrolan suara (voice chat) di group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Judul voice chat (opsional)."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_voice_chat",
            "description": "Tutup/akhiri obrolan suara (voice chat) di group.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_member_count",
            "description": "Cek jumlah anggota group.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_poll",
            "description": "Buat polling di group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Pertanyaan polling."},
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Daftar pilihan jawaban (min 2, max 10).",
                    },
                    "is_anonymous": {"type": "boolean", "description": "Anonim atau tidak (default true)."},
                },
                "required": ["question", "options"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_slow_mode",
            "description": "Set slow mode delay di group (dalam detik, 0 = matikan).",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "description": "Delay dalam detik (0, 10, 30, 60, 300, 900, 3600)."},
                },
                "required": ["seconds"],
            },
        },
    },
]
