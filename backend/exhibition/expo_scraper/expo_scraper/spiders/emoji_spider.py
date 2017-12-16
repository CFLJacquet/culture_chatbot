# spider to scrap data from the study of emoticones on twitter by Matjaz Perc, University of Maribor, SLOVENIA 
# url of article: http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0144296
# It gives the conversion emoji <-> text

import scrapy
import json
import unicodedata as ud

from scrapy.crawler import CrawlerProcess

def convert_special(c):
    """ converts emoji into emoji description if it exists """
    if c > '\uffff':
        c = ':{}:'.format(ud.name(c).lower().replace(' ', '_')) 
    return c


class ExpoSpider(scrapy.Spider):
    name = "expo"
    
    start_urls = [
        'http://kt.ijs.si/data/Emoji_sentiment_ranking/',
        ]

    def parse(self, response):
        r = response.css('html body div.container table tr')
        for i in range (1, len(r)+1):
            
            yield {
                'img': convert_special(r[i].css('td::text')[0].extract()),
                #'img': r[i].css('td::text')[0].extract(),
                'name': r[i].css('td::text')[9].extract().lower(),
                'negative': r[i].css('td::text')[5].extract(),
                'neutral': r[i].css('td::text')[6].extract(),
                'positive': r[i].css('td::text')[7].extract(),
                'sentiment': r[i].css('td::text')[8].extract(),

            } 

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'backend/exhibition/expo_scraper/emoji_sentiment.json',
    'FEED_EXPORT_ENCODING': 'utf-8'
})

process.crawl(ExpoSpider)
process.start() # the script will block here until the crawling is finished