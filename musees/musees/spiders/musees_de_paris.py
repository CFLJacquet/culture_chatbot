# import scrapy
# from scrapy import Field, Item
# from scrapy.selector import Selector
# from scrapy.http import HtmlResponse
# # from musees.spiders.item import Info
# from scrapy.crawler import CrawlerProcess
#
#
# class MuseesParis(scrapy.Spider):
#     name = "musee"
#
#     urls = [
#         "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-les-plus-visites",
#         "https://www.parisinfo.com/visiter-a-paris/musees/musees-beaux-arts-paris",
#         "https://www.parisinfo.com/visiter-a-paris/musees/musees-art-moderne-contemporain",
#         "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-en-famille",
#         "https://www.parisinfo.com/visiter-a-paris/musees/musees-insolites-de-paris",
#         "https://www.parisinfo.com/visiter-a-paris/musees/musees-histoire-et-cultures-d-ailleurs-paris",
#         "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-et-monuments-gratuits-a-paris"
#     ]
#
#
#     def parse(self, response):
#         for url in self.urls:
#             for musee in response.css("article.Article-line.Article-line--visitors"):
#                 yield {
#                     "nom": musee.css("header.Article-line-heading h3.Article-line-title a::text").extract_first(),
#                     "adresse": musee.css(
#                         "header.Article-line-heading div.Article-line-info div.Article-line-heading::text").extract_first(),
#                     "lien": 'https://www.parisinfo.com' + musee.css("figure.Article-line-image a::attr(href)").extract_first(),
#                 }
#
# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#     'FEED_FORMAT': 'jsonlines',
#     'FEED_URI': 'musees/musees/spiders/musees_de_paris.jsonl'
# })
#
# process.crawl(MuseesParis)
# process.start()








from unicodedata import normalize
import os
import scrapy
import os, sys
from scrapy.crawler import CrawlerProcess
from dateparser import parse
import json

class MuseesParis(scrapy.Spider):
    name = "museesparisiens"
    dict_categories = {}
    dict_genres = {}
    dict_musees = {}
    dict_prix_horaires = {}

    def __init__(self):
        self.urls = [
                "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-les-plus-visites",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-beaux-arts-paris",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-art-moderne-contemporain",
                "https://www.parisinfo.com/visiter-a-paris/musees/les-musees-en-famille",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-insolites-de-paris",
                "https://www.parisinfo.com/visiter-a-paris/musees/musees-histoire-et-cultures-d-ailleurs-paris",
            ]
        # self.liste = []
        for url in self.urls :
            url = list(url.split("/"))
            # liste = []
            MuseesParis.dict_categories[url[-1]] = []
            # liste = []
            # yield scrapy.Request(url, callback=self.remplircategories)
            # MuseesParis.dict_categories[url[-1]] += self.liste
        # MuseesParis.dict_categories["les-musees-les-plus-visites"] += []
        # MuseesParis.dict_categories["musees-beaux-arts-paris"] = []
        # MuseesParis.dict_categories["musees-art-moderne-contemporain"] = []
        # MuseesParis.dict_categories["les-musees-en-famille"] = []
        # MuseesParis.dict_categories["musees-insolites-de-paris"] = []
        # MuseesParis.dict_categories["musees-histoire-et-cultures-d-ailleurs-paris"] = []
        print(MuseesParis.dict_categories)


    # def remplircategories(self, response):
    #     musees_list = response.css("article.Article-line.Article-line--visitors")
    #     for musee in musees_list :
    #         try:
    #             title = musee.css("header.Article-line-heading h3.Article-line-title a::text").extract_first()
    #         except:
    #             title = "Titre non disp."
    #         self.liste += [title]



    def start_requests(self):

        for url in self.urls:

            #categorie = url.css("header.Article-line-heading h3.Article-line-title a::text").extract_first()
            yield scrapy.Request(url, callback=self.parse_details)
            # requests.append(request_details)
        # print(len(requests))
        # print(requests[1])

        # return requests

    def parse_details(self, response):
        # Open file
        # fd = open("toto.html",'w+')
        # fd.write(response.texxt)
        # fd.close()
        musees_list = response.css("article.Article-line.Article-line--visitors")
        nom_de_la_categorie = response.css("div.Row Row--visitors.spaceBefore--2.phoneSpaceBefore--0 div.Breadcrumbs-list li::text").extract_first()
        premiers_details = []
        MuseesParis.dict_genres[nom_de_la_categorie] = []

        for musee in musees_list:

            try:
                title = musee.css("header.Article-line-heading h3.Article-line-title a::text").extract_first()
            except:
                title = "Titre non disp."

            try:
                img_url = musee.css("figure.Article-line-image a img::attr(src)").extract_first()
            except:
                img_url = ""

            try:
                url = 'https://www.parisinfo.com' + musee.css("figure.Article-line-image a::attr(href)").extract_first()
            except:
                url = ""

            try:
                location = musee.css(
                    "header.Article-line-heading div.Article-line-info div.Article-line-place::text").extract_first()
            except:
                location = "Lieu indisp."
            premiers_details = [location, img_url, url]

            if title not in MuseesParis.dict_musees :
                MuseesParis.dict_musees[title] = [location, img_url, url]
                yield scrapy.Request(url, callback=self.parse_info)

            MuseesParis.dict_genres[nom_de_la_categorie] += [musee]



        # for key in MuseesParis.dict_musees :
        #     yield scrapy.Request(MuseesParis[key][2], callback=self.parse_info)

            # MuseesParis.dict_musees[title] = [location, img_url, url]
        # print(MuseesParis.dict_musees)
        yield



    def parse_info(self, response):
        details_prix_horaires = response.css("div.panel div.Panel-content.collapse div.Panel-content--gutter div.Service-set")
        dict_details = {}
        nom_du_musee = response.css("div.Figure-header header.Figure-header--heading div.Figure-header--title-area h1.Figure-header--title::text").extract_first()

        for detail in details_prix_horaires :

            try :
                type_visite = detail.css("p::text").extract_first()
            except :
                type_visite = None

            try :
                info = detail.css("div.eztext-field::text").extract_first()
            except :
                info = None

            dict_details[type_visite] = info

        MuseesParis.dict_prix_horaires[nom_du_musee] = dict_details
        # print(MuseesParis.dict_prix_horaires)
        yield


        # descriptif = response.css("h2.Heading::text").extract_first()
        # point_de_vue = response.css("div.margin-bottom:20px div.eztext-field::text").extract_first()



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'jsonl',
    'FEED_URI': 'liste_musees_paris.jsonl'
})

process.crawl(MuseesParis)
process.start()

print(MuseesParis.dict_musees)
print(MuseesParis.dict_prix_horaires)
print(MuseesParis.dict_genres)