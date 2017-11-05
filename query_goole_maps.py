"""
Run places through the google maps API
"""
import logging
import os
import pandas as pd
import click

import utils
import constants
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)


@click.command()
@click.option('--include-state', type=bool)
@click.option('--sleep', type=bool)
def main(include_state, sleep):
    # constants
    folder = os.path.join('2017', 'data')
    survey_responses = 'kin_locations_clean_id_11032017.csv'
    # read in data
    df_raw = pd.read_csv(os.path.join(folder, 'raw', survey_responses),
                         dtype=str)
    # clean up
    logging.info("Started with %d answers", df_raw.shape[0])
    df_raw = df_raw[~pd.isnull(df_raw['village_kin'])]
    logging.info("After dropping NAs, left with %d answers", df_raw.shape[0])
    # where to save output
    matches_file = '2017/data/processed/kin_location_geocode'
    if not include_state:
        matches_file += '_no_state'
    if os.path.exists(matches_file + '.pkl'):
        matches = utils.load_obj(matches_file)
        logging.info("Read %d queries from %s", len(matches), matches_file)
    else:
        logging.info("Starting from scratch")
        matches = {}
    for _, row in df_raw.iterrows():
        place = [row.village_kin]
        if include_state:
            place.append(row.state_respondent)
        # always add the country
        place.append('INDIA')
        place = ", ".join(place)
        # 1. see if we've already run this query
        try:
            response = matches[place]
        # if not, we need to re-run it
        except KeyError:
            already_run = False
            response = ''
        # if we ran it, but got no response, re-run
        if response == constants.NO_RESPONSE:
            already_run = False
        # if we ran it, and Google didn't recognize it, don't re-run
        elif response == constants.UNKNOWN_PLACE:
            already_run = True
        else:
            already_run = False
        if not already_run:
            matches[place] = utils.geocode_api(place, sleep=sleep)
            utils.save_obj(matches, matches_file)
            logging.info("I have run %d queries", len(matches))

    logging.info("There are %d total", df_raw.shape[0])
    logging.info("%d have been done ", len(matches))
    logging.info("There are %d left to do", (df_raw.shape[0] - len(matches)))


if __name__ == '__main__':
    main()
