import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017/")
cursor = client.fakenews.results.changes([
    {'$match': {
        'operationType': {'$in': ['insert', 'replace']}
    }},
    {'$match': {
        'newDocument.n': {'$gte': 1}
    }}
])

# Loops forever.
for change in cursor:
    print(change['newDocument'])
