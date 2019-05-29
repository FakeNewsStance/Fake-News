import json 
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from tweepy.streaming import StreamListener
from tweepy import Stream
import tweepy 
from newsapi.newsapi_client import NewsApiClient
from newspaper import Article
import tweepy
from tweepy.streaming import StreamListener
import json
import csv
import api_creds
import preprocessor
from rake_nltk import Rake
import time
import numpy as np
import pandas as pd
#from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder     
#import keras
import warnings
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
        warnings.filterwarnings(action='ignore', category=DeprecationWarning)
        from keras.preprocessing.sequence import pad_sequences
        sequences1 = self.tokenizer.texts_to_sequences([tweet])
        test1 = pad_sequences(sequences1, maxlen=self.MAX_SEQUENCE_LENGTH) 
        credibility_score=0
        print('Mic Check')
        print('len of Articles : ',len(articles))
        
        for article in articles:
                sequences2 = self.tokenizer.texts_to_sequences([article])
                test2 = pad_sequences(sequences2, maxlen=self.MAX_SEQUENCE_LENGTH)
                y_pred = self.model.predict([test1, test2])
                y_pred[y_pred > 0.5] = 1
                y_pred[y_pred < 0.5] = 0
                y_pred_num = np.argmax(y_pred)
                stance = self.labelencoder_y.inverse_transform(y_pred_num)
                if stance == "agree":
                    credibility_score+=1
                elif stance == "disagree":
                    credibility_score-=1
                elif stance == "discuss":
                    credibility_score+=0.25
                else:
                    credibility_score+=0
                print('\n\nY pred:',stance)
        print('\n\n Credibility Score:',(credibility_score/len(articles)*100))
        return credibility_score



class TwitterStreamListener(StreamListener):

    def __init__(self):
        self.rake = Rake()
        self.newsArticles = NewsArticles()
        #self.stance = Model() 


    def get_score(self,tweet,data):
        try:
#            preprocessor.set_options(preprocessor.OPT.URL, preprocessor.OPT.EMOJI)
#            tweet=preprocessor.clean(tweet)

            score = 777
            self.rake.extract_keywords_from_text(tweet)
            keywords = self.rake.get_ranked_phrases()
            sep = ' OR '
            query = sep.join(keywords)
            print('\n\nQuery:',query)
            
            articles = self.newsArticles.get_articles(query)
            print('Number of Articles Found: ',len(articles))

            db.addTweet(data)
            db.addArticles(data["id_str"],articles)

            if len(articles) == 0:
                return 0

            #summarizer = Summarizer()
            #summaries = summarizer.summarize_article(articles)
            #score = self.stance.test(tweet,summaries)

            db.addScore(data['id_str'],score)
            return score
        
        except Exception as e:
            print('Error:'+e)
            return 0


    def on_data(self, data):
        try: 
            tweet = json.loads(data)
            text = tweet['extended_tweet']['full_text']
            score = self.get_score(text,tweet)
            print(score)
            if score != 0:
                print('Going to web page')
                socketio.emit('stream_channel',
                          {'name':tweet['user']['name'],'data': text,'score': score, 'time': tweet[u'timestamp_ms']}, broadcast=True,
                          namespace='/demo_streaming')
            else:
                print('Not Going to web page')
        except:
            pass


    def on_error(self, status):
        print('Error status code', status)
        exit()


############## EXECUTION STARTS FROM HERE ######################

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()


def background_thread():
    """send server generted events to clients."""
    stream = Stream(auth, StreamListener,tweet_mode = 'extended')
    keywords_list = ['Modi','Rahul Gandhi','Congress','BJP','Priyanka Gandhi','#LSPolls','#Elections2019']
    stream.filter(track=keywords_list, languages=["en"])


app = Flask(__name__)
#model = keras.models.load_model('model')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
db = Database()

cred = {
            "access_key": api_creds.access_key, 
            "access_secret": api_creds.access_secret, 
            "consumer_key": api_creds.consumer_key, 
            "consumer_secret": api_creds.consumer_secret
        }
auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
auth.set_access_token(cred['access_key'], cred['access_secret'])


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')

@app.route('/mc')
def manual_checking():
    return render_template('man_check.html')


@app.route('/handle_man_check',methods=['POST'])
def handle_man_check():
    global StreamListener
    input_text = request.form['inp_txt']
    score = StreamListener.get_score(input_text)
    return input_text+'<br><br>Score:'+str(score)

StreamListener = TwitterStreamListener()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='18.216.146.53',port=1234)
