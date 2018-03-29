# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from scrapy.crawler import CrawlerProcess
import os


class MatchDesCritiquesSpider(scrapy.Spider):
    name = "critiques"
    start_urls = ['https://www.senscritique.com/films/toujours-a-l-affiche']

    #fonction appelée de base, elle permet d'extraire tous les url des films à l'affiche:
    def parse(self,response):

        #récupérer la liste de toutes les urls des films dans la section "à l'affiche)
        film_liste=response.css("body.dark-theme").css("ul.elpr-list").css("li.elpr-item")
        for f in film_liste:
            #récupérer le titre et l'url: film_url = "https://www.senscritique.com/film/"+url récupéré, pareil pour le titre
            film_url= "https://www.senscritique.com"+str(f.css("h2.d-heading2.elco-title").css("a::attr(href)").extract()[0])
            titre=f.css("h2.d-heading2.elco-title").css("a::text").extract()[0]
            request_details=scrapy.Request(film_url, self.parse_critique)
            request_details.meta['data']= {
                'titre': titre,
                'film_url':film_url
            }
            yield request_details
            #renvoie le dico complet


    def parse_critique(self, response):
        #récupération des infos envoyées dans le dico au moment de la requête (cf au dessus)
        data= response.meta["data"]
        try :
            critique1=response.css("section.d-rubric-inner.d-border-top").css("p.ere-review-excerpt::text").extract()[0].replace("\n"," ").replace("\t"," ").replace("\n\t\t\t\t"," ")
        except:
            critique1="critique indisponible"


        try:
            critique2 =response.css("section.d-rubric-inner.d-border-top").css("p.ere-review-excerpt::text").extract()[2].replace("\n"," ").replace("\t"," ").replace("\n\t\t\t\t"," ")
        except:
            critique2 = "critique indisponible"

        data["critique_1"] = critique1
        data["critique_2"] = critique2
        data["note_critique_1"]=response.css("body.dark-theme").css("section.d-rubric-inner.d-border-top").css("span.elrua-useraction-inner.only-child::text").extract()[0].replace("\n\t\t\t\t\t"," ").replace("\t\t\t\t"," ")
        data["note_critique_2"]=response.css("body.dark-theme").css("section.d-rubric-inner.d-border-top").css("span.elrua-useraction-inner.only-child::text").extract()[1].replace("\n\t\t\t\t\t"," ").replace("\t\t\t\t"," ")
        data["critique_1_url"]="https://www.senscritique.com"+str(response.css("section.d-rubric-inner.d-border-top").css("p.ere-review-excerpt").css("a.ere-review-anchor").css('a::attr(href)').extract()[0])
        data["critique_2_url"]="https://www.senscritique.com"+str(response.css("section.d-rubric-inner.d-border-top").css("p.ere-review-excerpt").css("a.ere-review-anchor").css('a::attr(href)').extract()[1])

        # yield renvoie le dico contenant toutes les informations, donc yield data
        yield data

if __name__ == "__main__":
    try:
        os.remove("/Users/constanceleonard/Desktop/strolling/backend/cinema/senscritiquescrapping/extracted-data/critiques_films.jsonl")
    except OSError:
        pass

    process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'FEED_FORMAT': 'jsonlines',
            'FEED_URI': '/Users/constanceleonard/Desktop/strolling/backend/cinema/senscritiquescrapping/extracted-data/critiques_films.jsonl'
        })
    process.crawl(MatchDesCritiquesSpider)
    process.start() # the script will block here until the crawling is finished
            

