from newsapi import NewsApiClient
from newspaper import Article
import tweepy
from tweepy.streaming import StreamListener
import json
import csv
import api_creds
from rake_nltk import Rake
from summarizer import Summarizer
from stance_model import Main
class StoreTweets:

    def __init__(self):
        pass

    def store(self,data):
        with open('tweets.csv', 'a', newline='',encoding="utf-8") as csvfile:
            fieldnames = list(data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)

        
class TwitterStreamListener(StreamListener):

    def __init__(self):
        self.storeTweets = StoreTweets()
        self.rake = Rake()
        self.newsArticles = NewsArticles()
        self.stance = Main()
        
    def on_data(self,data):
        try:
            data = json.loads(data)
#            self.storeTweets.store(data)
            self.rake.extract_keywords_from_text(data['text'])
            keywords = self.rake.get_ranked_phrases()
            
            print(keywords)
            sep = ' OR '
            query = sep.join(keywords)
            print(query)
            articles = self.newsArticles.get_articles(query)
            print(len(articles))
            summarizer = Summarizer()
            summaries = summarizer.summarize_article(articles)
            main = Main()
            main.test(data['text'],summaries)
        except Exception as e:
            print(e)
        return True
    
    def on_error(self,status):
        print(status)


class TwitterAuth:
    def __init__(self):
        consumer_key = api_creds.consumer_key
        consumer_secret = api_creds.consumer_secret
        access_key = api_creds.access_key
        access_secret = api_creds.access_secret
        auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
        auth.set_access_token(access_key,access_secret)
        self.api = tweepy.API(auth)


class NewsArticles:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=api_creds.news_api_key)
        
    def get_urls(self,query):
        all_articles = self.newsapi.get_everything(q=query,
                                      language='en',
                                      sort_by='relevancy',page=1)
        urls = []
        for article in all_articles['articles']:
            urls.append(article['url'])

        return urls

    def get_articles(self,query):
        urls = self.get_urls(query)
        articles = []
        for url in urls[:10]:
            try:
                fetched_article = Article(url)
                fetched_article.download()
                fetched_article.parse()
                articles.append(fetched_article.text)
            except:
                pass
        return articles


keywords_list = ['Modi','Rahul Gandhi','Congress','BJP','Priyanka Gandhi','#LSPolls','#Elections2019']
listener = TwitterStreamListener()
twitterAuth = TwitterAuth()
api = twitterAuth.api
stream = tweepy.Stream(api.auth,listener)
stream.filter(track=keywords_list,languages=["en"])


"""
class TweetFetcher:
    def __init__(self):
        twitterAuth = TwitterAuth()
        self.api = twitterAuth.api

    def get_tweets(self):
        tweets = self.api.search(q="#LSPolls")
        f = open('tp.txt','w')
        for i in tweets:
            f.write(i.text)
        f.close()
"""
