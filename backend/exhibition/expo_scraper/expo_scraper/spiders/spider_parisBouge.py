# spider to scrap url of exhibitions from parisbouge.com

import os
import json
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess

class Expo_parisbouge_Spider(scrapy.Spider):
    name = "expo_parisbouge"
    
    start_urls = [
        'https://www.parisbouge.com/search?type=event&category=exposition',
    ]

    def parse(self, response):
        
        expo_list = response.xpath(".//div[@class = 'card bg']")

        for expo in expo_list:
            try:
                title = expo.xpath(".//div[@class = 'card-title- onelined']//a/text()").extract_first().replace("\u2019","'")
            except:
                title = "Titre Indisp."
            try:
                img_url = expo.xpath(".//img/@data-original").extract_first()
            except:
                img_url = ""
            try:
                url = response.urljoin(expo.xpath(".//div[@class = 'card-title- onelined']//a/@href").extract_first())
            except:
                url = ""
            
            request_details = scrapy.Request(url, self.parse_details)
            request_details.meta['data'] =  {
                'title': title,
                'img_url': img_url,
            }
            yield request_details

        next_page = response.urljoin(response.xpath("//li[@class = 'page next-page']//a/@href").extract_first())
        if next_page != response.url:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_details(self, response):
        data = response.meta['data']
        try :
            price = response.xpath("//div[@class = 'col-xs-12 col-sm-11'][contains(., 'tarif')]//p/text()").extract()[1]
        except:
            price = "Prix Indisp."
        try:        # list of genre
            genre = response.xpath("//div[@class = 'col-xs-12 col-sm-11'][contains(., 'style')]//p//span/text()").extract() 
        except:
            genre = "Genre Indisp."
        description = BeautifulSoup(response.xpath("//p[@id = 'event-detail-infos-content']").extract_first())
        
        data['url'] = response.url
        data['genre'] = genre
        data['tags'] = genre
        data['location'] = response.xpath("//div[@class = 'address-container']//strong/text()").extract_first()
        data['d_start'] = response.xpath("//div[@class = 'row event-section l-section']").xpath(".//div[contains(.,'date et heure')]//a/@href").extract_first().split('&')[2][11:]
        data['d_end'] = response.xpath("//div[@class = 'row event-section l-section']").xpath(".//div[contains(.,'date et heure')]//a/@href").extract_first().split('&')[3][9:]
        data['timetable'] = "Horaires Indisp."
        data['reviews'] = ""
        data['rank'] = 0
        data['summary'] = description.getText().replace("\u2019","'")
        data['price'] = price
        data['source'] = "4-parisBouge"

        yield data


if __name__ == "__main__":
    try:
        os.remove("backend/exhibition/expo_scraper/extracted_data/parisBouge.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/parisBouge.jsonl'
    })

    process.crawl(Expo_parisbouge_Spider)
    process.start() # the script will block here until the crawling is finished