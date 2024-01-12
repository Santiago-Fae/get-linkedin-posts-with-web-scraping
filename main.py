from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from time import sleep
import unittest, time, re
import pdb
import re
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

# get variables from .env file
LINKEDIN_LOGIN = os.getenv("LINKEDIN_LOGIN")
LINKEDIN_SENHA = os.getenv("LINKEDIN_SENHA")
URL_PARA_POSTS = os.getenv("URL_PARA_POSTS")

class GetPostsLinkedin():
    def __init__(self):
        #chose if you want to save the full embed link or just the urn number
        self.save_full_embed_link = True
        #chose number of posts to get
        self.number_of_posts = 3

    def set_up(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
    
    def linkedin_posts(self):
        #open linkedin
        driver = self.driver
        driver.get("https://www.linkedin.com/")

        #login
        driver.find_element("id", "session_key").click()
        driver.find_element("id", "session_key").send_keys(LINKEDIN_LOGIN)
        sleep(2)
        driver.find_element("id", "session_password").click()
        driver.find_element("id", "session_password").send_keys(LINKEDIN_SENHA, Keys.ENTER)
        sleep(2)

        #open posts
        driver.get(URL_PARA_POSTS)
        sleep(5)

        #close chats
        element_search = driver.find_elements(By.CLASS_NAME, 'msg-overlay-list-bubble-search')
        if element_search:
            div_controls = driver.find_element(By.CLASS_NAME, 'msg-overlay-bubble-header__controls')
            buttons = div_controls.find_elements(By.TAG_NAME, 'button')
            if buttons:
                last_button = buttons[-1]
                last_button.click()
                sleep(2)

        #get list posts
        elements = driver.find_elements("class name", "feed-shared-control-menu__trigger")

        self.posts = []

        for element in elements:
            #scroll to element
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            sleep(1)
            driver.execute_script("window.scrollBy(0, -200);")
            sleep(2)
            element.click()
            sleep(2)

            #verify if exists embed menu
            embed_menu = driver.find_element("class name", "artdeco-dropdown__content-inner").find_element(By.CSS_SELECTOR, 'ul')
            if len(embed_menu.find_elements(By.TAG_NAME, 'li')) < 3:
                continue

            embed_menu.find_elements(By.TAG_NAME, 'li')[2].click()
            sleep(2)
            try:
                #verify if exists textarea for get embed
                textarea_element = driver.find_element("id", "feed-components-shared-embed-modal__embed-code-textarea")
                if textarea_element:
                    valor_textarea = textarea_element.get_attribute("value")
                    match = re.search(r'share:(\d+)', valor_textarea)

                    if match:
                        urn_number = match.group(1)
                        if self.save_full_embed_link:
                            self.posts.append(valor_textarea)
                            print("Saved embed link:", valor_textarea)
                        else:
                            self.posts.append(urn_number)
                            print("Saved urn number:", urn_number)
                        pass
            except NoSuchElementException:
                print("Element not found")

            close_button = driver.find_element("class name", "artdeco-modal__dismiss")
            close_button.click()
            sleep(2)

            if len(self.posts) == self.number_of_posts:
                break
        print("Números de URN:", self.posts)


    def save_file(self):
        #check if exists posts
        if len(self.posts) == 0:
            print("No posts to save")
            return
        
        with open("posts.txt", "w") as file:
            file.write(str(self.posts))
            
        print("File saved")

    def tear_down(self):
        self.driver.quit()

    def run(self):
        self.set_up()
        self.linkedin_posts()
        self.save_file()
        self.tear_down()

if __name__ == "__main__":
    get_posts = GetPostsLinkedin()
    get_posts.run()