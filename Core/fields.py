from bson import ObjectId as BsonObjectId
from django.db import models
from rest_framework import serializers
import bson

class MongoObjectIdField(models.Field):
    def db_type(self, connection):
        return 'ObjectId'

    def to_python(self, value):
        if not value:
            return value
        try:
            return str(BsonObjectId(value))  # Convert ObjectId to string for Python
        except bson.errors.InvalidId:
            raise ValueError("Invalid ObjectId")

    def get_prep_value(self, value):
        if value is None or value == '':
            return BsonObjectId()  # Generate new ObjectId
        return str(value)  # convert ObjectId to string

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)  # Convert value from database to Python

    def to_representation(self, value):
        # Method used by DR
        return str(value)
