# spider to scrap urls from timeout critics

import scrapy
import os
from scrapy.crawler import CrawlerProcess

class Expo_timeout_Spider(scrapy.Spider):
    name = "expo_timeout"
    
    start_urls = [
        'https://www.timeout.fr/paris/art/expositions/dernieres-critiques',
    ]

    def parse(self, response):
        main = response.xpath("//div[@class = 'xs-flex xs-flex-wrap xs-flex-row tiles']")
        expo_list = main.xpath(".//div[@class = 'feature-item__content']")

        for expo in expo_list:
            try:
                url = response.urljoin(expo.xpath(".//h3//a/@href").extract_first())
            except:
                title = "Non disp."

            request_details = scrapy.Request(url, self.parse_details)
            request_details.meta['data'] =  { 'url': url }

            yield request_details
    
    def parse_details(self, response):
        data = response.meta['data']
        
        try:
            score = int(response.xpath("//label").xpath(".//div[contains(@class, 'rating')]/@title").extract_first()[0])
        except:
            score = 0

        data['title'] = response.xpath("//h1/text()").extract_first()
        data['score'] = score
        data['review'] = ' '.join(response.xpath("//article[contains(@itemprop, 'review')]//p/text()").extract())
        
        yield data

if __name__ == "__main__":
    try:
        os.remove("backend/exhibition/expo_scraper/extracted_data/timeout.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/timeout.jsonl'
    })

    process.crawl(Expo_timeout_Spider)
    process.start() # the script will block here until the crawling is finished