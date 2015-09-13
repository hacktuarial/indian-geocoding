
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import csv
import pickle
import geocoder
import time
from googlemaps import googlemaps 
gmaps = googlemaps.Client(tKey, timeout=10)


# # Text matching

# Read in the data

# In[2]:

rraw = pd.read_csv("/Users/timothysweetser/Box Sync/Anna/village_kin/kin_locations_noexactmatch_clean.csv", dtype=str)
raw = rraw['village_kin']
raw = raw[~pd.isnull(raw)]
clean = pd.read_csv("/Users/timothysweetser/Box Sync/Anna/village_kin/clean_names.csv", dtype=str)
clean['state'][pd.isnull(clean['state'])] = 'NONE'
clean.head()


# In[9]:

place = 'VASAI'
print place in raw
print place in matches.keys()
matches[place]


# In[12]:

rraw[pd.isnull(rraw['village_kin'])]


# ### File input/output

# In[6]:

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


# In[7]:

filename = "/Users/timothysweetser/box sync/anna/village_kin/matches_so_far"
matches = load_obj(filename)
print len(matches)


# In[86]:

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


# In[29]:

print gc[0]['formatted_address']
print gc[0]['geometry']['location']


# In[7]:

for place in raw:
    if not (place in matches.keys()):
        # first pass done with a mix of ip and api calls


# In[36]:

print len(matches)
save_obj(matches, filename)


# In[13]:

print "There are %d total" % raw.nunique()
print "%d have been done " % len(matches)
print "There are %d left to do" %(raw.nunique() - len(matches))


# In[27]:

resultsDF = pd.DataFrame.from_dict(matches, orient='index').reset_index()
resultsDF.columns = ['village_kin', 'GMaps match']
resultsDF = resultsDF.merge(rraw, 'inner', 'village_kin')

print len(rraw.index)
print len(resultsDF.index) # dropped 1 NA
resultsDF = resultsDF[['village_kin', 'state_respondent', 'GMaps match']]
print resultsDF.head()
no_match = resultsDF['GMaps match'] == 'NA'
print "%d had no match" % sum(no_match)
import random
resultsDF.ix[no_match].tail(10)


# In[35]:

# write to file
filename = "/Users/timothysweetser/Box Sync/Anna/village_kin/google maps suggestions.txt"
resultsDF.to_csv(filename, sep="\t", index=False, encoding='utf-8')


# ### Second pass - add lat/long

# In[166]:

#take2 = {}
for place, val in matches.iteritems():
    if place not in take2.keys():
        take2[place] = geocode_api(place)

save_obj(take2, "/Users/timothysweetser/box sync/anna/village_kin/matches_take2")


# In[167]:

counter = 0L
for val in take2.values():
    if val == 'NA':
        counter += 1
print counter


# In[168]:

counter = 0L
for val in take2.values():
    if val == k_no_response:
        counter += 1
print counter


# In[169]:

len(take2)


# In[94]:

# try 'no responses' again
for place, val in take2.iteritems():
    if val == 'no response from google API':
        #take2[place] = geocode_api(place)
        print place


# In[179]:

save_obj(take2, "/Users/timothysweetser/box sync/anna/village_kin/matches_take2")


# In[171]:

take2[take2.keys()[15]]['formatted_address']


# In[173]:

print take2[take2.keys()[15]]['geometry']['location']['lat']
print take2[take2.keys()[15]]['geometry']['location']['lng']


# In[174]:

take2_select = {}
for place, val in take2.iteritems():
    if type(val) == dict:
        take2_select[place] = {'GMaps match':val['formatted_address'],             'latitude':val['geometry']['location']['lat'], 'longitude':val['geometry']['location']['lng']}
    else:
        take2_select[place] = {'GMaps match': 'NA', 'latitude':np.nan, 'longitude':np.nan}
        
take2_select = pd.DataFrame.from_dict(take2_select, orient='index').reset_index()
take2_select.rename(columns={'index':'village_kin'}, inplace=True)


# In[175]:

# merge in state_respondent
take2_select = take2_select.merge(rraw, 'inner', 'village_kin')


# In[176]:

take2_select = take2_select[['village_kin', 'state_respondent', 'GMaps match', 'latitude', 'longitude']]
take2_select.head()


# In[165]:

take2_select.to_csv('/Users/timothysweetser/Box Sync/Anna/village_kin/google maps suggestions lat long.txt',                     sep='\t', index=False, encoding='utf-8')


# In[177]:

len(take2_select.index)


# In[178]:

take2_select.head()


# In[ ]:



