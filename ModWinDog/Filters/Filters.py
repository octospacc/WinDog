# ==================================== #
#  WinDog multi-purpose chatbot        #
#  Licensed under AGPLv3 by OctoSpacc  #
# ==================================== #

def cFilters(context:EventContext, data:InputMessageData):
	language = data.user.settings.language
	if not check_room_admin(data.user):
		return send_status(context, 403, language)
	# action:     create, delete, toggle <chatid, name/filterid>
	# * (input)   handle, ignore         <...>
	# * (output)  setscript              <..., script> 
	# * (output)  insert, remove         <..., groupid, message>
	#arguments = data.command.parse_arguments(4)
	if not (action := data.command.arguments.action) or (action not in ["list", "create", "delete"]):
		return send_status_400(context, language)
	[room_id, filter_id, command_data] = ((None,) * 3)
	for token in data.command.tokens[2:]:
		if (not room_id) and (':' in token):
			room_id = token
		elif (not filter_id):
			filter_id = token
		elif (not command_data):
			command_data = token
	if not room_id:
		room_id = data.room.id
	if (action in ["delete"]) and (not filter_id):
		return send_status_400(context, language)
	match action:
		case "list":
			filters_list = ""
			for filter in Filter.select().where(Filter.owner == room_id).namedtuples():
				filters_list += f"\n* <code>{filter.id}</code> — {filter.name or '[?]'}"
			if filters_list:
				return send_message(context, {"text_html": f"Filters for room <code>{room_id}</code>:{filters_list}"})
			else:
				return send_status(context, 404, language, f"No filters found for the room <code>{room_id}</code>.", summary=False)
		case "create":
			...
			# TODO error message on name constraint violation
			# TODO filter name validation (no spaces or special symbols, no only numbers)
			if filter_id and (len(Filter.select().where((Filter.owner == room_id) & (Filter.name == filter_id)).tuples()) > 0):
				return
			else:
				filter_id = Filter.create(name=filter_id, owner=room_id)
				return send_status(context, 201, language, f"Filter with id <code>{filter_id}</code> in room <code>{room_id}</code> created successfully.", summary=False)
		case "delete":
			#try:
			Filter.delete().where((Filter.owner == room_id) & ((Filter.id == filter_id) | (Filter.name == filter_id))).execute()
			return send_status(context, 200, language)
			#return send_status(context, 200, language, f"Filter <code>{filter_id}</code> for room <code>{room_id}</code> deleted successfully.", summary=False)
			#except Exception:
			#	... # TODO error and success message, actually check for if the item to delete existed
		case "insert": # TODO
			#output = Filter.select().where((Filter.owner == room_id) & ((Filter.id == filter_id) | (Filter.name == filter_id))).namedtuples().get().output
			Filter.update(output=data.quoted).where((Filter.owner == room_id) & ((Filter.id == filter_id) | (Filter.name == filter_id))).execute()
		case "remove":
			...
		case "handle":
			...
		case "ignore":
			...

register_module(name="Filters", endpoints=[
	SafeNamespace(names=["filters"], handler=cFilters, quoted=False, arguments={
		"action": True,
	}),
])

