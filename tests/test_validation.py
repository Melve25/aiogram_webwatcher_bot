import pytest
from pytest_mock import MockerFixture
from app.services.validation import is_website_alive

pytestmark = pytest.mark.asyncio

async def test_is_website_alive_success(mocker: MockerFixture):
	mock_response = mocker.AsyncMock()
	mock_response.status = 200

	mock_session_get = mocker.AsyncMock()
	mock_session_get.__aenter__.return_value = mock_response

	mocker.patch('aiohttp.ClientSession.get', return_value=mock_session_get)

	assert await is_website_alive('https://google.com') is True

async def test_is_website_alive_failure(mocker: MockerFixture):
	mock_response = mocker.AsyncMock()
	mock_response.status = 404

	mock_session_get = mocker.AsyncMock()
	mock_session_get.__aenter__.return_value = mock_response

	mocker.patch('aiohttp.ClientSession.get', return_value=mock_session_get)

	assert await is_website_alive('https://nonexistlink.com') is False