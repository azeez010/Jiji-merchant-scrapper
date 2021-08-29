import csv, shelve, os, re
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys 
from stdiomask import getpass
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# constants
MAX_PAGINATION = 395

chrome_options = Options()

chrome_options.add_argument("--headless")
basedir = os.path.abspath(os.path.dirname(__file__))

browser = webdriver.Chrome()

db = shelve.open("db")
if not db.get("jiji_current_pagination"):
    db["jiji_current_pagination"] = 1
    print(f"the current pagination has been created and has been set to {db['jiji_current_pagination']}")

try:
    csvFile = open('jiji.csv', 'r', newline='')
    csvFile = open('jiji.csv', 'a', newline='')
    csvWriter = csv.writer(csvFile, delimiter=',')
except Exception as e:
    csvFile = open('jiji.csv', 'w', newline='')
    csvWriter = csv.writer(csvFile, delimiter=',')
    csvWriter.writerow(['Name', 'Phone 1' ,'store name', 'about'])


def start():
    choice = ask_for_input("1. Do you want to start the scraper\n2. Do you want to change the page number\n", 2)
    if choice == 1:
        start_scrapper()
    elif choice == 2:
        settings() 

def start_scrapper():
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    jiji_current_pagination = db['jiji_current_pagination']

    print(f"the scrapper is starting from page {jiji_current_pagination}", MAX_PAGINATION)
    while jiji_current_pagination <= MAX_PAGINATION:
        if jiji_current_pagination > MAX_PAGINATION:
            print(f"You have just finish scraping jiji NG, you are on page {jiji_current_pagination} out of {MAX_PAGINATION}, If you don't mean it, you can use the settings to reset the page number")
            break

        browser.get(f"https://www.jiji.ng/company/page{db['jiji_current_pagination']}")
        all_agents = browser.find_elements_by_xpath("//div[@class='b-company-list__item box-shadow qa-company']")
        all_buttons = WebDriverWait(browser, 50 ,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.XPATH,"//div[@class='b-company-list__info']/div/div[1]/a")))
        
        for i, each_agents in enumerate(all_agents):
            store_link = WebDriverWait(browser, 20 ,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.XPATH, "//div[@class='b-company-list__info']/a")))[i]
            store_name = store_link.text          
            about = WebDriverWait(browser, 50 ,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_all_elements_located((By.XPATH, "//div[@class='b-company-list__info']/div/div")))[i].text
            
            store_link_url = store_link.get_attribute("href")
            print(f"visiting {store_link_url}...")
            store_link.click()
    
            seller_no = WebDriverWait(browser, 50 ,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH, "//div[@class='js-seller-page-phone-button general-button general-button--full general-button--border-radius  general-button--with-shadow general-button--with-icon']")))
            seller_no = seller_no.get_attribute('data-number')
            seller_name = WebDriverWait(browser, 50 ,ignored_exceptions=ignored_exceptions).until(expected_conditions.presence_of_element_located((By.XPATH,"//div[@class='b-seller-info__name']/h1"))).text
            
            print("Scraping...", store_name, about, seller_no, seller_name)
            csvWriter.writerow([seller_name, seller_no, store_name, about])

            browser.back()

        db['jiji_current_pagination'] += 1
    else:
        print(f"You have just finish scraping jiji NG, you are on page {jiji_current_pagination} out of {MAX_PAGINATION}, If you don't mean it, you can use the settings to reset the page number")

def settings():
    try:
        number = int(input("Enter a number to reset your jiji NG scraping page \n"))
    except Exception as exc:
        print("Only Numbers are allowed!")
        settings()

    if number <= 0:
        print(f"The Number entered must be greater than zero")
        settings()
    elif number > MAX_PAGINATION:
        print(f"The Number entered must be less than or equal to {MAX_PAGINATION}")
        settings()
    else:    
        db['jiji_current_pagination'] = number
        print(f'You have successful set agent"s page number to {number}')
        start()

def ask_for_input(question, max_choice):
    choice = ""
    while choice == "":
        num_input = input(question)
        if num_input.isdecimal():
            choice = int(num_input)
            if choice <= max_choice:
                return choice
            
            print('++++++++++++++++++++\nyour choice is out of bound\n++++++++++++++++++++')
            choice = ""
        print('++++++++++++++++++++\ninvalid choice\n++++++++++++++++++++')

start()
