# spider to scrap data from l'office des spectacles

import scrapy
from scrapy.crawler import CrawlerProcess

class Expo_offspec_Spider(scrapy.Spider):
    name = "expo_offspec"
    
    start_urls = [
        'https://www.offi.fr/expositions-musees/mois-12-2017.html?npage=1',
    ]

    def parse(self, response):
        for expo in response.css("div.oneRes"):
            yield {
                'title': ' '.join(expo.css("div.eventTitle strong a span::text").extract_first().split()), 
                'type': ' '.join(expo.css("div.oneRes ul li::text").extract_first()[2:].split()),
                'img_url': expo.css("div.resVignette a img::attr(src)").extract_first(),
                'url': response.urljoin(expo.css("div.resVignette a::attr(href)").extract_first()),
                'prog': ' '.join(expo.css("div.oneRes ul li::text").extract()[1].split()),
                'date_start': expo.css("div.oneRes ul li::text").extract()[4], #date en francais en str -> besoin de transformer avec dateparser plus tard
                'date_end': expo.css("div.oneRes ul li::text").extract()[5],
                'location': expo.css("div.oneRes ul li a::text").extract_first() + " " + " ".join(expo.css("div.oneRes ul li::text").extract()[3].split()),
                'description': ' '.join(expo.css("div.oneRes::text").extract()[3].split())
            }
        
        next_page = response.css("div.dayNav ul li.last a::attr(href)").extract_first()
        if next_page != '/expositions-musees/mois-12-2017.html?npage=1':
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'jsonlines',
    'FEED_URI': 'backend/exhibition/expo_scraper/expo_offspect.jsonl'
})

process.crawl(Expo_offspec_Spider)
process.start() # the script will block here until the crawling is finished