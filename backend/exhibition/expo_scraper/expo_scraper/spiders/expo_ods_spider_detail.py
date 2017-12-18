# spider to get the detail of each exhibition in l'office des spectacles
# !!! Run the expo_ods_spider first to create the expo_offspect.jsonl !!!

import scrapy
from scrapy.crawler import CrawlerProcess
import json
import re
from unicodedata import normalize   #to Normalize Unicode -> look for "e\u0301" in https://www.safaribooksonline.com/library/view/fluent-python/9781491946237/ch04.html

class Expo_offspec_d_Spider(scrapy.Spider):
    name = "expo_offspec_detail"
    
    list_urls =[]
    with open('backend/exhibition/expo_scraper/extracted_data/offSpec_main.jsonl') as f:
        for line in f:
            list_urls.append(json.loads(line)['url'])

    start_urls = list_urls

    def parse(self, response):

        try:
            main = response.css("ul.detail li")
            text =[]
            for i in range(1, len(main)):
                if '<li style="min-height:28px;margin-bottom:14px;">' in main[i].extract() :
                    break
                else:
                    text.append(' '.join(main[i].xpath('.//text()').extract()))
            s = ' '.join(text)
        except :
            s = "Sacrebleu ! Nous n'avons pas réussi à récupérer le détail... :("
        try:
            price = response.xpath("//li[contains(.,'Tarif')]//text()").extract()[1].capitalize()
        except:
            price = "Tarif non disp."

        yield {
            'url': response.url,
            'summary': normalize('NFC', s), 
            'price': price,
        }


if __name__ == '__main__':
    process2 = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/offSpec_details.jsonl',
    })

    process2.crawl(Expo_offspec_d_Spider)
    process2.start() # the script will block here until the crawling is finished

