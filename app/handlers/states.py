from aiogram.fsm.state import State, StatesGroup

class WebsiteUrl(StatesGroup):
	url = State()
