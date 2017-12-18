# spider to scrap data from l'office des spectacles

import scrapy
from scrapy.crawler import CrawlerProcess

class Expo_offspec_Spider(scrapy.Spider):
    name = "expo_offspec"
    
    start_urls = [
        'https://www.offi.fr/expositions-musees/mois-12-2017.html?npage=1',
    ]

    def parse(self, response):

        for i, expo in enumerate(response.css("div.oneRes")):
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
                prog = ' '.join(expo.xpath(".//li[contains(.,'{}')]//text()".format('Programmation')).extract()[1].split())
            except:
                prog = "Horaires non disp."
            try:
                date_start = expo.xpath(".//li[contains(.,'{}')]//text()".format('Date de début')).extract()[1] #date en francais en str -> besoin de transformer avec dateparser plus tard
            except:
                date_start = "Date de départ non disp."
            try:
                date_end = expo.xpath(".//li[contains(.,'{}')]//text()".format('Date de fin')).extract()[1]
            except:
                date_end = "Date de fin non disp."
            try:
                location = expo.xpath(".//li[contains(.,'Lieu')]//a//text()").extract_first() + " " + " ".join(expo.xpath(".//li[contains(.,'{}')]//text()".format('Lieu')).extract()[3].split())
            except:
                location = "Lieu non disp."
            try:
                description = ' '.join(' '.join(expo.css("div.oneRes::text").extract()).split())
            except:
                description = "Descr. non disp."


            yield {
                'title': title,
                'type': genre,
                'img_url': img_url,
                'url': url,
                'prog': prog,
                'date_start': date_start, 
                'date_end': date_end,
                'location': location,
                'description': description
            }

        next_page = response.css("div.dayNav ul li.last a::attr(href)").extract_first()
        if next_page != '/expositions-musees/mois-12-2017.html?npage=1':
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/offSpec_main.jsonl'
    })

    process.crawl(Expo_offspec_Spider)
    process.start() # the script will block here until the crawling is finished