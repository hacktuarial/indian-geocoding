import pandas as pd
import numpy as np
import csv
import Levenshtein


# # Text matching

# Read in the data
rraw = pd.read_csv("/Users/timothysweetser/Box Sync/Anna/village_kin/kin_locations.csv", dtype=str)
raw = rraw['village_kin']
raw = raw[~pd.isnull(raw)]
clean = pd.read_csv("/Users/timothysweetser/Box Sync/Anna/village_kin/clean_names.csv", dtype=str)
clean['state'][pd.isnull(clean['state'])] = 'NONE'


# In[11]:

matches = {}
for raw_name in raw:
    matches[raw_name] = {}
    for index, row in clean.iterrows():
        clean_name = row['name_short']
        key = ', '.join(row) # city, state
        
        # the first letters MUST match
        if raw_name[0] != clean_name[0]:
            matches[raw_name][key] = np.inf
        else:
            matches[raw_name][key] = Levenshtein.distance(raw_name, clean_name)


# In[12]:

results = {}
from scipy.stats import rankdata
for raw_name in matches.keys():
    min_value = min(matches[raw_name].itervalues())
    min_keys = [k for k in matches[raw_name] if matches[raw_name][k] == min_value]
    results[raw_name] = ';'.join(min_keys)


# In[14]:

resultsDF = pd.DataFrame.from_dict(results, orient='index').reset_index()
resultsDF.columns = ['village_kin', 'suggestions']
resultsDF = resultsDF.merge(rraw, 'inner', 'village_kin')

print len(rraw.index)
print len(resultsDF.index) # dropped 1 NA
resultsDF = resultsDF[['village_kin', 'state_respondent', 'suggestions']]


# In[16]:

# write to file
filename = "/Users/timothysweetser/Box Sync/Anna/village_kin/suggestions.txt"
resultsDF.to_csv(filename, sep="\t", index=False)

