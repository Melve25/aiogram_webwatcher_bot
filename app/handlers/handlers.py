from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_marked_section, Bold

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.dao import get_or_create_user, add_website_for_user, get_user_websites, delete_user_website
from app.handlers.states import WebsiteUrl
from app.services.keyboards import inline_websites

router = Router()

# NOTE: приветствие
@router.message(Command('start'))
async def greeting_handler(message: Message, session: AsyncSession):
	await get_or_create_user(session=session, message=message)	
	await message.answer(f'Привет {message.from_user.first_name}')

# NOTE: получение данный о url сайта
@router.message(StateFilter(None), Command('add'))
async def add_website_handler(message: Message, state: FSMContext):
	await message.answer('Отправьте мне URL сайта, который нужно отслеживать')
	await state.set_state(WebsiteUrl.url)

@router.message(StateFilter('*'), Command('exit'))
async def exit_state_handler(message: Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		await message.answer("Я ничего от вас не жду мне нечего сбрасывать")
		return
	
	await state.clear()
	await message.answer("Чем могу помочь ещё?")

@router.message(WebsiteUrl.url, F.text)
async def get_url_handler(message: Message, session: AsyncSession, state:FSMContext):
	success, info = await add_website_for_user(session=session, message=message)

	if success:
		await state.update_data(url=info)
		await state.clear()
		await message.answer(f'Отлично я начал следить за сайтом {info}')
	else:
		await message.answer(info)

# NOTE: удаление сайта с базы
@router.message(Command('delete'))
async def delete_website_handler(message: Message, session: AsyncSession):
	websites = await get_user_websites(message=message, session=session)
	if not websites:
		await message.answer("❌ У тебя пока нет сайтов.")
		return
	
	await message.answer("Выбери сайт за которым больше не нужно следить: ", reply_markup=await inline_websites(websites))

@router.callback_query(F.data.startswith('delete:'))
async def delete_website_callback(callback: CallbackQuery, session: AsyncSession):
	
	website_to_delete_id: int = int(callback.data.split('delete:')[1])

	await delete_user_website(website_to_delete_id, session=session)
	
	await callback.answer('🗑️ Сайт удалён.')
	await callback.message.edit_text('Сайт успешно удалён ✅')


# NOTE: перечень сайтов пользователя
@router.message(Command('list'))
async def list_websites_handler(message: Message, session: AsyncSession):
	get_websites = await get_user_websites(message=message, session=session)
	websites = [website.url for website in get_websites]

	if not websites:
		await message.answer("❌ У тебя пока нет сайтов.")
		return
	
	content = as_marked_section(
		Bold("🌐 Твои сайты:\n"),
		*websites,
		marker="    🔗 "
	)
	text_to_answer = content.as_markdown()

	await message.answer(text_to_answer, parse_mode="Markdown")

#NOTE: объяснение что делает бот
@router.message(Command('help'))
async def help_handler(message: Message):
	await message.answer('Телеграм-бот, который следит за доступностью и внешним видом сайтов')