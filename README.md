# Project Strolling bot

FB Messenger chatbot that recommends you cultural events in Paris (exhibition, movie...) based on the user's interest.

### Website: https://www.strolling.club/ 

# Back-end Structure:   

├── backend   
│   ├── cinema  
│   ├── exhibition  
│   │   ├── expo_scraper  
│   │   │   └── expo_scraper  
│   │   │       └── spiders  
│   │   └── README.txt  
│   ├── language   
│   ├── messenger   
│   └── others  
├── static   
├── README.md                   
├── server.py                 
├── uwsgi_config.ini                  
└── wsgi.py             

# Environment 

(virtualenv): Python 3.5  

### Installed libraries:  
* flask   
* uwsgi (not needed on local machines to dev)  
* schedule -> to schedule python jobs  

* scrapy -> to scrape website info  
* BS4 -> to scrape trickier parts

* dateparser -> to transform dates in French in date objects
* nltk -> to work on text  
* treetaggerwrapper (+TreeTagger) -> to tag and lemmatize French   (http://treetaggerwrapper.readthedocs.io/en/latest/)   

* pandas -> to concatenate text from different sources
* numpy -> to handle some table operations
* sklearn -> to use machine learning algorithms

* PIL (pillow) -> to transform image size, download version 4.3.0 (type in console: pip install 'pillow==4.3.0')


