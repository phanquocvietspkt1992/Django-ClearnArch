from django.conf import settings

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        from pymongo import MongoClient
        _client = MongoClient(settings.MONGODB['CONNECTION_STRING'])
        _db = _client[settings.MONGODB['DATABASE_NAME']]
    return _db
