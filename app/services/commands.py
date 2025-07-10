from aiogram.types import BotCommand

all_commands = [
	BotCommand(command='start', description='Регистрация'),
	BotCommand(command='add', description='добавить ссылку на сайт'),
	BotCommand(command='exit', description='выйти из любого состояния/вопроса'),
	BotCommand(command='delete', description='удаление сайтов'),
	BotCommand(command='list', description='список всех твоих сайтов'),
	BotCommand(command='help', description='описание бота')
]