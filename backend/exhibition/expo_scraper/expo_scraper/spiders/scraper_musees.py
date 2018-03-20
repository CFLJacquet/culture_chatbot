import scrapy
from scrapy.crawler import CrawlerProcess

class MuseesParis(scrapy.Spider):
    name = "museesparisiens"
    start_urls = [
                "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-les-plus-visites",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-beaux-arts-paris",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-art-moderne-contemporain",
                "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-en-famille",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-insolites-de-paris",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-histoire-et-cultures-d-ailleurs-paris",
            ]

    def parse(self, response):
        musee_list = response.css("article.Article-line.Article-line--visitors")

        for musee in musee_list:
            try:
                url = 'https://www.parisinfo.com' + musee.css("figure.Article-line-image a::attr(href)").extract_first()
            except:
                url = ""

            try:
                name = musee.css("header.Article-line-heading h3.Article-line-title a::text").extract_first()
            except:
                name = "Nom non disp."


            try:
                location = musee.css("header.Article-line-heading div.Article-line-info div.Article-line-place::text").extract_first()
            except:
                location = "Lieu indisp."
            print(url)


            request_details = scrapy.Request(url, self.parse_info)
            request_details.meta["data"] = {
                "name" : name,
                "location" : location,
            }

            yield request_details


    def parse_info(self, response):
        data = response.meta["data"]
        details_prix_horaires = response.css("div.panel div.Panel-content.collapse div.Panel-content--gutter div.Service-set")
        dict_prixethoraires = {}
        dict_infosutiles = {}
        informations = response.css("div.Row-box")

        for detail in details_prix_horaires :

            try :
                type_visite = detail.css("p::text").extract_first()
            except :
                type_visite = None

            try :
                info = detail.css("div.eztext-field::text").extract_first()
            except :
                info = None

            dict_prixethoraires[type_visite] = info

        for information in informations :
            type_info = information.css("h2.Heading::text").extract_first()
            contenu = information.css("div.eztext-field::text").extract_first()
            dict_infosutiles[type_info] = contenu

        data["prix_horaires"] = dict_prixethoraires
        data["infos_utiles"] = dict_infosutiles

        yield data


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'jsonlines',
    'FEED_URI': 'backend/exhibition/expo_scraper/extracted_data/museum_list.jsonl'
})

process.crawl(MuseesParis)
process.start()