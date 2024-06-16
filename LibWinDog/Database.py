from peewee import *

Db = SqliteDatabase("Database.sqlite")

class BaseModel(Model):
	class Meta:
		database = Db

