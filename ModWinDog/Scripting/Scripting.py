# ================================== #
# WinDog multi-purpose chatbot       #
# Licensed under AGPLv3 by OctoSpacc #
# ================================== #

""" # windog config start # """

LuaCycleLimit = 10000
LuaMemoryLimit = (512 * 1024) # 512 KB
LuaCrashMessage = f"Script has been forcefully terminated due to having exceeded the max cycle count limit ({LuaCycleLimit})."

# see <http://lua-users.org/wiki/SandBoxes> for a summary of certainly safe objects (outdated though)
LuaGlobalsWhitelist = ["_windog", "_VERSION", "print", "error", "assert", "tonumber", "tostring", "math", "string", "table"]
LuaTablesWhitelist = {"os": ["clock", "date", "difftime", "time"]}

""" # end windog config # """

# always specify a Lua version; using the default latest is risky due to possible new APIs and using JIT is vulnerable
from lupa.lua54 import LuaRuntime as NewLuaRuntime, LuaError, LuaSyntaxError

# I'm not sure this is actually needed, but better safe than sorry
def luaAttributeFilter(obj, attr_name, is_setting):
	raise AttributeError("Access Denied.")

# TODO make print behave the same as normal Lua, and expose a function for printing without newlines
def cLua(context:EventContext, data:InputMessageData) -> None:
	# TODO update quoted api getting
	scriptText = (data.command.body or (data.Quoted and data.Quoted.Body))
	if not scriptText:
		return SendMessage(context, {"Text": "You must provide some Lua code to execute."})
	luaRuntime = NewLuaRuntime(max_memory=LuaMemoryLimit, register_eval=False, register_builtins=False, attribute_filter=luaAttributeFilter)
	luaRuntime.eval(f"""(function()
_windog = {{ stdout = "" }}
function print (text, endl) _windog.stdout = _windog.stdout .. tostring(text) .. (endl ~= false and "\\n" or "") end
function luaCrashHandler () return error("{LuaCrashMessage}") end
debug.sethook(luaCrashHandler, "", {LuaCycleLimit})
end)()""")
	# delete unsafe objects
	for key in luaRuntime.globals():
		if key in LuaTablesWhitelist:
			for tabKey in luaRuntime.globals()[key]:
				if tabKey not in LuaTablesWhitelist[key]:
					del luaRuntime.globals()[key][tabKey]
		elif key not in LuaGlobalsWhitelist:
			del luaRuntime.globals()[key]
	try:
		textOutput = ("[ʟᴜᴀ ꜱᴛᴅᴏᴜᴛ]\n\n" + luaRuntime.eval(f"""(function()
_windog.scriptout = (function()\n{scriptText}\nend)()
return _windog.stdout .. (_windog.scriptout or '')
end)()"""))
	except (LuaError, LuaSyntaxError) as error:
		Log(textOutput := ("Lua Error: " + str(error)))
	SendMessage(context, {"TextPlain": textOutput})

RegisterModule(name="Scripting", group="Geek", summary="Tools for programming the bot and expanding its features.", endpoints={
	"Lua": CreateEndpoint(["lua"], summary="Execute a Lua snippet and get its output.", handler=cLua),
})

