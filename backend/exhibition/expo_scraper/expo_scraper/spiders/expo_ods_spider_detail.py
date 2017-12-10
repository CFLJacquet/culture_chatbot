# spider to get the detail of each exhibition in l'office des spectacles
# !!! Run the expo_ods_spider first to create the expo_offspect.jsonl !!!

import scrapy
from scrapy.crawler import CrawlerProcess
import json
import re

list_urls =[]
with open('backend/exhibition/expo_scraper/expo_offspect.jsonl') as f:
    for line in f:
        list_urls.append(json.loads(line)['url'])


class Expo_offspec_Spider(scrapy.Spider):
    name = "expo_offspec_detail"
    
    start_urls = list_urls

    def parse(self, response):
        s = response.css("ul.detail li span[itemprop='description']").extract_first()
        try:
            s = re.sub('<[^>]*>', '', s)
        except TypeError:
            s = response.css("ul.detail li").extract()[1]
            try:
                s = re.sub('<[^>]*>', '', s)
            except TypeError:
                s = "Sacrebleu ! Nous n'avons pas réussi à récupérer le détail... :("


        yield {
            'url': response.url,
            'summary': s, 
            'price': response.css("div.info ul.detail li::text").extract()[1][1:].capitalize(),
        }

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'jsonlines',
    'FEED_URI': 'backend/exhibition/expo_scraper/expo_offspect_detail.jsonl'
})

process.crawl(Expo_offspec_Spider)
process.start() # the script will block here until the crawling is finished