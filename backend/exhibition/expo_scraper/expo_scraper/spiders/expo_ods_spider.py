# spider to scrap data from l'office des spectacles
# need to update the 'start_url' each month

import os
from unicodedata import normalize
import scrapy
from scrapy.crawler import CrawlerProcess
from dateparser import parse

class Expo_offspec_Spider(scrapy.Spider):
    name = "expo_offspec"
    
    start_urls = [
        'https://www.offi.fr/expositions-musees/mois-12-2017.html?npage=1',
    ]

    def parse(self, response):

        for expo in response.css("div.oneRes"):
            try:
                title = ' '.join(expo.css("div.eventTitle strong a span::text").extract_first().split())
            except:
                title = "Titre non disp."
            try:
                genre = ' '.join(expo.xpath(".//li[contains(.,'{}')]//text()".format('Rubrique')).extract()[1][2:].split())
            except:
                genre = "En cours"
            try:
                img_url = expo.css("div.resVignette a img::attr(src)").extract_first()
            except:
                img_url = ""
            try:
                url = response.urljoin(expo.css("div.resVignette a::attr(href)").extract_first())
            except:
                url = ""
            try:
                timetable = ' '.join(expo.xpath(".//li[contains(.,'{}')]//text()".format('Programmation')).extract()[1].split())
            except:
                timetable = "Horaires non disp."
            try:
                date_start = parse(expo.xpath(".//li[contains(.,'{}')]//text()".format('Date de début')).extract()[1]).strftime("%Y-%m-%d")
            except:
                date_start = "Date de départ non disp."
            try:
                date_end = parse(expo.xpath(".//li[contains(.,'{}')]//text()".format('Date de fin')).extract()[1]).strftime("%Y-%m-%d")
            except:
                date_end = "Date de fin non disp."
            try:
                location = expo.xpath(".//li[contains(.,'Lieu')]//a//text()").extract_first() + " " + " ".join(expo.xpath(".//li[contains(.,'{}')]//text()".format('Lieu')).extract()[3].split())
            except:
                location = "Lieu non disp."

            request_details = scrapy.Request(url, self.parse_details)
            request_details.meta['data'] = {
                'title': title,
                'img_url': img_url,
                'url': url,
                'genre': genre,
                'location': location,
                'd_start': date_start, 
                'd_end': date_end,
                'timetable': timetable,
                'reviews':"",
                'rank':0
            }

            yield request_details 

        next_page = response.css("div.dayNav ul li.last a::attr(href)").extract_first()
        if next_page != '/expositions-musees/mois-12-2017.html?npage=1':
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        

    def parse_details(self, response):
        data = response.meta['data']
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

        data['summary'] = normalize('NFC', s)
        data['price'] = price

        yield data


if __name__ == "__main__":
    try:
        os.remove("backend/exhibition/expo_scraper/extracted_data/offSpectacles.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/offSpectacles.jsonl'
    })

    process.crawl(Expo_offspec_Spider)
    process.start() # the script will block here until the crawling is finished