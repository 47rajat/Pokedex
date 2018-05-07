# importing packages
from requests import exceptions
import argparse
import requests
import cv2
import os

# constructing argument parser and parsing argument
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True, help="search query to search Bing API for")
ap.add_argument("-o", "--output", required=True, help="path to output directory of images")
args = vars(ap.parse_args())

# setting parameters value for maximum number of results for a given search and
# group size for results, try later with max size of 1000 images
API_KEY = "INSERT YOUR API HERE"
MAX_RESULTS = 250
GROUP_SIZE = 50

# endpoint url
URL = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'

# building a list of exceptions
EXCEPTIONS = set([IOError, FileNotFoundError, exceptions.RequestException,
                exceptions.HTTPError, exceptions.ConnectionError, exceptions.Timeout])

# storing the search term in a conviniece variable
term = args['query']
headers = {'Ocp-Apim-Subscription-Key': API_KEY}
params = {'q': term, 'offset': 0, 'count': GROUP_SIZE}

# make search
print('[INFO] searching Bing API for "{}"'.format(term))
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

# grab the results from the search, including total number of estimated
# results
results = search.json()
estNumResults = min(results['totalEstimatedMatches'], MAX_RESULTS)
print('[INFO] {} total results for "{}"'.format(estNumResults, term))

# init total number of images downloaded thus far.
total = 0

# loop over estimated number of results in GROUP_SIZE group
for offset in range(0, estNumResults, GROUP_SIZE):
    # updating the parameter using current offset and 
    # then making search request.
    print('[INFO] making request for group {}-{} of {}....'.format(offset, offset+GROUP_SIZE, estNumResults))
    params['offset'] = offset
    search = requests.get(URL, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print('[INFO] saving images for group {}-{} of {}....'.format(offset, offset+GROUP_SIZE, estNumResults))

    # looping over the results
    for v in results['value']:
        # trying to download the image
        try:
            # making request to download images
            print('[INFO] fetching: {}'.format(v['contentUrl']))
            r = requests.get(v['contentUrl'], timeout=30)
            # build path to output image
            ext = v['contentUrl'][v['contentUrl'].rfind('.'):]
            p = os.path.sep.join([args['output'], '{}{}'.format(str(total).zfill(8), ext)])
            # write image to disk
            f = open(p, 'wb')
            f.write(r.content)
            f.close()

            # try to load the image from disk
            image = cv2.imread(p)
            # if image is `None` then it was not loaded properly and we will ignore
            # it
            if image is None:
                print('[INFO] deleting: {}'.format(p))
                os.remove(p)
                continue
            # update total counter
            total += 1
        # catching any erros while downloading images
        except Exception as e:
            # check if exception is present in out list of exceptions
            if type(e) in EXCEPTIONS:
                print('[INFO] skipping: {}'.format(v['contentUrl']))
                continue
    
