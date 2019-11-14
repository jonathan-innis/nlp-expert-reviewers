import requests
import urllib.request
import time
from bs4 import BeautifulSoup

class WireCutterScraper:
    def __init__(self, url, category):
        self.id = 2261
        self.url = url
        self.category = category
        self.response = requests.get(self.url)
        self.soup = BeautifulSoup(self.response.text, "html.parser")
        self.articles = self.soup.select('section > ul > li > article > div > a')
    
    def scrape(self):
        data = []
        for article in self.articles:
            article_url = article['href']
            article_response = requests.get(article_url)
            article_soup = BeautifulSoup(article_response.text, "html.parser")
            callouts = article_soup.select('section[data-gtm-element="intro"] div[data-scp="callout"]')
            for callout in callouts:
                res = self.scrape_other_review(callout)
                if res[0] and res[1] and res[2]:
                    res.insert(0, self.id)
                    data.append(res)
                    self.id += 1
            time.sleep(1)
        return data

    def scrape_review(self, callout):
        try:
            title = callout.select('a[data-gtm-trigger="callout_product_link_name"]')[0]
            if not title:
                raise Exception("No title to this review")
            review = callout.find_next_sibling("p")
            if not review:
                review = callout.find_next_sibling("p")
                if not review:
                    raise Exception("No review attached to this product: {}".format(title.text))
            amazon_link = callout.select('a[data-store="Amazon"]')
            if not amazon_link or len(amazon_link) == 0:
                return [self.category, title.text, review.text.strip('\"'), False, amazon_link[0]['href']]
                raise Exception("No Amazon link attached to this product: {}".format(title.text))
        except Exception as error:
            print('Error occurred: {}'.format(error))
            return ["", "", "", ""]
        return [self.category, title.text, review.text.strip('\"'), True, amazon_link[0]['href']]

    def scrape_other(self):
        data = []
        for article in self.articles:
            article_url = article['href']
            article_response = requests.get(article_url)
            article_soup = BeautifulSoup(article_response.text, "html.parser")
            reviews = article_soup.select('#the-competition-panel p .product-link')
            for review in reviews:
                res = self.scrape_other_review(review)
                if res[0] and res[1] and res[2]:
                    res.insert(0, self.id)
                    data.append(res)
                    self.id += 1
        return data

    def scrape_other_review(self, review):
        try:
            title = review
            if not title:
                raise Exception("No title to this review")
            review_text = review.parent
            if not review_text:
                raise Exception("No review attached to this product: {}".format(title.text))
        except Exception as error:
            print('Error occurred: {}'.format(error))
            return ["", "", "", False, ""]
        if "merchant=Amazon" in title['href']:
            return [self.category, title.text, review_text.text.strip('\"'), True, title['href']]
        return [self.category, title.text, review_text.text.strip('\"'), False, title['href']]
