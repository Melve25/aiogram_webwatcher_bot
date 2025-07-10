from aiogram import Dispatcher

from app.handlers.handlers import router

def register_all_routers(dp: Dispatcher):
	dp.include_router(router)