#spider to scrap data from l'office du tourisme de Paris

import scrapy

import scrapy
from scrapy.crawler import CrawlerProcess

class ExpoSpider(scrapy.Spider):
    name = "expo"
    
    start_urls = [
        'https://www.parisinfo.com/ou-sortir-a-paris/infos/guides/calendrier-expositions-paris?perPage=50',
        'https://www.parisinfo.com/ou-sortir-a-paris/infos/guides/calendrier-expositions-paris?perPage=50&page=2',
    ]

    def parse(self, response):
        for expo in response.css('article.Article-line.Article-line--visitors'):
            yield {
                'title':expo.css("header.Article-line-heading h3.Article-line-title a::text").extract_first(),
                'img_url': expo.css("figure.Article-line-image a img::attr(src)").extract_first(),
                'url': 'https://www.parisinfo.com' + expo.css("figure.Article-line-image a::attr(href)").extract_first(),
                'period': ' '.join(expo.css("header.Article-line-heading div.Article-line-meta.date::text").extract_first().split()),
                'location': expo.css("header.Article-line-heading div.Article-line-info div.Article-line-place::text").extract_first(),
                'description': expo.css("div.Article-line-content p::text").extract_first()
            } 

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'jsonlines',
    'FEED_URI': 'backend/exhibition/expo_scraper/expo_offtour.jsonl'
})

process.crawl(ExpoSpider)
process.start() # the script will block here until the crawling is finished