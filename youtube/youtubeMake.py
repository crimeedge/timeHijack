import google_auth_oauthlib
import googleapiclient.discovery
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from driverMethods import create_driver


def get_api_service(key=None):
    api_service_name = "youtube"
    api_version = "v3"
    if not key:
        key = open('.credsAPIKey').readlines()[0].strip()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=key)
    return youtube