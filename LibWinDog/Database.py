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
	#country = ...
	#timezone = ...

class Entity(BaseModel):
	id = CharField(null=True)
	id_hash = CharField()
	settings = ForeignKeyField(EntitySettings, backref="entity", null=True)

class File(BaseModel):
	path = CharField()
	content = BlobField()
	owner = ForeignKeyField(Entity, backref="files")
	class Meta:
		indexes = (
			(('path', 'owner'), True),
		)

#class BaseFilter(BaseModel):
#	name = CharField(null=True)
#	owner = ForeignKeyField(Entity, backref="filters")

#class ScriptFilter(BaseFilter):
#	script = TextField()

#class StaticFilter(BaseFilter):
#	response = TextField()

class Filter(BaseModel):
	name = CharField(null=True)
	trigger = CharField(null=True)
	output = CharField(null=True)
	owner = ForeignKeyField(Entity, backref="filters")

class Room(Entity):
	pass

UserToRoomDeferred = DeferredThroughModel()
FilterToRoomDeferred = DeferredThroughModel()

class User(Entity):
	rooms = ManyToManyField(Room, backref="users", through_model=UserToRoomDeferred)

class UserToRoom(BaseModel):
	user = ForeignKeyField(User, backref="room_links")
	room = ForeignKeyField(Room, backref="user_links")

class FilterToRoom(BaseModel):
	filter = ForeignKeyField(Filter, backref="room_links")
	room = ForeignKeyField(Room, backref="filter_links")

UserToRoomDeferred.set_model(UserToRoom)
FilterToRoomDeferred.set_model(FilterToRoom)

Db.create_tables([
	EntitySettings, File, Filter,
	User, Room,
	FilterToRoom, UserToRoom,
], safe=True)

class UserSettingsData():
	def __new__(cls, user_id:str=None) -> SafeNamespace:
		settings = None
		try:
			settings = EntitySettings.select().join(User).where(User.id == user_id).dicts().get()
		except EntitySettings.DoesNotExist:
			pass
		return SafeNamespace(**(settings or {}), _exists=bool(settings))

