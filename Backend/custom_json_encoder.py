from bson import ObjectId
from json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
       # return JSONEncoder.default(self, obj)
        return super().default(obj)