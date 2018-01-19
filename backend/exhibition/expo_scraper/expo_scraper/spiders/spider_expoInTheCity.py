# spider to scrap url of exhibitions from expointhecity.com

import os
import json
from dateparser import parse as dp
from bs4 import BeautifulSoup
from unicodedata import normalize
import scrapy
from scrapy.crawler import CrawlerProcess

class Expo_expoInTheCity_Spider(scrapy.Spider):
    name = "expo_expoInTheCity"
    
    start_urls = [
        "http://www.expointhecity.com/category/photo-addicts/",
        "http://www.expointhecity.com/category/sculpture/",
        "http://www.expointhecity.com/category/classique/",
        "http://www.expointhecity.com/category/contemporain/",
        "http://www.expointhecity.com/category/en-famille/",
        "http://www.expointhecity.com/category/les-gratuits/",
        "http://www.expointhecity.com/category/mode/",
        "http://www.expointhecity.com/category/les-incontournables/",
        "http://www.expointhecity.com/category/envie-dailleurs/",
    ]

    def parse(self, response):
        
        expo_list = response.xpath("//div[@class = 'col s1-3 post-preview']")

        for expo in expo_list:
            try:
                title = expo.xpath(".//h3//a/text()").extract_first().replace("\u2019","'")
                if "Passée au crible" in title: 
                    title = title[18:]
            except:
                title = "Titre non disp."
            try:
                img_url = expo.xpath(".//img/@src").extract_first()
            except:
                img_url = ""
            try:
                url = expo.xpath(".//a/@href").extract_first()
            except:
                url = ""

            try:
                dates = expo.xpath('.//p/text()').extract_first().split("-")[0].lower().replace("du", "").split("au")
                d_start = dp(dates[0]).strftime("%Y-%m-%d")
                d_end = dp(dates[1]).strftime("%Y-%m-%d")
            except:
                d_start = "2000-01-01"
                d_end = "2000-01-01"
            
            try:
                location = " ".join(expo.xpath('.//p/text()').extract_first().split("-")[1].split("//")[0].split())
            except:
                location = "Lieu indisp."


            genre = response.xpath("//h1/text()").extract_first()
            if genre == 'photo-addicts':
                genre = 'photographie'
            elif genre == 'les-gratuits':
                genre = 'gratuit'
            elif genre == 'les-incontournables':
                genre = 'incontournable'
            elif genre == 'envie-dailleurs':
                genre = 'autres'
            elif genre == 'en-famille':
                genre = 'famille'
            
            request_details = scrapy.Request(url, self.parse_details)
            request_details.meta['data'] =  {
                'title': title,
                'img_url': img_url,
                'd_start' :d_start,
                'd_end': d_end, 
                'genre': genre,
                'location': location,
                'tags': [genre],
            }
            yield request_details

    def parse_details(self, response):
        data = response.meta['data']
        
        try:
            d = BeautifulSoup("\n".join(response.xpath("//p[@style = 'text-align: justify;']").extract()))
            description = d.getText().replace("\u2019","'")
        except:
            description = "Description indisp."

        try:
            ttb = BeautifulSoup(response.xpath("//div[@class='biz-hours']").extract_first().replace("</h4>"," : ").replace(" </li>", ". "))
            timetable = ttb.getText()
        except:
            timetable = "Horaires indisp."

        try:
            p = BeautifulSoup(response.xpath("//div[@class='fee-kind']").extract_first().replace("</h4>", "\n").replace('class ="fee-conditions">', '> (').replace("</ul>", ")").replace("</li>", ". "))
            price = normalize("NFKD", p.getText())
        except:
            price = "Tarifs indisp."

        data['url'] = response.url
        data['timetable'] = timetable
        data['reviews'] = ""
        data['rank'] = 0
        data['summary'] = description
        data['price'] = price
        data['source'] = "3-expoInTheCity"
        
        yield data


if __name__ == "__main__":
    try:
        os.remove("backend/exhibition/expo_scraper/extracted_data/expoInTheCity.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/expoInTheCity.jsonl'
    })

    process.crawl(Expo_expoInTheCity_Spider)
    process.start() # the script will block here until the crawling is finished