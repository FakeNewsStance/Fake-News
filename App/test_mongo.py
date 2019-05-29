from pymongo import Connection
import time

db = Connection().my_db
coll = db.my_collection
cursor = coll.find(tailable=True)
while cursor.alive:
    try:
        doc = cursor.next()
        print doc
    except StopIteration:
        time.sleep(1)