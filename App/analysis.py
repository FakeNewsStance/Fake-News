import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['fakenews']
tweets = db['tweets']
articles = db['articles']
results = db['results']

total_tweets = tweets.count_documents({})
total_tweets_with_articles = articles.count_documents({})
total_tweets_with_score = results.count_documents({})
score_min = results.find_one(sort=[('score',1)])['tweet_id']
score_max = results.find_one(sort=[('score',-1)])['tweet_id']
tweet_max = tweets.find_one({'tweet_id':score_max})
tweet_min = tweets.find_one({'tweet_id':score_min})

print('\nTotal Tweets fetched :',total_tweets)
print('Total tweets with articles :',total_tweets_with_articles)
print('Total tweets with score:',total_tweets_with_score)
print('Most credible tweet ',tweet_max)
print('Least credible tweet ',tweet_min)