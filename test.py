from backend.messenger.msg_fct import user_details
from backend.language.handle_text import *
from pprint import pprint 

msg = "une expo sur jean fautrier"
pprint(get_exhib_query(vect_search(msg), ["All"], 1))


# sender = 1680982418636079
# ACCESS_TOKEN = "EAAHSfldMxYcBAAt4D30ZAzVHSnhhFqxV15wMJ0RwZCOBH4MZALBJOa8gTvUV0OTL5t3Q4ZBOosziQ3AXIwYpgpdbJCRRkbJKBuB7FASzhnZAcZCsy6expZATAbflsnln2Hd5I1Yo8J2Ddny170yI13r7A224a20yBWczLeYZAzZBDTQZDZD"
# user_details(sender, ACCESS_TOKEN)