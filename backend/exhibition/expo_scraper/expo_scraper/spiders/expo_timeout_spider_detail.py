# spider to scrap data from l'office des spectacles

import scrapy
from scrapy.crawler import CrawlerProcess
import json

class Expo_timeout_Spider(scrapy.Spider):
    name = "expo_timeout"
    
    list_urls =[]
    with open('backend/exhibition/expo_scraper/extracted_data/timeout_url.jsonl') as f:
        for line in f:
            list_urls.append(json.loads(line)['url'])

    start_urls = list_urls    

    def parse(self, response):

        yield {
            'title': response.xpath("//h1/text()").extract_first(),
            'score': response.xpath("//label").xpath(".//div[contains(@class, 'rating')]/@title").extract_first(),
            'review': ' '.join(response.xpath("//article[contains(@itemprop, 'review')]//p/text()").extract())
        }

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/timeout_critics.jsonl'
    })

    process.crawl(Expo_timeout_Spider)
    process.start() # the script will block here until the crawling is finished