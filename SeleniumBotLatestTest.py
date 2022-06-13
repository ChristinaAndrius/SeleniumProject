import random
import time

from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from details import secrets


class SeleniumBot:
    def __init__(self, path):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome(service=Service(path), options=options)
        self.driver.maximize_window()
        self.driver.delete_all_cookies()

    def wait(self, locator, id, time=15):
        element = WebDriverWait(self.driver, time).until(EC.element_to_be_clickable((locator, id)))
        return element

    def waitVisibile(self, locator, id, time=15):
        elements = WebDriverWait(self.driver, time).until(EC.visibility_of_all_elements_located((locator, id)))
        return elements


    def click(self, element, double=False):
        action = ActionChains(self.driver)

        if double:
            action.double_click(element)
        else:
            action.click(element)
        action.perform()


    def login(self, username, password):
        self.username = username
        self.driver.get('https://www.instagram.com/')
        username_input = self.wait(By.XPATH, "//input[contains(@aria-label, 'username')]")
        username_input.send_keys(username)

        password_input = self.driver.find_element(By.XPATH, "//input[@aria-label='Password']")
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)

        # Until it is done logging in
        while True:
            try:
                self.driver.find_element(By.XPATH, "//input[@aria-label='Password']")
            except NoSuchElementException:
                break


    def scrape_by_hashtag(self, hastag):
        self.driver.get(f'https://www.instagram.com/explore/tags/{hastag}/')
        time.sleep(5)
        links = self.waitVisibile(By.CSS_SELECTOR, 'article a')

        usernames = []

        for link in links[:5]:
            links.append('https://www.instagram.com' + link.get_attribute('href'))
            self.click(link)

            tags = self.waitVisibile(By.XPATH, '//header//a[text()]')

            for tag in tags:
                href = tag.get_attribute('href')
                if not 'explore' in href:
                    usernames.append(tag.text)
                    break

            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(10)


        return usernames

    def follow_users(self, usernames):
        for username in usernames:
            self.driver.get(f'https://www.instagram.com/{username}/')

            try:
                follow_button = self.wait(By.XPATH, "//button//div[contains(text(), 'Follow')]", time=5)
            except TimeoutException:
                continue

            text = follow_button.text.strip()

            self.click(follow_button)

            while True:
                try:
                    time.sleep(5)
                    if follow_button.text.strip() != text:
                        break
                except:
                    break

    def upload_picture(self, path, caption):
        # try:
        self.driver.get(f'https://www.instagram.com/{self.username}/')

        self.click(self.wait(By.XPATH, '//*[@aria-label = "New post"]'))
        time.sleep(10)
        # except (WebDriverException, TimeoutException):
        #     return self.upload_picture(path, caption)

        try:
            post = self.wait(By.XPATH, '//input[contains(@accept, "video")]', time=15)
        except TimeoutException:
            post = self.driver.find_element(By.XPATH, '//input[contains(@accept, "video")]')
        post.send_keys(path)

        for _ in range(2):
            next_btn = self.wait(By.XPATH, '//button[text() = "Next"]')
            time.sleep(10)
            self.click(next_btn)

        description = self.wait(By.XPATH, "//textarea[contains(@aria-label, 'caption')]")
        time.sleep(10)
        description.send_keys(caption)

        time.sleep(10)
        self.click(self.driver.find_element(By.XPATH, '//button[text() = "Share"]'))


        while True:
            try:
                self.driver.find_element(By.XPATH, "//*[text()= 'Your post has been shared.']")
                break
            except NoSuchElementException:
                pass

    def like_last_ten(self, usernames):
        for username in usernames:
            self.driver.get(f'https://www.instagram.com/{username}/')




            posts = self.waitVisibile(By.CSS_SELECTOR, 'article a')

            for post in posts[:5]:
                self.click(post)

                time.sleep(10)
                try:
                    likes = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@aria-label = 'Like']")))
                except TimeoutException:
                    likes = []

                for img in likes[:3]:
                    try:
                        self.click(img)
                    except: pass
                time.sleep(5)

                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(5)

    def write_comments(self, usernames, comment):
        for username in usernames:
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(3)


            posts = self.waitVisibile(By.CSS_SELECTOR, 'article a')

            for post in posts[:2]:
                self.click(post)

                time.sleep(10)

                try:
                    self.click(self.wait(By.XPATH, "//textarea[contains(@aria-label, 'comment')]"))

                    textarea = self.driver.find_element(By.XPATH, "//textarea[contains(@aria-label, 'comment')]")
                    textarea.send_keys(comment)
                    time.sleep(5)

                    self.click(self.driver.find_element(By.XPATH, '//button/div[text() = "Post"]'))
                    time.sleep(5)
                except TimeoutException:
                    pass



                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(10)

    def send_direct_message(self, usernames, message):
        for username in usernames:
            self.driver.get(f'https://www.instagram.com/{username}/')
            time.sleep(5)

            url = self.driver.current_url
            try:
                self.click(self.wait(By.XPATH, "//button//div[contains(text(), 'Message')]", time=6))
            except TimeoutException:
                self.click(self.driver.find_element(By.XPATH, "//button//div[contains(text(), 'Follow')]"))
                try:
                    self.click(self.wait(By.XPATH, "//button//div[contains(text(), 'Message')]"))
                except TimeoutException:
                    continue

            time.sleep(10)
            while url == self.driver.current_url:
                pass

            self.click(self.wait(By.XPATH, '//textarea[contains(@placeholder, "Message")]'))

            textarea = self.driver.find_element(By.XPATH, '//textarea[contains(@placeholder, "Message")]')
            textarea.send_keys(message)
            time.sleep(5)
            textarea.send_keys(Keys.ENTER)

            time.sleep(10)

    def scrape_followers(self):
        self.driver.get(f'https://www.instagram.com/{self.username}/')

        self.click(self.wait(By.XPATH, "//a[contains(@href, 'followers')]"))

        time.sleep(15)

        followers = []

        ff_usernames = self.waitVisibile(By.XPATH, "//li//div//a//span")
        while len(ff_usernames) < 100:
            self.driver.execute_script('arguments[0].scrollIntoView()', ff_usernames[-1])
            time.sleep(5)
            ff_usernames = self.driver.find_elements(By.XPATH, "//li//div//a//span")

        for ff in ff_usernames:
            followers.append(ff.text)

        return followers


    def scrape_following(self):
        self.driver.get(f'https://www.instagram.com/{self.username}/')

        self.click(self.wait(By.XPATH, "//a[contains(@href, 'following')]"))

        time.sleep(15)

        following = []

        ff_usernames = self.waitVisibile(By.XPATH, "//li//div//a//span")
        while len(ff_usernames) < 100:
            try:
                self.driver.execute_script('arguments[0].scrollIntoView()', ff_usernames[-1])
            except StaleElementReferenceException:
                ff_usernames = self.driver.find_elements(By.XPATH, "//li//div//a//span")
                self.driver.execute_script('arguments[0].scrollIntoView()', ff_usernames[-1])

            ff_usernames = self.driver.find_elements(By.XPATH, "//li//div//a//span")

        for ff in ff_usernames:
            following.append(ff.text)

        return following

    def unfollow_users(self, usernames):
        for username in usernames:
            self.driver.get(f'https://www.instagram.com/{username}/')

            self.click(self.wait(By.XPATH, '//*[@aria-label = "Following"]'))

            time.sleep(5)

            self.click(self.wait(By.XPATH, '//button[text() = "Unfollow"]'))

            time.sleep(5)

            while True:
                try:
                    self.driver.find_element(By.XPATH, "//button//div[contains(text(), 'Follow')]")
                    break
                except NoSuchElementException:
                    pass



    def logout(self):
        try:
            self.driver.quit()
        except WebDriverException:
            print('The bot has already been closed')



if __name__ == '__main__':

    PATH = ChromeDriverManager().install()
    bot = SeleniumBot(PATH)

    bot.login(username=secrets['username'], password=secrets['password'])
    time.sleep(5)

    usernames1 = bot.scrape_by_hashtag('dress')
    print(usernames1)
    time.sleep(10)
    #
    # bot.follow_users(usernames1)
    # time.sleep(10)
    #
    # usernames2 = bot.scrape_by_hashtag('germany')
    # time.sleep(10)
    #
    # bot.follow_users(usernames2)
    # time.sleep(10)

    bot.upload_picture(r'C:\Users\ebran\Desktop\Instagram_Pics_BOT\\kristina-petrick--poL3YQTBPI-unsplash (1).jpg', 'we love #designerfashion!')
    time.sleep(10)

    bot.like_last_ten(usernames1)
    time.sleep(30)
    # bot.like_last_ten(usernames2)
    # time.sleep(15)

    bot.write_comments(usernames1,'Such a nice #fashionstyle !')
    time.sleep(30)
    # bot.write_comments(usernames2, 'Nice, I love it !')
    # time.sleep(15)


    bot.send_direct_message(usernames1, 'Hello, would You be interested in promoting our brand ?')
    time.sleep(30)
    # bot.send_direct_message(usernames2, 'Hello')
    # time.sleep(15)


    followers = bot.scrape_followers()
    followings = bot.scrape_following()
    non_followers = set(followings) - set(followers)

    bot.send_direct_message(random.sample(followers, 5), 'Hi, do You like fashion?')
    time.sleep(15)

    bot.unfollow_users(random.sample(list(non_followers), 25))
    time.sleep(5)

    bot.logout()


















