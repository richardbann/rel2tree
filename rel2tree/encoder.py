from collections import OrderedDict
import json
import decimal


class JSONAttrMixin(object):
    def default(self, obj):
        if hasattr(obj, '_json') and callable(obj._json):
            return obj._json()
        if hasattr(obj, '_json_fields'):
            json_fields = obj._json_fields
            return OrderedDict((k[0], getattr(obj, k[1])) for k in json_fields)
        return super(JSONAttrMixin, self).default(obj)


class DecimalEncodeMixin(object):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return super(DecimalEncodeMixin, self).default(obj)


class JSONEncoder(JSONAttrMixin, json.JSONEncoder):
    pass
