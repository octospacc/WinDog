# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

""" # windog config start # """

SeleniumDriversLimit = 2

""" # end windog config # """

currentSeleniumDrivers = []

from seleniumbase import Driver

# TODO implement some kind of timeout after a closure of a browser, since otherwise we get in a buggy state sometimes?

def getSelenium() -> tuple[int, Driver]|bool:
	if len(currentSeleniumDrivers) == SeleniumDriversLimit:
		return False
	for index in range(1, (SeleniumDriversLimit + 1)):
		if index not in currentSeleniumDrivers:
			currentSeleniumDrivers.append(index)
			break
	return (index, Driver(uc=True, headless2=True, user_data_dir=f"./Data/Selenium/{index}"))

def closeSelenium(index:int, driver:Driver) -> None:
	if driver:
		try:
			driver.close()
			driver.quit()
		except:
			app_log(format_exc())
	if index:
		currentSeleniumDrivers.remove(index)

def cDalleSelenium(context:EventContext, data:InputMessageData):
	warning_text = "has been blocked by Microsoft because it violates their content policy. Further attempts might lead to a ban on your profile. Please review the Code of Conduct for Image Creator in this picture or at https://www.bing.com/new/termsofuseimagecreator#content-policy."
	if not (prompt := data.command.body):
		return send_message(context, {"text_plain": "Please tell me what to generate."})
	driver_index, driver = None, None
	try:
		driver = getSelenium()
		if not driver:
			return send_message(context, {"text_plain": "Couldn't access a web scraping VM as they are all busy. Please try again later."})
		driver_index, driver = driver
		driver.get("https://www.bing.com/images/create/")
		driver.refresh()
		driver.find_element('form input[name="q"]').send_keys(prompt)
		driver.find_element('form a[role="button"]').submit()
		try:
			driver.find_element('img.gil_err_img[alt="Content warning"]')
			send_message(context, {"text_plain": f"Content warning: This prompt {warning_text}", "media": {"bytes": open("./Assets/ImageCreator-CodeOfConduct.png", 'rb').read()}})
			return closeSelenium(driver_index, driver)
		except Exception: # warning element was not found, we should be good
			pass
		send_message(context, {"text_plain": "Request sent successfully, please wait..."})
		retry_index = 3
		while retry_index < 12:
			# note that sometimes generation can still fail and we will never get any image!
			time.sleep(retry_index := retry_index + 1)
			driver.refresh()
			img_list = driver.find_elements('div.imgpt a img.mimg')
			if not len(img_list):
				try:
					driver.find_element('img.gil_err_img[alt="Unsafe image content detected"]')
					result = send_message(context, {"text_plain": f"Unsafe image content detected: This result {warning_text}", "media": {"bytes": open("./Assets/ImageCreator-CodeOfConduct.png", 'rb').read()}})
					closeSelenium(driver_index, driver)
					return result
				except: # no error is present, so we just have to wait more for the images
					continue
			img_array = []
			for img_url in img_list:
				img_url = img_url.get_attribute("src").split('?')[0]
				img_array.append({"url": img_url}) #, "bytes": HttpReq(img_url).read()})
			page_url = driver.current_url.split('?')[0]
			result = send_message(context, OutputMessageData(
				text_plain=f'"{prompt}"\n{{{page_url}}}',
				text_html=f'"<i>{html_escape(prompt)}</i>"\n<pre>{page_url}</pre>',
				media=img_array))
			closeSelenium(driver_index, driver)
			return result
		raise Exception("VM timed out.")
	except Exception as error:
		app_log(format_exc())
		result = send_message(context, {"text_plain": "An unexpected error occurred."})
		closeSelenium(driver_index, driver)
		return result

def cCraiyonSelenium(context:EventContext, data:InputMessageData):
	if not (prompt := data.command.body):
		return send_message(context, {"text_plain": "Please tell me what to generate."})
	driver_index, driver = None, None
	try:
		driver = getSelenium()
		if not driver:
			return send_message(context, {"text_plain": "Couldn't access a web scraping VM as they are all busy. Please try again later."})
		driver_index, driver = driver
		driver.get("https://www.craiyon.com/")
		driver.find_element('textarea#prompt').send_keys(prompt)
		driver.execute_script("arguments[0].click();", driver.find_element('button#generateButton'))
		send_message(context, {"text_plain": "Request sent successfully, please wait up to 60 seconds..."})
		retry_index = 3
		while retry_index < 16:
			time.sleep(retry_index := retry_index + 1)
			img_list = driver.find_elements('div.image-container > img')
			if not len(img_list):
				continue
			img_array = []
			for img_elem in img_list:
				img_array.append({"url": img_elem.get_attribute("src")}) #, "bytes": HttpReq(img_url).read()})
			result = send_message(context, {
				"text_plain": f'"{prompt}"',
				"text_html": f'"<i>{html_escape(prompt)}</i>"',
				"media": img_array,
			})
			closeSelenium(driver_index, driver)
			return result
		raise Exception("VM timed out.")
	except Exception as error:
		app_log(format_exc())
		result = send_message(context, {"text_plain": "An unexpected error occurred."})
		closeSelenium(driver_index, driver)
		return result

register_module(name="Scrapers", endpoints=[
	SafeNamespace(names=["dalle"], handler=cDalleSelenium, body=True),
	SafeNamespace(names=["craiyon", "crayion"], handler=cCraiyonSelenium, body=True),
])

