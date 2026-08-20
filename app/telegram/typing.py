import asyncio

from aiogram import Bot
from aiogram.enums import ChatAction


class TypingManager:
    """Send TYPING action while the bot is thinking."""

    def __init__(self, bot: Bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id
        self._task = None
        self._running = False

    async def _loop(self):
        while self._running:
            try:
                await self.bot.send_chat_action(
                    chat_id=self.chat_id,
                    action=ChatAction.TYPING,
                )
            except Exception:
                pass
            await asyncio.sleep(4)

    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
