import google_auth_oauthlib
import googleapiclient.discovery
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from driverMethods import create_driver
import pyperclip

default_scope = ["https://www.googleapis.com/auth/youtube"]

# global flow allows for modularization bypassing variable
flow = None

def get_api_service(key=None):
    api_service_name = "youtube"
    api_version = "v3"
    if not key:
        key = open('.credsAPIKey').readlines()[0].strip()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=key)
    return youtube



def get_authenticated_service(scopes=default_scope):
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "o.json"
    global flow
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    # credentials = _run_selenium(flow)
    credentials = _run_selenium(flow)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    return youtube


def _run_selenium(flow, **kwargs):
    kwargs.setdefault('prompt', 'consent')
    flow.redirect_uri = flow._OOB_REDIRECT_URI

    auth_url, _ = flow.authorization_url(**kwargs)

    driver = create_driver()
    driver.get(auth_url)
    WebDriverWait(driver, 60).until(_run_selenium2)
    driver.quit()
    return flow.credentials

# horrible call function that bashes fetch until copipe succeeds
def _run_selenium2(driver):
    try:
        codee=pyperclip.paste()
        global flow
        flow.fetch_token(code=codee)
        print(codee)
        return True
    except BaseException as e:
        print(e)
        return False