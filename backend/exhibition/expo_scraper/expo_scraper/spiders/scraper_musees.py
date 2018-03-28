import scrapy
import os
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

        categorie = response.css("div.Row.Row--visitors.spaceBefore--2.phoneSpaceBefore--0 div.Row-content-c3 div.Main-column article.Article-full header.Heading h1.Heading--title::text").extract_first()
        categorie_sous_titre = response.css("div.Row.Row--visitors.spaceBefore--2.phoneSpaceBefore--0 div.Row-content-c3 div.Main-column article.Article-full header.Heading h2.Heading--subtitle::text").extract_first()

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


            try:
                img_url = musee.css("figure.Article-line-image a img::attr(src)").extract_first()
            except:
                img_url = ""


            request_details = scrapy.Request(url, self.parse_info)
            request_details.meta["data"] = {
                "Categorie": categorie,
                "What": categorie_sous_titre,
                "name" : name,
                "location" : location,
                "image" : img_url,
            }

            yield request_details


    def parse_info(self, response):
        data = response.meta["data"]
        details_prix_horaires = response.css("div.panel div.Panel-content.collapse div.Panel-content--gutter div.Service-set")
        dict_prixethoraires = {}
        dict_infosutiles = {}
        informations = response.css("div.Row-box")
        liste_images = response.css("div.Light-slider default.Light-slider--visitors div.Light-slider-carousel")
        images_alternatives = []


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
            liste_contenu = " ".join(information.css("div.eztext-field::text").extract())
            dict_infosutiles[type_info] = liste_contenu

        for image in liste_images :
            image_aleatoire = 'https://www.parisinfo.com' + image.css("figure img::attr(src)").extract_first()
            images_alternatives += [image_aleatoire]
        
        toutes_les_keys = []
        for key in dict_infosutiles :
            toutes_les_keys += [key]
        if "Descriptif" not in toutes_les_keys :
            dict_infosutiles["Descriptif"] = "Va visiter le site, je n'ai pas de description à te proposer !"

        data["prix_horaires"] = dict_prixethoraires
        data["infos_utiles"] = dict_infosutiles
        data["images_supplementaires"] = images_alternatives

        yield data


if __name__ == '__main__':
    try:
        os.remove("backend/musees/musees/liste.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'backend/musees/musees/listeM.jsonl'
    })

    process.crawl(MuseesParis)
    process.start()