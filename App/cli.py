import json 
import time
from tweepy.streaming import StreamListener
from tweepy import Stream
import tweepy 
from newsapi.newsapi_client import NewsApiClient
from newspaper import Article
import tweepy
from tweepy.streaming import StreamListener
import api_creds
from rake_nltk import Rake
import time
import numpy as np
import pandas as pd
from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder     
import keras
import warnings
import preprocessor
from requirements import Summarizer,NewsArticles
from Database import Database

class Model:
    
    def __init__(self):
       
        
        self.MAX_SEQUENCE_LENGTH = 300
        self.MAX_NUM_WORDS = 60000
        self.EMBEDDING_DIM = 300
        self.VALIDATION_SPLIT = 0.2
        
        stances = pd.read_csv("train_stances.csv")
        bodies = pd.read_csv("train_bodies.csv")
        
        dataset = pd.merge(stances, bodies)
        
        dataset = dataset.drop(['BodyID'], axis=1)
        
        cols = dataset.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        dataset = dataset[cols]
        
        y = dataset['Stance']
        y = np.array(y)
        
        
        self.labelencoder_y = LabelEncoder()
        y = self.labelencoder_y.fit_transform(y)
        
        
        
        self.tokenizer = Tokenizer(nb_words=self.MAX_NUM_WORDS)
        self.tokenizer.fit_on_texts(dataset['Headline']+dataset['articleBody'])
        
        self.model = keras.models.load_model('model')
    

    def test(self,tweet,articles):
        try:
            warnings.filterwarnings(action='ignore', category=DeprecationWarning)
            from keras.preprocessing.sequence import pad_sequences
            sequences1 = self.tokenizer.texts_to_sequences([tweet])
            test1 = pad_sequences(sequences1, maxlen=self.MAX_SEQUENCE_LENGTH)
            credibility_score=0
            for article in articles:
                    sequences2 = self.tokenizer.texts_to_sequences([article])
                    test2 = pad_sequences(sequences2, maxlen=self.MAX_SEQUENCE_LENGTH)
                    y_pred = self.model.predict([test1, test2])
                    y_pred[y_pred > 0.5] = 1
                    y_pred[y_pred < 0.5] = 0
                    y_pred_num = np.argmax(y_pred)
                    stance = self.labelencoder_y.inverse_transform([y_pred_num])
                    if stance == "agree":
                        credibility_score+=1
                    elif stance == "disagree":
                        credibility_score-=1
                    elif stance == "discuss":
                        credibility_score+=0.25
                    else:
                        credibility_score+=0
            return (credibility_score/len(articles)*100)
        except Exception as e:
            print('Error in model :',e)
            return 777


class TwitterStreamListener(StreamListener):

    def __init__(self):
        self.rake = Rake()
        self.newsArticles = NewsArticles()
        self.stance = Model() 


    def get_score(self,tweet,data):
        try:
            preprocessor.set_options(preprocessor.OPT.URL, preprocessor.OPT.EMOJI)
            tweet=preprocessor.clean(tweet)

            score = 777
            self.rake.extract_keywords_from_text(tweet)
            keywords = self.rake.get_ranked_phrases()
            sep = ' OR '
            query = sep.join(keywords)
            print('\nQuery >>> ',query)
            
            articles = self.newsArticles.get_articles(query)
            print('\nNumber of Articles Found >>> ',len(articles))

            db.addTweet(data)

            if len(articles) == 0:
                return 777
			
			db.addArticles(data["id_str"],articles)

            summarizer = Summarizer()
            summaries = summarizer.summarize_article(articles)
            score = self.stance.test(tweet,summaries)

            db.addScore(data['id_str'],score)
            return score
        
        except Exception as e:
            print('Error >>> '+e)
            return 777


    def on_data(self, data):
        try: 
            tweet = json.loads(data)
            text = tweet['extended_tweet']['full_text']
            if text != '':
                print('\n\n\n--------------------------------------------------')
                print('Tweet >>> ',text)
                score = self.get_score(text,tweet)
                if score != 777:
                    print('\nCredibility Score >>> ',score)
                else:
                    print('\nNo Score available')
        except:
            pass


    def on_error(self, status):
        print('Error status code', status)
        exit()


########### EXECUTION STARTS HERE ################

model = keras.models.load_model('model')
db = Database()

cred = {
            "access_key": api_creds.access_key, 
            "access_secret": api_creds.access_secret, 
            "consumer_key": api_creds.consumer_key, 
            "consumer_secret": api_creds.consumer_secret
        }
auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
auth.set_access_token(cred['access_key'], cred['access_secret'])

StreamListener = TwitterStreamListener()
stream = Stream(auth, StreamListener,tweet_mode = 'extended')
keywords_list = ['Modi','Rahul Gandhi','Congress','BJP','Priyanka Gandhi','#LSPolls','#Elections2019']
stream.filter(track=keywords_list, languages=["en"])
