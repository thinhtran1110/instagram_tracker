import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from decouple import config

# Setup a .env file in the current directory
# like 
# iguser=yourusername 
# igpassword=yourpsw
# ==========================================
USERNAME = config("iguser")
PASSWORD = config("igpassword")
TARGET = config("igtarget")
# ==========================================

TIMEOUT = 15

def copy_old():
    with open('followers.txt', 'r') as f:
        with open('follower_old/followers_old.txt', 'w') as o:
            o.write(f.read())
def check():
    followers_set = set()
    with open('followers.txt', 'r') as file:
        for line in file:
            followers_set.add(line.strip())

    followers_old_set = set()
    with open('follower_old/followers_old.txt', 'r') as file:
        for line in file:
            followers_old_set.add(line.strip())

    result_set = followers_old_set - followers_set
    with open('unfollowers.txt', 'w') as f:
        for item in result_set:
            f.write('%s\n' % item)


def scrape():
    # usr = input('[Required] - Whose followers do you want to scrape: ')
    usr = TARGET

    # user_input = int(
    #     input('[Required] - How many followers do you want to scrape (60-500 recommended): '))

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--log-level=3")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    bot.get('https://www.instagram.com/accounts/login/')

    time.sleep(1)

    #accept cookie policy
    # bot.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
    # bot.find_element(By.XPATH,"/html/body/div[4]/div/div/div[3]/div[2]/button").click()
    
    print("[Info] - Logging in...")  

    user_element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div[1]/div[3]/div/label/input')))

    user_element.send_keys(USERNAME)

    pass_element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div[1]/div[4]/div/label/input')))

    pass_element.send_keys(PASSWORD)

    login_button = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div[1]/div[6]/button')))

    time.sleep(0.4)

    login_button.click()

    time.sleep(10)

    bot.get('https://www.instagram.com/{}/'.format(usr))

    time.sleep(3.5)

    #follower_count = bot.find_element(By.XPATH, "a[@href='/{}/followers']/span[@class='g47SY']".format(TARGET)).text
    follower_count = int(bot.find_element(By.CSS_SELECTOR, "a[href='/{}/followers/'] span".format(TARGET)).get_attribute("title"))
    WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, "//a[contains(@href, '/following')]"))).click()

    time.sleep(2)

    print('[Info] - Scraping...')

    users = set()

    for _ in range(round(follower_count // 20)):

        ActionChains(bot).send_keys(Keys.END).perform()

        time.sleep(1)

    followers = bot.find_elements(By.XPATH,
    "//a[contains(@href, '/')]")

    # Getting url from href attribute
    for i in followers:
        if i.get_attribute('href'):
            users.add(i.get_attribute('href').split("/")[3])
        else:
            continue

    print('[Info] - Saving...')
    print('[DONE] - Your followers are saved in followers.txt file!')

    with open('followers.txt', 'w') as file:
        file.write('\n'.join(users) + "\n")


if __name__ == '__main__':
    copy_old()
    scrape()
    check()