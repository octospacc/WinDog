# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

from peewee import *
from LibWinDog.Types import *

Db = SqliteDatabase("./Data/Database.sqlite")

class BaseModel(Model):
	class Meta:
		database = Db

class EntitySettings(BaseModel):
	language = CharField(null=True)

class Entity(BaseModel):
	id = CharField(null=True)
	id_hash = CharField()
	settings = ForeignKeyField(EntitySettings, backref="entity", null=True)

class User(Entity):
	pass

class Room(Entity):
	pass

Db.create_tables([EntitySettings, User, Room], safe=True)

class UserSettingsData():
	def __new__(cls, user_id:str) -> SafeNamespace|None:
		try:
			return SafeNamespace(**EntitySettings.select().join(User).where(User.id == user_id).dicts().get())
		except EntitySettings.DoesNotExist:
			return None

