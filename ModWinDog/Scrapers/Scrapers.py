# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start # """

SeleniumDriversLimit = 2

""" # end windog config # """

currentSeleniumDrivers = 0

#from selenium import webdriver
#from selenium.webdriver import Chrome
#from selenium.webdriver.common.by import By
from seleniumbase import Driver

def getSelenium() -> Driver:
	global currentSeleniumDrivers
	if currentSeleniumDrivers >= SeleniumDriversLimit:
		return False
	#options = webdriver.ChromeOptions()
	#options.add_argument("headless=new")
	#options.add_argument("user-data-dir=./Selenium-WinDog")
	#seleniumDriver = Chrome(options=options)
	currentSeleniumDrivers += 1
	return Driver(uc=True, headless2=True, user_data_dir=f"./Selenium-WinDog/{currentSeleniumDrivers}")

def closeSelenium(driver:Driver) -> None:
	global currentSeleniumDrivers
	try:
		driver.close()
		driver.quit()
	except:
		Log(format_exc())
	if currentSeleniumDrivers > 0:
		currentSeleniumDrivers -= 1

def cDalleSelenium(context, data) -> None:
	if not data.Body:
		return SendMsg(context, {"Text": "Please tell me what to generate."})
	#if not seleniumDriver:
	#	SendMsg(context, {"Text": "Initializing Selenium, please wait..."})
	#	loadSeleniumDriver()
	try:
		driver = getSelenium()
		if not driver:
			return SendMsg(context, {"Text": "Couldn't access a web scraping VM as they are all busy. Please try again later."})
		driver.get("https://www.bing.com/images/create/")
		driver.refresh()
		#retry_index = 3
		#while retry_index < 12:
		#	time.sleep(retry_index := retry_index + 1)
		#	try:
		#seleniumDriver.find_element(By.CSS_SELECTOR, 'form input[name="q"]').send_keys(data.Body)
		#seleniumDriver.find_element(By.CSS_SELECTOR, 'form a[role="button"]').submit()
		driver.find_element('form input[name="q"]').send_keys(data.Body)
		driver.find_element('form a[role="button"]').submit()
		try:
			driver.find_element('img[alt="Content warning"]')
			SendMsg(context, {"Text": "This prompt has been blocked by Microsoft because it violates their content policy. Further attempts might lead to a ban on your profile."})
			closeSelenium(driver)
			return
		except Exception: # warning element was not found, we should be good
			pass
		SendMsg(context, {"Text": "Request sent successfully, please wait..."})
		#	except Exception:
		#		pass
		retry_index = 3
		while retry_index < 12:
			# note that sometimes generation fails and we will never get any image!
			#try:
			time.sleep(retry_index := retry_index + 1)
			driver.refresh()
			img_list = driver.find_elements(#By.CSS_SELECTOR, 
				'div.imgpt a img.mimg')
			if not len(img_list):
				continue
			img_array = []
			for img_url in img_list:
				img_url = img_url.get_attribute("src").split('?')[0]
				img_array.append({"url": img_url}) #, "bytes": HttpReq(img_url).read()})
			page_url = driver.current_url.split('?')[0]
			SendMsg(context, {
				"TextPlain": f'"{data.Body}"\n{{{page_url}}}',
				"TextMarkdown": (f'"_{CharEscape(data.Body, "MARKDOWN")}_"\n' + MarkdownCode(page_url, True)),
				"media": img_array,
			})
			closeSelenium(driver)
			break
			#except Exception as ex:
			#	pass
	except Exception as error:
		Log(format_exc())
		SendMsg(context, {"TextPlain": "An unexpected error occurred."})
		closeSelenium(driver)

RegisterModule(name="Scrapers", endpoints={
	"DALL-E": CreateEndpoint(["dalle"], summary="Sends an AI-generated picture from DALL-E 3 via Microsoft Bing.", handler=cDalleSelenium),
})

