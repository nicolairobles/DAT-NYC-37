from __future__ import print_function

import sys
import twitter
from TwitterAPI import TwitterAPI
from pygments import highlight, lexers, formatters
import json

##################################
# Helper functions
##################################

# A simple function to output Twitter's API JSON in a clean, readable format
def prettify_json(json_string):
    formatted_json = json.dumps(json_string, sort_keys=True, indent=4)

    colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


# Send an API request to Twitter to get a list of tweets related to a topic
def retrieve_tweets(topic,
                    url="https://stream.twitter.com/1/statuses/filter.json",
                    method="GET", ):
    """
    Params:
    topic - must be in this format "#topic" or '@handle"
    Returns
    """
    response = api.request('statuses/filter', {'track': topic})

    if response.status_code != 200:
        raise ValueError("Unable to retrieve tweets, please check your API credentials")

    for x in response:
        try:
            yield x
        except UnicodeError as unicode_error:
            continue


##################################
# Execution starts here
##################################

# 1. Define our API credentials
access_token_key = "118197143-lxLFvzNTbq0YwygedKusXeWQwLCk4KaE8DL0mACl"
access_token_secret = "cnwvXILlGw0R6o31EKaoJ7s2gQRRJ0cVVh5SYn7dtN43o"

api_key = "n7dLWfUSdZeLiXjFf24d8djP7"
api_secret = "TIBmvnQdtwA1rQ5KXmmfXO4kAKapE6Na5UQR2msShTp90Bca4S"


# 2. Initialize our connection to Twitter with our credentials
api = TwitterAPI(api_key, api_secret, access_token_key, access_token_secret)


# 3. Read in our command-line arguments
# For instance, if we ran `python capture_tweets.py datascience`, then `sys.argv[1]` would be the string "datascience"
try:
    topic = sys.argv[1]
except:
    print("Please include a topic to listen for (usage: `python capture_tweets.py datascience`)")
    sys.exit(1)


# 4. Call our API handler
results = retrieve_tweets(topic=topic)


# 5. We'll write the results of our API "scrape" to a new file:
out = open('captured-tweets.txt', 'ab')


# 6. Iterate through each result we get from Twitter:
i = 0
for result in results:
    # Pretty print the JSON to the console
    prettify_json(result)

    ######
    # TODO: Rather than output the entire JSON object, just print the section of JSON we're interested in
    ######

    # Filter to english tweets
    if ('lang' in result and result['lang'] == 'en') or ('user' in result and result['user']['lang'] == 'en'):
        # The tweet is stored with key 'text', we'll write that to our file...
        out.write((result['text'] + "\n").encode('utf-8'))
        i += 1

    # Defaulting to capturing 5000 tweets, this takes a long time...
    if i == 5000:
        exit()
