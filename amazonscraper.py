from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time, random

class AmazonScraper:
    def __init__(self):
        option = webdriver.ChromeOptions()
        option.add_argument(" — incognito")
        self.driver = webdriver.Chrome(executable_path="/home/jonathan/github-projects/expert-reviews/chromedriver", chrome_options=option)
        self.TIMEOUT = 20

    def scrape(self, product_id, product_url):
        review_link = self.get_product(product_url)
        return self.get_reviews(review_link, product_id)
        self.driver.quit()
        
    def get_product(self, product_url):
        self.driver.get(product_url)

        try:
            WebDriverWait(self.driver, self.TIMEOUT)
            review_element = self.driver.find_element_by_xpath("//a[@data-hook='see-all-reviews-link-foot']")
            review_link = review_element.get_attribute('href')
            time.sleep(random.randint(1,4))
        except TimeoutException:
            print("Timed out waiting for page to load")
            self.driver.quit()
            return ""
        except Exception as error:
            print(error)
        
        return review_link
    
    def get_reviews(self, review_link, product_id):
        self.driver.get(review_link)
        review_data = []
        try:
            while True:
                time.sleep(random.randint(1,4))
                WebDriverWait(self.driver, self.TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='cm_cr-pagination_bar']/ul/li[2]/a")))
                reviews = self.driver.find_elements_by_xpath("//div[@data-hook='review']")
                review_data += self.scrape_page_reviews(reviews, product_id)
                next_button = self.driver.find_element_by_xpath("//div[@id='cm_cr-pagination_bar']/ul/li[2]/a")
                if next_button.get_attribute("class").find("a-disabled") != -1:
                    break
                next_button.click()
        except Exception as error:
            print(error)
        return review_data 
    
    def scrape_page_reviews(self, reviews, product_id):
        review_data = []
        for raw_review in reviews:
            title = raw_review.find_element_by_xpath(".//a[@data-hook='review-title']").text
            stars = self.get_stars(raw_review)
            username = raw_review.find_element_by_xpath(".//span[@class='a-profile-name']").text
            review = raw_review.find_element_by_xpath(".//span[@data-hook='review-body']").text

            review = review.replace('\n', '').replace('\r', '').strip()
            review_data.append([product_id, title, stars, username, review])
        return review_data
    
    def get_stars(self, review):
        star_element = review.find_element_by_xpath(".//i[@data-hook='review-star-rating']")
        star_element_class = star_element.get_attribute("class")
        
        SEARCH_TEXT = "a-star-"
        start = star_element_class.index(SEARCH_TEXT) + len(SEARCH_TEXT)
        return star_element_class[start:start+1]



        