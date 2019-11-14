from bs4 import BeautifulSoup
from wirecutterscraper import WireCutterScraper
from amazonscraper import AmazonScraper
import pandas as pd
from itertools import cycle
from lxml.html import fromstring
import requests, urllib.request, time, sys, random

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

def main():
    assert len(sys.argv) == 2
    if sys.argv[1] == 'wirecutter':
        url = "https://thewirecutter.com/kitchen-dining/"
        wire_cutter_scraper = WireCutterScraper(url, "Kitchen & Dining")
        data_content = wire_cutter_scraper.scrape_other()

        dataset = pd.DataFrame(data_content)
        dataset.columns = ["id", "category", "product", "review", "has_amazon_link", "amazon_link"]
        dataset.to_csv("data/wirecutter.csv", mode='a', header=False, index=False)

    elif sys.argv[1] == 'amazon':
        data = pd.read_csv("wirecutter.csv", delimiter=',', names=["id", "product", "review", "amazon_link"])
        parsed = data[['id', 'amazon_link']]
        proxies = list(get_proxies())
        proxy_pool = cycle(proxies)
        amazon_scraper = AmazonScraper()

        data_content = []

        # dataset = pd.DataFrame([["","","","",""]])
        # dataset.columns = ["product_id", "review_title", "review_stars", "review_username", "review_text"]
        # dataset.to_csv("amazon.csv", index=False)

        for i, row in parsed.iterrows():
            if i >= 77:
                data_content = amazon_scraper.scrape(row.id, row.amazon_link)
                dataset = pd.DataFrame(data_content)
                dataset.to_csv("amazon.csv", mode='a', header=False, index=False)
                time.sleep(random.randint(2,5))

if __name__ == "__main__":
    main()