# spider to scrap data from l'office des spectacles

import scrapy
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

            yield {
                'url': url,
            }

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/timeout_critics.jsonl'
    })

    process.crawl(Expo_timeout_Spider)
    process.start() # the script will block here until the crawling is finished