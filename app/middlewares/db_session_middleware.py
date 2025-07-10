from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import TelegramObject

from app.db.database import AsyncSessionLocal

class DbSessionMiddleware(BaseMiddleware):
	async def __call__(
			self,
			handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
			event: TelegramObject,
			data: Dict[str, Any]) -> Any:
		async with AsyncSessionLocal() as session:
			data['session'] = session
			result = await handler(event, data)
			return result