from peewee import *

Db = SqliteDatabase("Database.sqlite")

class BaseModel(Model):
	class Meta:
		database = Db

class Entity(BaseModel):
	id = CharField(null=True)
	id_hash = CharField()
	#settings = ForeignKeyField(EntitySettings, backref="entity")
	#language = CharField(null=True)

class User(Entity):
	pass

class Room(Entity):
	pass

Db.create_tables([User, Room], safe=True)

