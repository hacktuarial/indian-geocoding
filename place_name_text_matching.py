"""
Match survey responses to known place names using Levenshtein edit distance
"""
from collections import defaultdict
import os
import pickle
import logging
import pandas as pd
import numpy as np
from Levenshtein import distance as edit_distance
import click

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)


@click.command()
@click.option('--use-cache')
def main(use_cache):
    # constants
    folder = os.path.join('2017', 'data')
    survey_responses = 'kin_locations_clean_id_11032017.csv'
    names_of_cities = 'mc_list_v2_june2017_officialhistoricnames.csv'
    # read in data
    df_raw = pd.read_csv(os.path.join(folder, 'raw', survey_responses),
                         dtype=str)
    big_cities = pd.read_csv(os.path.join(folder, 'raw', names_of_cities),
                             dtype=str,
                             usecols=['mc', 'state'])
    big_cities['state'].fillna('NONE', inplace=True)
    results_file = os.path.join(folder, 'processed', 'results.p')
    if os.path.exists(results_file) and use_cache:
        logging.info("reading pickled matches from disk")
        with open(results_file, 'rb') as ff:
            matches = pickle.load(ff)
    else:
        logging.info("computing matches")
        matches = pairwise_comparison(raw_names=df_raw['village_kin'].dropna(),
                                      big_cities=big_cities)
        logging.info("writing matches to disk")
        with open(results_file, 'wb') as ff:
            pickle.dump(matches, ff)
    results = pick_best_match(matches)
    df_results = results_to_df(results, df_raw)
    # write to file
    df_results.to_csv(os.path.join(folder, 'processed', 'suggestions.txt'),
                      sep='\t', index=False)


def pairwise_comparison(raw_names, big_cities):
    " do comparisons"
    matches = defaultdict(dict)
    # for each raw place name, see how well it matchs the name of a big city
    for raw_name in raw_names:
        # loop over big cities
        for _, row in big_cities.iterrows():
            big_city = row['mc']
            key = ', '.join(row)  # city, state
            # the first letters MUST match
            if raw_name[0].lower() != big_city[0].lower():
                matches[raw_name][key] = np.inf
            else:
                matches[raw_name][key] = edit_distance(raw_name.lower(),
                                                       big_city.lower())
    return matches


def pick_best_match(matches):
    """
    look through the list of matches, picking the best one
    if multiple places have the same minimum distance,
    keep all of them
    """
    results = {}
    for raw_name in matches:
        min_value = min(matches[raw_name].values())
        # there could be multiple names with min edit distance;
        # keep all of them
        min_keys = [k for k in matches[raw_name]
                    if matches[raw_name][k] == min_value]
        results[raw_name] = ';'.join(min_keys)
    return results


def results_to_df(results, df_raw):
    " Convert results dictionary to dataframe and merge with original data "
    # output to file
    df_results = pd.DataFrame.from_dict(results, orient='index').reset_index()
    df_results.columns = ['village_kin', 'suggestions']
    df_results = pd.merge(df_results, df_raw,
                          how='inner', on='village_kin')
    n_original = df_raw.shape[0]
    n_final = df_results.shape[0]
    logging.info("i started with %d row", n_original)
    logging.info("i finished with %d villages", n_final)
    return df_results[['village_kin', 'state_respondent', 'suggestions']]


if __name__ == '__main__':
    main()
