import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['fakenews']
tweets = db['tweets']
articles = db['articles']
results = db['results']

total_tweets = tweets.count_documents({})
total_tweets_with_articles = articles.count_documents({})
total_tweets_with_score = results.count_documents({})
score_min = results.find_one(sort=[('score',1)])
score_max = results.find_one(sort=[('score',-1)])
tweet_max = tweets.find_one({'id_str':score_max['tweet_id']})
tweet_min = tweets.find_one({'id_str':score_min['tweet_id']})
num_articles_score_max = articles.find_one({'tweet_id':score_max['tweet_id']})['count']
num_articles_score_min = articles.find_one({'tweet_id':score_min['tweet_id']})['count']


print('\nTotal Tweets fetched :',total_tweets)
print('Total tweets with articles :',total_tweets_with_articles)
print('Total tweets with score:',total_tweets_with_score)
print('\n-----Most credible tweet-----\n',tweet_max['text'],'\nScore :',score_max['score'])
print('Articles for this tweet :',num_articles_score_max)

print('\n------Least credible tweet-----\n',tweet_min['text'],'\nScore :',score_min['score'])
print('Articles for this tweet :',num_articles_score_min)
