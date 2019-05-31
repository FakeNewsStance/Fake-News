import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['fakenews']
tweets = db['tweets']
articles = db['articles']
results = db['results']

total_tweets = tweets.count_documents({})
total_tweets_with_articles = articles.count_documents({})
total_tweets_with_score = results.count_documents({})
score_max = results.find().sort({score:-1}).limit(1)
score_min = results.find().sort({score:+1}).limit(1)

print('\nTotal Tweets fetched :',total_tweets)
print('Total tweets with articles :',total_tweets_with_articles)
print('Total tweets with score:',total_tweets_with_score)
print('Most credible tweet ',score_max)
print('Least credible tweet ',score_min)
