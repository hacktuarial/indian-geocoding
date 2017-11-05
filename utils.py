import pandas as pd
import numpy as np
import googlemaps
from vincenty import vincenty
import random
import geocoder
import time
import pickle
import key
from constants import (NO_RESPONSE,
                       UNKNOWN_PLACE)


gmaps = googlemaps.Client(key.key2)


def geocode_api(place, sleep):
    """
    use google API directly, using API key
    """
    try:
        gc = gmaps.geocode(place)
        if sleep:
            time.sleep(1 + 2 * random.random())
        if len(gc) > 0:
            return gc[0]
        else:
            return UNKNOWN_PLACE
    except:
        return NO_RESPONSE


def geocode_ip(place):
    " use geocoder, which depends on IP address"
    gc = geocoder.google(place + ', INDIA')
    time.sleep(2)
    if gc.address is None:
        return UNKNOWN_PLACE
    else:
        return gc


def closest_city(p, cities):
    " return index of nearest city to village p and distance in kilometers "
    distances = cities.apply(lambda city: vincenty(p, (city.latitude, city.longitude)), axis=1)
    return (cities.index[np.argmin(distances)], min(distances))


# lat/long is reversed in village_list_tndata_coords_small
def find_closest(f_villages, f_cities):
    " for each village, find the closest city "
    villages = pd.read_csv("data/raw/%s" % f_villages).\
        rename(columns= {"subdist_latitude": "latitude", "subdist_longitude": "longitude"}).\
        rename(columns= {"long": "latitude", "lat": "longitude"})
    cities = pd.read_csv("data/processed/%s" % f_cities).\
        rename(columns = {"lat": "latitude", "longi":"longitude"})

    # closest cities is indexed on village
    closest_cities = villages.apply(lambda village: closest_city((village.latitude, village.longitude), cities), axis=1)
    closest_cities = pd.DataFrame({"city_index": closest_cities.apply(lambda x: x[0]),
              "distance": closest_cities.apply(lambda x: x[1])},
             index=closest_cities.index)
    # add city, state to closest_cities
    closest_cities = pd.merge(closest_cities, cities[["city", "state"]],
                              "inner", left_on="city_index", right_index=True)

    villages_appended = pd.merge(villages, closest_cities, "inner",
                                 left_index=True, right_index=True)
    return villages_appended


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
