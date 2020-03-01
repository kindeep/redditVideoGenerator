from tinydb import TinyDB, Query
db = TinyDB('log/db.json')
table = db.table('created_videos')
table.insert({'url': 'www.example.com', 'id': '00'})