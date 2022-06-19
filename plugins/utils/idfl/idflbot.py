from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
'''Uncomment the below line when running in linux'''
# from pyvirtualdisplay import Display
import time, os
 
class Twitterbot:
 
    def __init__(self, email, password):
  
        self.email = email
        self.password = password
        self.base = 'https://idfl-forum.com/'
        # initializing chrome options
        chrome_options = Options()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--disable-gpu')
 
        # adding the path to the chrome driver and
        # integrating chrome_options with the bot
        self.bot = webdriver.Chrome(
            executable_path = os.environ.get("GOOGLE_CHROME_DRIVER"),
            options = chrome_options
        )
 
    def login(self):
        """
            Method for signing in the user
            with the provided email and password.
        """
 
        bot = self.bot
        # fetches the login page
        bot.get('https://idfl-forum.com/forum.php')
        # adjust the sleep time according to your internet speed
        time.sleep(3)

        email = bot.find_element_by_xpath(
            '//div[1]/div[1]/div[2]/ul/li[3]/form/fieldset/div/div/input[1]'
        )
        password = bot.find_element_by_xpath(
            '//div[1]/div[1]/div[2]/ul/li[3]/form/fieldset/div/div/input[3]'
        )
 
        # sends the email to the email input
        email.send_keys(self.email)
        # sends the password to the password input
        password.send_keys(self.password)
        # executes RETURN key action
        password.send_keys(Keys.RETURN)
 
        time.sleep(2)
 
    def latest_post(self):

        bot = self.bot
 
        # fetches the latest
        bot.get('https://idfl-forum.com/forum.php')
 
        time.sleep(3)
 
        # using set so that only unique links
        # are present and to avoid unnecessary repetition
        thread = set()
        posts = set()
 
        # obtaining the links of the tweets
        for _ in range(15):
            bot.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)'
            )
 
            time.sleep(4)

            [
                thread.add(f'''[{elem.text}]({self.base}{elem.get_attribute('href')})''')\
                for elem in \
                bot.find_elements_by_xpath("//div[2]/table/tbody/tr/td/table[2]/tbody/tr[1]/td/table[2]/tbody/tr/td/div[2]/table/tbody/tr[2]/td[1]//a[@href]")
            ]

        for _ in range(15):
            bot.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)'
            )
 
            time.sleep(4)

            [
                posts.add(f'''[{elem.text}]({self.base}{elem.get_attribute('href')})''')\
                for elem in\
                bot.find_elements_by_xpath("//div[2]/table/tbody/tr/td/table[2]/tbody/tr[1]/td/table[2]/tbody/tr/td/div[2]/table/tbody/tr[2]/td[2]//a[@href]") if elem.get_attribute('href').endswith('newpost')
            ]
        bot.close()
        return thread, posts

    def quit_selenium(self):
        self.bot.quit()
