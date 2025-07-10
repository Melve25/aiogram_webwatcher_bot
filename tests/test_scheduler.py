import pytest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path


from app.db.models import Website
from app.services.scheduler import check_websites

pytestmark = pytest.mark.asyncio

async def test_check_website_success(mocker: MockerFixture):
	test_folder = Path('tests/screenshots_test')
	test_folder.mkdir(exist_ok=True)
	mocker.patch('app.services.scheduler.SCREENSHOTS_PATH', test_folder)
	
	websites = [Website(url='https://google.com', user_id=1, id=1)]
	mocker.patch('app.services.scheduler.get_all_websites', return_value=websites)
	mocker.patch('app.services.scheduler.take_screenshot', return_value=b'binarydata')

	bot = mocker.AsyncMock()
	await check_websites(bot)

	saved_file = test_folder / '1.png'
	assert saved_file.exists()
	saved_file.unlink()
	test_folder.rmdir()

async def test_check_website_fail_no_screenshot(mocker: MockerFixture):
	test_folder = Path('tests/screenshots_test')
	test_folder.mkdir(exist_ok=True)
	mocker.patch('app.services.scheduler.SCREENSHOTS_PATH', test_folder)

	old_screenshot = test_folder / '1.png'
	old_screenshot.write_bytes(b'old binary data')

	user_mock = mocker.AsyncMock()
	user_mock.telegram_id = 1

	websites = [Website(url='https://google.com', user_id=1, id=1, user=user_mock)]
	mocker.patch('app.services.scheduler.get_all_websites', return_value=websites)
	mocker.patch('app.services.scheduler.take_screenshot', return_value=None)

	mocked_fsinputfile = mocker.patch('app.services.scheduler.FSInputFile')

	bot = mocker.AsyncMock()
	await check_websites(bot)
	
	mocked_fsinputfile.assert_called_once_with(old_screenshot)
	bot.send_photo.assert_called_once()

	old_screenshot.unlink()
	test_folder.rmdir()

async def test_check_website_fail_with_screenshot(mocker: MockerFixture):

	user_mock = mocker.AsyncMock()
	user_mock.telegram_id = 1

	websites = [Website(url='https://google.com', user_id=1, id=1, user=user_mock)]
	mocker.patch('app.services.scheduler.get_all_websites', return_value=websites)
	mocker.patch('app.services.scheduler.take_screenshot', return_value=None)

	bot = mocker.AsyncMock()
	await check_websites(bot)
	
	bot.send_message.assert_called_once()


