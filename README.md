# indian-geocoding
* Query google maps to validate cities of residence provided as part of an Indian survey
* Use Levenstein edit distance to resolve differences in names
* Use the google maps API to get latitude, longitude coordinates of cities
* Use vincenty distance to calculate between each village and the nearest city

# order
* place name text matching: use Levenshtein edit distance to compare 2 lists of places
* query_google_maps, 2 ways: with and without the respondent's state
* combine queries: combine results of above into one dataframe
