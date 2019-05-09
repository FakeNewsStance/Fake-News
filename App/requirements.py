from newsapi.newsapi_client import NewsApiClient
from newspaper import Article
import api_creds

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


class Summarizer:
    
    def __init__(self):
        pass
    
    def summarize_article(self,articles):
        summaries = []
        from gensim.summarization import summarize
        for article in articles:
            summary = summarize(article)
            summaries.append(summary)
        
        return summaries



from tweepy.streaming import StreamListener
from tweepy import Stream
import tweepy 
from tweepy.streaming import StreamListener
from rake_nltk import Rake
import json
import time
class TwitterStreamListener(StreamListener):
    def __init__(self):
        
        self.rake = Rake()
        self.newsArticles = NewsArticles()
        #self.stance = Main() 
    
    def get_score(self,tweet):
        try:
            p.set_options(p.OPT.URL, p.OPT.EMOJI)
            tweet=p.clean(tweet)
            self.rake.extract_keywords_from_text(tweet)
            keywords = self.rake.get_ranked_phrases()
            sep = ' OR '
            query = sep.join(keywords)
            print('QUERY : ',query)
            #articles = self.newsArticles.get_articles(query)
            #summarizer = Summarizer()
            #summaries = summarizer.summarize_article(articles)
            #score = self.stance.test(tweet,summaries)
            return score
        except:
            return 999
    
    def on_data(self, data):
        try: 
            tweet = json.loads(data)
            text = tweet['extended_tweet']['full_text']
            score = self.get_score(text)
            socketio.emit('stream_channel',
                      {'name':tweet['user']['name'],'data': text,'score': score, 'time': tweet[u'timestamp_ms']}, broadcast=True,
                      namespace='/demo_streaming')
            time.sleep(5)
        except: 
            pass 
    
    
    def on_error(self, status):
        print('Error status code', status)
        exit()