import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from platform import system
import selenium.webdriver.support.expected_conditions as ec
from selenium.webdriver.common.by import By


def create_driver(with_data: bool = True, with_speed=False) -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument('--always-authorized-plugins=true')

    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

    if with_speed:
        chrome_options.add_argument('--disable-application-cache')
    if with_data:
        # chrome_options.add_argument("--user-data-dir=C:\\Users\\tarn\\workspace\\prontab\\chrome-data")
        chrome_options.add_argument("--user-data-dir=C:\\Users\\tarn\\AppData\\Local\\Google\\Chrome\\User Data")
        chrome_options.add_argument("profile-directory=Profile 1")
    if system().lower() == 'darwin':
        # driver = webdriver.Chrome('chromedriver', options=chrome_options)
        pass
    else:
        # driver = webdriver.Chrome( options=chrome_options)
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    return driver

