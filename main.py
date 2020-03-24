import os
import string
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Chrome
import random
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import zipfile


ip = '134.209.41.244'
port = 3128


def read_proxys():
    lines = []
    with open("proxies.txt", "r") as file:
        for line in file:
            lines.append(line)

    with open("proxies.txt", "r+") as file:
        for line in file:
            beegining_of_proxy = line[line.find("]") + 1:-2]
            global ip, port
            ip = beegining_of_proxy[0:beegining_of_proxy.find(":")]
            port = beegining_of_proxy[beegining_of_proxy.find(":") + 1:]
            lines.remove(line)
            break
        file.seek(0)
        file.truncate()
        for line in lines:
            file.write(line)


def get_chromedriver(use_proxy=False, user_agent=None):
    username = 'foo'
    password = 'bar'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%(ip)s",
                port: %(port)s
            }
            }
        }
    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%(username)s",
                password: "%(password)s"
            }
        }
    }
    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    )
    """ % {'ip': ip, 'port': port, 'username': username, 'password': password}

    plugin_file = 'proxy_auth_plugin.zip'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    chrome_options = Options()
    chrome_options.add_extension(plugin_file)
    chrome_options.add_argument("--window-size=500,500")
    driver = Chrome("C:\chromedriver.exe", options=chrome_options)
    return driver


def wait_for_element(driver, xpath):
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        print("Loading took too much time!")
        return False


def random_string(string_length=13):
    # Generate a random string of letters and digits
    letters_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_digits) for i in range(string_length))


class Website:
    def __init__(self, first, last, email):
        self.first = first
        self.last = last
        self.email = email
        self.url = "https://us.battle.net/account/creation/en/"
        self.is_good_proxy = False

        while not self.is_good_proxy:
            self.driver = get_chromedriver(True)
            self.driver.minimize_window()
            try:
                self.driver.set_page_load_timeout(80)
                self.driver.get(self.url)

                # check for internet
                try:
                    error = self.driver.find_element_by_class_name("error-code")
                    if error.text == "ERR_PROXY_CONNECTION_FAILED" or error.text == "DNS_PROBE_FINISHED_NO_INTERNET" or error.text == "ERR_NAME_NOT_RESOLVED" or error.text == "ERR_TUNNEL_CONNECTION_FAILED" or error.text == "ERR_EMPTY_RESPONSE":
                        print("No internet connection... retrying...")
                        self.driver.quit()
                        read_proxys()
                except NoSuchElementException:
                    print("Success, proxy is valid!")
                    self.is_good_proxy = True
            except TimeoutException as ex:
                print('Proxy took to long... retrying...')
                self.driver.quit()
                read_proxys()

    def log_account(self):
        with open('generated.txt', 'a') as file:
            file.write(web.email + ":" + "ThxNMan4!" + "\n")

    def create_account(self):
        self.driver.find_element_by_id("firstName").send_keys(self.first)
        self.driver.find_element_by_id("lastName").send_keys(self.last)
        self.driver.find_element_by_id("select-box-dobMonth").click()
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/fieldset[1]/div[3]/div[2]/div/div[1]/div/div[2]").click()
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/fieldset[1]/div[4]/input").send_keys("1")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/fieldset[1]/div[5]/input").send_keys("1990")
        self.driver.find_element_by_id("emailAddress").send_keys(self.email)
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/fieldset[2]/div[2]/input").send_keys("ThxNMan4!")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/fieldset[3]/div[1]/div[2]").click()
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/fieldset[3]/div[1]/div[2]/div/div[2]").click()
        self.driver.find_element_by_id("answer1").send_keys("Tundra")
        self.driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[1]/div[2]/div[2]/form[2]/div[1]/button").click()
        self.log_account()
        time.sleep(1)


read_proxys()

email = random_string(7)
email += "@protonmail.com"
first = random_string(13)
last = random_string(8)
web = Website(first, last, email)

i = 0
while i < 4:
    web.create_account()
    web.driver.get(web.url)

    email = random_string(7)
    email += "@protonmail.com"
    first = random_string(13)
    last = random_string(8)
    web.first = first
    web.last = last
    web.email = email
    i += 1
