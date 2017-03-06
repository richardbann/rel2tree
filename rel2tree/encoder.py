from collections import OrderedDict
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '_json') and callable(obj._json):
            return obj._json()
        if hasattr(obj, '_json_fields'):
            json_fields = obj._json_fields
            return OrderedDict((k[0], getattr(obj, k[1])) for k in json_fields)
        return super(JSONEncoder, self).default(obj)
