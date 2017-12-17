Source code of Strolling bot

Structure:   
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

Environment (virtualenv): Python 3.5  

Installed libraries:  
- flask   
- uwsgi (not needed on local machines to dev)  
- schedule -> to schedule python jobs  
- scrapy -> to scrape website info  
- dateparser -> to transform dates in French in date objects  
- treetaggerwrapper (+TreeTagger) -> to tag and lemmatize French   (http://treetaggerwrapper.readthedocs.io/en/latest/)   

