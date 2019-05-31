import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['fakenews']
tweets = db['tweets']
articles = db['articles']
results = db['results']

try:
    with db.results.watch(
            [{'$match': {'operationType': 'insert'}}]) as stream:
        for insert_change in stream:
            print(insert_change)
except pymongo.errors.PyMongoError:
    # The ChangeStream encountered an unrecoverable error or the
    # resume attempt failed to recreate the cursor.
    print('Error')