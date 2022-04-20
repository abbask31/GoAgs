import geocoder
import db_functions
import geopy
from geopy.distance import *

API_KEY = 'AIzaSyBqFc48tsnMHLcWGhIWzwukMw5vFgelDfw'

def location_check_prompt(consent, game_location, ucd_email, ticket):
    # use html alert to ask user to agree to share their location
    if consent:
        game_location = db_functions.game_location(ucd_email, ticket)
        
        user = geocoder.ip('me')
        event = geocoder.google(game_location, key = API_KEY)

        user_coords = (user.lat, user.lng)
        event_coords = (event.lat, event.lng)

        distance = geopy.distance.geodesic(user_coords, event_coords).mi

        return distance

        # if int(distance) <= 1:
        #     db_functions.update_check_in(ucd_email, ticket)

    else:
        return 


