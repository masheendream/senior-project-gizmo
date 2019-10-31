import tweepy
import json
import sys

#It's not really a constant, but we'll pretend it is.
MAX_WORDS = 300

print("\n*************************************************")
print("*   Welcome to the scraper tool! ~Derek Lopez   *")
print("*************************************************\n")

#get the username from the command line arguments. Terminate if none is provided.
if len(sys.argv) < 2:
    print("No username provided. Terminating.\n")
    quit()
else:
    username = sys.argv[1]

#get the credentials for the twitter API from keys.json
with open('credentials.json') as json_creds:
    credentials = json.load(json_creds)

#create the tweepy API object
    auth = tweepy.OAuthHandler(credentials["keys"]["public"], credentials["keys"]["secret"])
    auth.set_access_token(credentials["tokens"]["public"], credentials["tokens"]["secret"])
    api = tweepy.API(auth)

#use the API to pull 100 tweets from the specified user
tweets = api.user_timeline(screen_name = username,count=100)

#create a class to hold our data
class WordList(object):
    username = ""
    wordCount = 0
    words = []

    def __init__(self, username, wordCount, words):
        self.username = username
        self.wordCount = wordCount
        self.words = words

#create an empty WordList object
wl = WordList(username, 0, [])

#populate the object with the first 300 words from the last 100 tweets
for tweet in tweets:
    wl.words.extend(tweet._json["text"].split()[:MAX_WORDS-wl.wordCount])
    wl.wordCount += len(tweet._json["text"].split()[:MAX_WORDS-wl.wordCount])
    if wl.wordCount > 299:
        break

if wl.wordCount < 300:
    print("\tWARNING: Unable to get 300 words from " + username + ". Could only pull " + str(wl.wordCount) + ". Saved to output_" + username + ".json\n")
else:
    print("300 words of " + username + " are now saved to output_" + username + ".json.\n")

with open('output_' + username + '.json', 'w') as outfile:
    json.dump(wl.__dict__, outfile)