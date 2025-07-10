from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import asyncio

async def take_screenshot(url: str) -> bytes | None:
	"""
	Заходит на сайт и делает скриншот.
	Возвращает скриншот в виде байтов или None в случае ошибки.
	"""
	chrome_options = Options()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')

	# NOTE: ON COMPUTER
	# driver = webdriver.Chrome(options=chrome_options)
	
	# NOTE: ON DOCKER
	driver = webdriver.Remote(
		command_executor='http://selenium_chrome:4444/wd/hub',
		options=chrome_options
	)

	try: 
		driver.get(url)
		WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.TAG_NAME, 'body'))
		)
		await asyncio.sleep(1)
		screenshot = driver.get_screenshot_as_png()
		return screenshot
	except Exception as e:
		print(f'Error taking screenshot for{url}: {e}')
		return None
	finally:
		driver.quit()