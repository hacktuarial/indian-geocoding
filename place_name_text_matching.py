"""
Match survey responses to known place names
"""
import pandas as pd
import numpy as np
import Levenshtein
from scipy.stats import rankdata
from collections import defaultdict
import os


# Read in the data
folder = os.path.join('2017', 'data', 'raw')
df_raw = pd.read_csv(os.path.join(folder, 'raw',
                                  'kin_locations_clean_id_11032017.csv'),
                     dtype=str)
raw_names = df_raw['village_kin'].dropna().apply(lambda s: s.lower())
big_cities = pd.read_csv(os.path.join(folder, 'clean_names.csv'), dtype=str)
big_cities['state'].fillna('NONE', inplace=True)


matches = defaultdict(dict)
# for each raw place name, try to match it to a big city
for raw_name in raw_names:
    # loop over big cities
    for index, row in big_cities.iterrows():
        big_city = row['name_short']
        key = ', '.join(row)  # city, state

        # the first letters MUST match
        if raw_name[0] != big_city[0]:
            matches[raw_name][key] = np.inf
        else:
            matches[raw_name][key] = Levenshtein.distance(raw_name, big_city)


results = {}
for raw_name in matches.keys():
    min_value = min(matches[raw_name].itervalues())
    min_keys = [k for k in matches[raw_name] if matches[raw_name][k] == min_value]
    results[raw_name] = ';'.join(min_keys)


df_results = pd.DataFrame.from_dict(results, orient='index').reset_index()
df_results.columns = ['village_kin', 'suggestions']
df_results = df_results.merge(df_raw, 'inner', 'village_kin')

print(len(df_raw.index))
print(len(df_results.index)) # dropped 1 NA
df_results = df_results[['village_kin', 'state_respondent', 'suggestions']]


# write to file
df_results.to_csv(os.path.join(path, 'processed', 'suggestions.txt'), sep="\t", index=False)
