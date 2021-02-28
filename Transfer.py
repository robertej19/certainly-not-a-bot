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

def nap(s=1):
   #sleep for 1 second to wait for things to load (not sure if necessary)
   print("sleeping")
   time.sleep(s)
   print("done sleeping")

CHROME_DRIVER_LOCATION = r'/home/bobby/selinium-driver/chromedriver.exe'

print("ChromeDriver Location is: {} (make sure this exists!!!)".format(CHROME_DRIVER_LOCATION))
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
    new_driver.get(f"https://www.sec.state.ma.us/wheredoivotema/bal/myelectioninfo.aspx?fbclid=IwAR1qpAdVVyaUsMwuMjLFbce0DpWwRlVSaa3wzr6vgASZDeeRmoK4nG-dX08")
    return new_driver



driver = get_driver()

s_no = "197"
s_name = "Clifton"
c_name = "Malden"
z_no = "02148"

print("entering info: {} {} {} {}".format(s_no, s_name, c_name, z_no))

street_no = driver.find_element_by_name("ctl00$MainContent$txtStreetNo")
street_no.send_keys(s_no)
#nap(1)

street_name = driver.find_element_by_name("ctl00$MainContent$txtStreetName")
street_name.send_keys(s_name)
#nap(0.25)

city_name = driver.find_element_by_name("ctl00$MainContent$ddlCityTown")
city_name.send_keys(c_name)
#nap(0.25)

zip_no = driver.find_element_by_name("ctl00$MainContent$txtZip")
zip_no.send_keys(z_no)
#nap(0.25)

search_button = driver.find_element_by_name("ctl00$MainContent$btnSearch")
search_button.click()

nap(1.5)

precinct_number = driver.find_element_by_id("MainContent_lblPrecinctNo")
print("Precint number for {} {} {} {} is {}".format(s_no, s_name, c_name, z_no, precinct_number.text))
