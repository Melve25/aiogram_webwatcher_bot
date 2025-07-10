from pydantic import BaseModel, HttpUrl
import aiohttp

class WebsiteUrlModel(BaseModel):
	url: HttpUrl

async def is_website_alive(url: str) -> bool:
	try:
		timeout = aiohttp.ClientTimeout(total=5)
		async with aiohttp.ClientSession(timeout=timeout) as session:
			async with session.get(url) as response:
				return response.status == 200
	except Exception as e:
		print(e)
		return False