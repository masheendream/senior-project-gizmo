import tweepy
import json
import sys
import csv 

#create a class to hold our data
class WordList(object):
    username = ""
    wordCount = 0
    words = []

    def __init__(self, username, wordCount, words):
        self.username = username
        self.wordCount = wordCount
        self.words = words

def pull_to_csv(username):
    #It's not really a constant, but we'll pretend it is.
    MAX_WORDS = 2400

    #get the credentials for the twitter API from keys.json
    with open('credentials.json') as json_creds:
        credentials = json.load(json_creds)
        #create the tweepy API object
        auth = tweepy.OAuthHandler(credentials["keys"]["public"], credentials["keys"]["secret"])
        auth.set_access_token(credentials["tokens"]["public"], credentials["tokens"]["secret"])
        api = tweepy.API(auth)
    
    #create an empty WordList object
    wl = WordList(username, 0, [])
    #use the API to pull 100 tweets from the specified user
    tweets = api.user_timeline(screen_name = username,count=100)
    #populate the object with the first 300 words from the last 100 tweets
    for tweet in tweets:
        wl.words.extend(tweet._json["text"].split()[:MAX_WORDS-wl.wordCount])
        wl.wordCount += len(tweet._json["text"].split()[:MAX_WORDS-wl.wordCount])

    print(str(wl.wordCount) + " words from " + username + " are now saved to test_user.csv\n")

    with open('test_user.csv', 'w',newline='') as f:
        fwriter = csv.writer(f)
        fwriter.writerow('w')
        fwriter.writerow([wl.words])