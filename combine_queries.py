"""
We queried the google maps API 2 ways:
    with and without the state
    e.g. "place, INDIA" (without state)
    "place, TAMIL NADU, INDIA" (with state)
This script combines these two results
"""

import os
import logging
import numpy as np
import pandas as pd
import utils
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)


def parse_matches(matches):
    " extract relevant entries from GMaps json "
    matches_select = {}
    for place, val in matches.items():
        if isinstance(val, dict):
            matches_select[place] = {
                    'GMaps match': val['formatted_address'],
                    'latitude': val['geometry']['location']['lat'],
                    'longitude': val['geometry']['location']['lng']
                    }
        else:
            matches_select[place] = {
                    'GMaps match': 'NA',
                    'latitude': np.nan,
                    'longitude': np.nan
                    }
    return matches_select


def matches_to_df(matches):
    " convert matches to dataframe and write to disk "
    df_matches = pd.DataFrame.\
        from_dict(matches, orient='index').\
        reset_index().\
        rename(columns={'index': 'village_kin'})
    df_matches['state_respondent'] = df_matches['village_kin'].apply(
        lambda x: x.split(",")[1])
    df_matches['village_kin'] = df_matches['village_kin'].apply(
        lambda x: x.split(",")[0])
    # reorder columns
    df_matches = df_matches[['village_kin', 'state_respondent',
                             'GMaps match', 'latitude', 'longitude']]

    def extract(s, i):
        try:
            res = s.split(',')[i]
            # remove numbers
            res = ''.join([r for r in res if not r.isdigit()]).strip()
        except IndexError:
            res = np.nan
        return res

    df_matches['gmaps_place'] = df_matches['GMaps match'].apply(lambda x: extract(x, 0))
    df_matches['gmaps_state'] = df_matches['GMaps match'].apply(lambda x: extract(x, 1))
    return df_matches


def main():
    # constants
    folder = os.path.join('2017', 'data')
    output_file = 'google_to_search_matches_20171104.csv'
    survey_responses = 'kin_locations_clean_id_11032017.csv'
    # read in data
    df_raw = pd.read_csv(os.path.join(folder, 'raw', survey_responses),
                         dtype=str)
    # clean up
    logging.info("Started with %d answers", df_raw.shape[0])
    df_raw = df_raw[~pd.isnull(df_raw['village_kin'])]
    matches_files = ['2017/data/processed/kin_location_geocode']
    matches_files.append(matches_files[0] + '_no_state')
    matches = [utils.load_obj(m) for m in matches_files]
    df_matches = [matches_to_df(parse_matches(m))
                  for m in matches]
    # for the second one, we didn't use state respondent, so drop it
    df_matches[1].drop('state_respondent', axis=1, inplace=True)
    df_combined = pd.merge(df_matches[0], df_matches[1],
                           how='outer',
                           on=['village_kin'],
                           suffixes=['_with_state', '_without_state']
                           )
    df_combined.to_csv(os.path.join(folder, 'processed', output_file),
                       index=False)


if __name__ == '__main__':
    main()
