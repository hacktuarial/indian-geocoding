import pandas as pd
import numpy as np
import googlemaps
from vincenty import vincenty


K_NO_RESPONSE = 'no response from google API'
tKey = 'AIzaSyARU5rBJNB4du2bKDEEDpN5eIyut3biat4'
gmaps = googlemaps.Client(tKey)


def geocode_api(place):
    " use google API directly, using API key"
    try: 
        gc = gmaps.geocode(place + ', INDIA')
        if len(gc) > 0:
            return gc[0]
        else:
            return 'NA'
    except:
        return K_NO_RESPONSE


def closest_city(p, cities):
    distances = cities.apply(lambda city: vincenty(p, (city.latitude, city.longitude)), axis=1)
    return (np.argmin(distances), min(distances))


# lat/long is reversed in village_list_tndata_coords_small
def find_closest(f_villages, f_cities):
    " for each village, find the closest city "
    villages = pd.read_csv("data/raw/%s" % f_villages).\
        rename(columns= {"subdist_latitude": "latitude", "subdist_longitude": "longitude"}).\
        rename(columns= {"long": "latitude", "lat": "longitude"})
    cities = pd.read_csv("data/processed/%s" % f_cities).\
        rename(columns = {"lat": "latitude", "longi":"longitude"})
    closest_cities = villages.apply(lambda village: closest_city((village.latitude, village.longitude), cities), axis=1)
    villages['city_index'] = [c[0] for c in closest_cities]
    villages_appended = pd.merge(villages, cities[["city", "state"]],
                                 'inner', left_on='city_index', right_index=True)
    villages_appended['distance'] = [c[1] for c in closest_cities]
    villages_appended.drop("city_index", axis=1, inplace=True)
    return villages_appended
