import base64
import os
import requests
import time

from io import BytesIO
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

CHROME_DRIVER_LOCATION = r'/home/bobby/selinium-driver/chromedriver.exe'
SEARCH_TERMS = ['mit', 'ifhtp']
TARGET_SAVE_LOCATION = os.path.join(r'pictures/test', '_'.join([x.capitalize() for x in SEARCH_TERMS]),  r'{}.{}')
if not os.path.isdir(os.path.dirname(TARGET_SAVE_LOCATION)):
    os.makedirs(os.path.dirname(TARGET_SAVE_LOCATION))

def check_if_result_b64(source):
    possible_header = source.split(',')[0]
    if possible_header.startswith('data') and ';base64' in possible_header:
        image_type = possible_header.replace('data:image/', '').replace(';base64', '')
        return image_type
    return False

def get_driver():

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/80.0.3987.132 Safari/537.36'
    options = Options()
    #options.add_argument("--headless") #Uncomment if you don't want the browser GUI to pop up
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--allow-cross-origin-auth-prompt")

    new_driver = webdriver.Chrome(executable_path=CHROME_DRIVER_LOCATION, options=options)
    new_driver.get(f"https://www.google.com/search?q={'+'.join(SEARCH_TERMS)}&source=lnms&tbm=isch&sa=X")
    return new_driver



driver = get_driver()

first_search_result = driver.find_elements_by_xpath('//a/div/img')[0]
first_search_result.click()

right_panel_base = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'''//*[@data-query="{' '.join(SEARCH_TERMS)}"]''')))
first_image = right_panel_base.find_elements_by_xpath('//*[@data-noaft="1"]')[0]
magic_class = first_image.get_attribute('class')
image_finder_xp = f'//*[@class="{magic_class}"]'


# initial wait for the first image to be loaded
# this part could be improved but I couldn't find a proper way of doing it
time.sleep(3)

# initial thumbnail for "to_be_loaded image"
thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")

for i in range(10):

    # issue 4: All image elements share the same class. Assuming that you always click "next":
    # The last element is the base64 encoded thumbnail version is of the "next image"
    # [-2] element is the element currently displayed
    target = driver.find_elements_by_xpath(image_finder_xp)[-2]

    # you need to wait until image is completely loaded:
    # first the base64 encoded thumbnail will be displayed
    # so we check if the displayed element src match the cached thumbnail src.
    # However sometimes the final result is the base64 content, so wait is capped
    # at 5 seconds.
    wait_time_start = time.time()
    while (target.get_attribute("src") == thumbnail_src) and time.time() < wait_time_start + 5:
        time.sleep(0.2)
    thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")
    attribute_value = target.get_attribute("src")




    print(attribute_value)



    # issue 1: if the image is base64, requests get won't work because the src is not an url

    is_b64 = check_if_result_b64(attribute_value)
    if is_b64:
        image_format = is_b64
        content = base64.b64decode(attribute_value.split(';base64')[1])
    else:
        resp = requests.get(attribute_value, stream=True)
        temp_for_image_extension = BytesIO(resp.content)
        image = Image.open(temp_for_image_extension)
        image_format = image.format
        content = resp.content
    # issue 2: if you 'open' a file, later you have to close it. Use a "with" pattern instead
    with open(TARGET_SAVE_LOCATION.format(i, image_format), 'wb') as f:
        f.write(content)
    # issue 3: this Xpath is bad """//*[@id="Sva75c"]/div/div/div[3]/div[2]/div/div[1]/div[1]/div/div[1]/a[2]/div""" if page layout changes, this path breaks instantly
    svg_arrows_xpath = '//div[@jscontroller]//a[contains(@jsaction, "click:trigger")]//*[@viewBox="0 0 24 24"]'
    next_arrow = driver.find_elements_by_xpath(svg_arrows_xpath)[-3]
    next_arrow.click()
