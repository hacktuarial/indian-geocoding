
# coding: utf-8

# In[2]:

import pandas as pd
import numpy as np
import csv
import pickle
import geocoder
import time
from googlemaps import googlemaps 
gmaps = googlemaps.Client(tKey)


# # Text matching

# Read in the data

# In[35]:

rraw = pd.read_csv("/Users/timothysweetser/Box Sync/Anna/village_kin/kin_locations_clean.csv", dtype=str)
print len(rraw.index)
rraw.dropna(inplace=True)
print len(rraw.index)
print rraw.head(10)


# ### File input/output

# In[45]:

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


# In[8]:

k_no_response = 'no response from google API'
def geocode_api(place):
    # use google API directly, using API key
    try: 
        gc = gmaps.geocode(place + ', INDIA')
        time.sleep(2)
        if len(gc) > 0:
            return gc[0]
        else:
            return 'NA'
    except:
        return k_no_response

def geocode_ip(place):
    # use geocoder, which depends on IP address
    gc = geocoder.google(place + ', INDIA')
    time.sleep(2)
    if gc.address == None:
        return 'NA'
    else:
        return gc


# In[40]:

matches = {}


# In[41]:

for index, row in rraw.iterrows():
    place_state = row.village_kin + ", " + row.state_respondent
    matches[place_state] = geocode_api(place_state)


# In[46]:

print len(matches)
save_obj(matches, "/Users/timothysweetser/Box Sync/Anna/village_kin/matches_v2")


# In[47]:

print "There are %d total" % raw.nunique()
print "%d have been done " % len(matches)
print "There are %d left to do" %(raw.nunique() - len(matches))


# In[48]:

matches[matches.keys()[15]]['formatted_address']


# In[49]:

print matches[matches.keys()[15]]['geometry']['location']['lat']
print matches[matches.keys()[15]]['geometry']['location']['lng']


# In[64]:

matches_select = {}
for place, val in matches.iteritems():
    if type(val) == dict:
        matches_select[place] = {'GMaps match':val['formatted_address'],             'latitude':val['geometry']['location']['lat'], 'longitude':val['geometry']['location']['lng']}
    else:
        matches_select[place] = {'GMaps match': 'NA', 'latitude':np.nan, 'longitude':np.nan}
        
matches_select = pd.DataFrame.from_dict(matches_select, orient='index').reset_index()
matches_select.rename(columns={'index':'village_kin'}, inplace=True)
matches_select['state_respondent'] = matches_select['village_kin'].apply(lambda x: x.split(",")[1])
matches_select['village_kin'] = matches_select['village_kin'].apply(lambda x: x.split(",")[0])
# reorder columns
matches_select = matches_select[['village_kin', 'state_respondent', 'GMaps match', 'latitude', 'longitude']]
matches_select.head(20)


# In[65]:

matches_select.to_csv('/Users/timothysweetser/Box Sync/Anna/village_kin/google maps suggestions lat long v2.txt',                     sep='\t', index=False, encoding='utf-8')

