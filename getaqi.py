#
# https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages#installing-the-requirements
#
# Grab current AQI off a web page and send to InfluxDB
#
#
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


def AQIsetup():
    # start by defining the options
    options = webdriver.ChromeOptions()
    options.headless = True # it's more scalable to work in headless mode
    # normally, selenium waits for all resources to download
    # we don't need it as the page also populated with the running javascript code.
    options.page_load_strategy = 'none'
    # this returns the path web driver downloaded
    chrome_path = ChromeDriverManager().install()
    chrome_service = Service(chrome_path)
    # pass the defined options and service objects to initialize the web driver
    driver = Chrome(options=options, service=chrome_service)
    driver.implicitly_wait(5)
    return driver

def printAQI() -> int:
    driver = AQIsetup()

    url = "PAGEWITHPurpleAirWidget"
    driver.get(url)
    time.sleep(10)

    try:
        content = driver.find_element(By.ID,"currentConditions")

    except NoSuchElementException as e:
        print(str(e))
        exit(1)
    except Exception as e:
        print(e)
        exit(1)
    aqi = int(content.text.splitlines()[2])

    driver.close()

    return aqi

def sendAQI(x: int) -> None:
    bucket = "BUCKET" # fill these in with your values.
    org = "ORG"
    token = "TOKEN"
    url="URLWITHPORT"

    client = influxdb_client.InfluxDBClient(url=url,token=token,org=org)

    write_api = client.write_api(write_options=SYNCHRONOUS)

    p = influxdb_client.Point("aqi").tag("location", "glenview").field("value", x)

    write_api.write(bucket=bucket, org=org, record=p)

    return

def main():
    aqi = printAQI()
    sendAQI(aqi)
    exit(0)

if __name__ == "__main__":
    main()
