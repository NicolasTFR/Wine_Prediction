import argparse
import json
from pathlib import Path
import utils.constants as c
from utils.requester import Requester
import os

#we initialize a "loop" counter to get through the full list
loop=0
#we cannot scap more than 60 pages at once, so breaking down in prices buckets. please adjust to you need
prix=[[3,9],[9,11],[11,13],[13,15],[15,17],[17,20],[20,24],[24,28],[28,32],[32,36],[36,43],[43,53],[53,63],[63,75],[75,100],[100,150],[150,250],[250,350],[350,500],[500,999999]]
start_page = 1

#the loop itself
for loop in range(len(prix)):

    # Instantiates a wrapper over the `requests` package
    r = Requester(c.BASE_URL)

    # Defines the payload, i.e., filters to be used on the search. You can adjust them to your need, for me it was french red wine
    payload = {
        "country_codes[]": "fr", #only french wine
        # "food_ids[]": 20,
        # "grape_ids[]": 3,
        # "grape_filter": "varietal",
         "min_rating": 1, #rating cannot go lower, so all wine
        # "order_by": "ratings_average",
        # "order": "desc",
        "price_range_min": prix[loop][0], #lower price bucket
        "price_range_max": prix[loop][1], #higher price bucket
        # "region_ids[]": 383,
        # "wine_style_ids[]": 98,
        "wine_type_ids[]": 1, #red wine
        # "wine_type_ids[]": 2,
        # "wine_type_ids[]": 3,
        # "wine_type_ids[]": 4,
        # "wine_type_ids[]": 7,
        # "wine_type_ids[]": 24,
    }

    # Performs an initial request to get the number of records (wines)
    res = r.get('explore/explore?', params=payload)
    n_matches = res.json()['explore_vintage']['records_matched']

    #this will help you ensure your buckets are not too big. If you see more than 1200 results, you need to filter more
    print(f'Number of matches: {n_matches} for {prix[loop][0]}_{prix[loop][1]}')

    # Iterates through the amount of possible pages
    for i in range(start_page, int(n_matches / c.RECORDS_PER_PAGE) + 1):
        # Creates a dictionary to hold the data
        data = {}
        data['wines'] = []

        # Adds the page to the payload
        payload['page'] = i

        print(f'Page: {payload["page"]}')

        # Performs the request and scraps the URLs
        res = r.get('explore/explore', params=payload)
        matches = res.json()['explore_vintage']['matches']

        # Iterates over every match
        for match in matches:
            # Gathers the wine-based data

            print(f'Scraping data from wine: {match["vintage"]["wine"]["name"]}')

            # Appends current match to the dictionary
            data['wines'].append(match)

            # Gathers the full-taste profile from current match
            res = r.get(f'wines/{match["vintage"]["wine"]["id"]}/tastes')
            tastes = res.json()

            # Replaces the taste profile
            data['wines'][-1]['vintage']['wine']['taste'] = tastes['tastes']

        # Opens the output .json file
        os.getcwd()
        #one file per page and per price range
        path=os.getcwd()+f'.\\resultsscrap\\{i}_{prix[loop][0]}_{prix[loop][1]}.json'
        with open(path, 'w') as f:
            # Dumps the data
            json.dump(data, f)
        
        # Closes the file
        f.close()

        
