from __future__ import print_function

from TwitterAPI import TwitterAPI
from pygments import highlight, lexers, formatters
import json

access_token_key = "118197143-lxLFvzNTbq0YwygedKusXeWQwLCk4KaE8DL0mACl"
access_token_secret = "cnwvXILlGw0R6o31EKaoJ7s2gQRRJ0cVVh5SYn7dtN43o"

api_key = "n7dLWfUSdZeLiXjFf24d8djP7"
api_secret = "TIBmvnQdtwA1rQ5KXmmfXO4kAKapE6Na5UQR2msShTp90Bca4S"

_debug = 0


api = TwitterAPI(api_key, api_secret, access_token_key, access_token_secret)

topic = "DemsInPhilly"

def prettify_json(json_string):
    formatted_json = json.dumps(json_string, sort_keys=True, indent=4)

    colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
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


import sys
import twitter

if __name__ == '__main__':
    results = retrieve_tweets(topic=topic)
    out = open('captured-tweets.txt', 'ab')
    # The tweet is stored with key 'text',
    i = 0
    for result in results:

        prettify_json(result)

        # Filter to english tweets
        if ('lang' in result and result['lang'] == 'en') or ('user' in result and result['user']['lang'] == 'en'):
            out.write((result['text'] + "\n").encode('utf-8'))
            i += 1

        # Defaulting to capturing 5000, this takes a long time...
        if i == 5000:
            exit()

