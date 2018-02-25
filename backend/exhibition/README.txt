-----------------------------------------------------------------------------
    HOW TO UPDATE EXHIBITIONS DATABASE
-----------------------------------------------------------------------------

Pour récupérer les informations, run indexator.py

NB: pour vérifier la qualité de la classification, utiliser le Jupyter Notebook
verification_classif_expo

-----------------------------------------------------------------------------
    DETAILS
-----------------------------------------------------------------------------

1. Les scrapers (dans /expo_scrapers) récupèrent les informations de
    - l'officiel des spectacles
    - expo In The City
    - Paris Bouge

2. Les classifieurs (dans /expo_classifiers) classifient les expositions :
    - Architecture  
    - Sculpture     + desgin, artisanat
    - Peinture      (en réalité les arts-visuels : peinture, dessin, gravure)
    - Musique 
    - Littérature   + poésie
    - Danse         (en réalité les arts de la scène : théâtre, danse, mime, cirque)
    - Cinéma        + vidéo
    - Photographie

3. Indexator crée un index inversé qui sert lors des recherches full-text


