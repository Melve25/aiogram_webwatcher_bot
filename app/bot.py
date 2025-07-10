import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import settings
from app.services.commands import all_commands
from app.services.scheduler import check_websites
from app.handlers import register_all_routers
from app.middlewares.db_session_middleware import DbSessionMiddleware

# aiohttp - conf
# WEBHOOK_PATH = '/webhook'
# WEBHOOK_URL = f'https://33e2-46-251-196-144.ngrok-free.app{WEBHOOK_PATH}'
# WEB_SERVER_HOST = '0.0.0.0'
# WEB_SERVER_PORT = 8080

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

async def on_startup(bot: Bot):
	"""Выполняется при старте, устанавливает вебхук."""
	# await bot.send_webhook(url=WEBHOOK_URL)
	await bot.delete_webhook(drop_pending_updates=True)
	await bot.delete_my_commands()
	await bot.set_my_commands(commands=all_commands)

async def main():
	dp.callback_query.middleware(DbSessionMiddleware())
	dp.message.middleware(DbSessionMiddleware())
	register_all_routers(dp)

	scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
	scheduler.add_job(check_websites, 'interval', minutes=1, args=(bot,))
	scheduler.start()
	
	dp.startup.register(on_startup)

	await dp.start_polling(bot)

	# app = web.Application()

	# webhook_requests_handler = SimpleRequestHandler(
	# 	dispatcher=dp,
	# 	bot=bot
	# )
	# webhook_requests_handler.register(app, path=WEBHOOK_PATH)
	# setup_application(app, dp, bot=bot)
	
	# runner = web.AppRunner(app)
	# await runner.setup()
	# site = web.TCPSite(runner, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
	# await site.start()

	# await asyncio.Event().wait()


if __name__ == '__main__':
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		print('Exit from loop')
	
		
	