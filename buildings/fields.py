import json
from collections import OrderedDict

from djongo.models import JSONField
from rest_framework import serializers

class GeoPointField(serializers.Field):
    def to_representation(self, value):
        # Ensure the value is in the correct format (a dict, not an OrderedDict)
        if isinstance(value, OrderedDict):
            value = json.loads(json.dumps(value))
        return {
            "type": value.get('type', 'Point'),
            "coordinates": value.get('coordinates', [])
        }

    def to_internal_value(self, data):
        # Validate and convert the incoming data back to the expected format
        if not isinstance(data, dict) or 'type' not in data or 'coordinates' not in data:
            raise serializers.ValidationError("Invalid format for GeoPoint.")
        return data

    class Meta:
        swagger_schema_fields = {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string"
                },
                "coordinates": {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            }
        }

class CustomJSONField(JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, OrderedDict):
            return value  # Or convert it to a regular dict: dict(value)
        return json.loads(value, cls=self.decoder)
