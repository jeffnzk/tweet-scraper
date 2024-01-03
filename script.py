from dotenv import load_dotenv
from datetime import datetime
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

load_dotenv()  # This loads the environment variables from .env

# Now you can use os.environ to access your variables
TWITTER_USERNAME = os.environ.get('TWITTER_USERNAME')
TWITTER_PASSWORD = os.environ.get('TWITTER_PASSWORD')

# Replace 'path_to_webdriver' with the path to your WebDriver executable
# or ensure it's already in your PATH
driver = webdriver.Chrome()

# Open Twitter
driver.get("https://www.x.com")
scrapeUser = "davidgoggins"

def login(username, password):
  # click sign in button
  wait = WebDriverWait(driver, 10)  # Waits for 10 seconds
  element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sign in')]")))
  element.click()

  # input username
  wait = WebDriverWait(driver, 10)  # Waits for 10 seconds
  inputElement = wait.until(EC.presence_of_element_located((By.TAG_NAME, "INPUT")))
  inputElement.send_keys(username)

  # # click next button (to proceed to username/password screen)
  wait = WebDriverWait(driver, 10)  # Waits for 10 seconds
  nextButton = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Next']")))
  nextButton.click()

  # input password
  wait = WebDriverWait(driver, 10)  # Waits for 10 seconds
  passwordInput = wait.until(EC.presence_of_element_located((By.NAME, "password")))
  passwordInput.send_keys(password)

  # click login button
  loginButton = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Log in']")))
  loginButton.click()

login(TWITTER_USERNAME, TWITTER_PASSWORD)

# Find on screen element to check if we're logged in, then redirect
wait = WebDriverWait(driver, 10)  # Waits for 10 seconds
whatIsHappening = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'What is happening?')]")))

# redirect + wait a couple of seconds for Tweets to load onto the page
driver.get(f"https://twitter.com/{scrapeUser}")
time.sleep(2)

def getTweetData(tweet):
  try:
    date_string = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
    date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    date = date_object.strftime('%m/%d/%Y %I:%M %p')
    # print("DATE POSTED", date, "\n")
  except NoSuchElementException:
    return
  
  # tweet username, body, number of comments, retweets, likes and views
  username = tweet.find_element(By.XPATH, ".//span[contains(text(), '@')]").text
  tweetBody = tweet.find_element(By.XPATH, ".//div[2]/div[2]/div[2]").text
  numOfLikes = tweet.find_element(By.XPATH, ".//*[@data-testid='like']").get_attribute('aria-label').split(' ', 1)[0]
  numOfReplies = tweet.find_element(By.XPATH, ".//*[@data-testid='reply']").get_attribute('aria-label').split(' ', 1)[0]
  numOfRetweets = tweet.find_element(By.XPATH, ".//*[@data-testid='retweet']").get_attribute('aria-label').split(' ', 1)[0]
  
  # print("TWEET CONTENT", tweetBody, "\n")
  # print(numOfReplies[0], numOfRetweets[0], numOfLikes[0])

  tweetData = (username, date, tweetBody, numOfLikes, numOfRetweets, numOfReplies)
  return tweetData

data = []
tweet_ids = set()
prev_position = driver.execute_script('return window.pageYOffset;')
scrolling = True

while scrolling:
  cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@data-testid="tweet"]')))
  for card in cards[-15:]:
    tweet = getTweetData(card)
    if tweet:
      tweetID = ''.join(tweet)
      if tweetID not in tweet_ids and tweet[0][1:] == scrapeUser:
        tweet_ids.add(tweetID)
        data.append(tweet)
        print(tweet, "\n")
  
  scroll_attempt = 0
  
  while True:
    # JS script to scroll down to the end of the page
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)
    curr_position = driver.execute_script('return window.pageYOffset;')

    if prev_position == curr_position:
      scroll_attempt += 1
      
      if scroll_attempt >= 3:
        scrolling = False
        break
      else:
        time.sleep(2)
    else:
      prev_position = curr_position
      break

# print(data)
# print(tweet_ids)

data = sorted(data, key=lambda x: int(x[3]), reverse=True)

with open('tweets.csv', 'w', newline='', encoding='utf-8') as f:
  header = ['TwitterHandle', 'Date', 'Tweet Body', 'Number of Likes', 'Number of Replies', 'Number of Retweets']
  writer = csv.writer(f)
  writer.writerow(header)
  writer.writerows(data)


# TODO
# Separate everything into Page Object Model classes in Python
# constructor function + methods for each on screen page
# import/export
# then a script file to execute all POM classes
  
time.sleep(600) # 60 seconds => 1 min

# Close the browser
driver.quit()