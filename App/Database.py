class Database:

	def __init__(self):
		import pymongo
		client = pymongo.MongoClient("mongodb://localhost:27017/")
		db = client["fakenews"]
		self.col_tweets = db["tweets"]
		self.col_articles = db["articles"]
		self.col_results = db["results"]

	def addTweet(self,tweet):
		self.col_tweets.insert_one(tweet)


	def addArticles(self,tweet_id,articles):
		self.col_articles.insert_one({'tweet_id':tweet_id,'articles':articles,'count':len(articles)})


	def addScore(self,tweet_id,score):
		self.col_results.insert_one({'tweet_id':tweet_id,'score':score})

		