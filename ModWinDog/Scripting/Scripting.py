luaCycleLimit = 10000
luaMemoryLimit = (512 * 1024) # 512 KB
luaCrashMessage = f"Lua Error: Script has been forcefully terminated due to having exceeded the max cycle count limit ({luaCycleLimit})."

from lupa import LuaRuntime as NewLuaRuntime, LuaError, LuaSyntaxError

def luaAttributeFilter(obj, attr_name, is_setting):
	raise AttributeError("Access Denied.")

#LuaRuntime = NewLuaRuntime(max_memory=(16 * 1024**2), register_eval=False, register_builtins=False, attribute_filter=luaAttributeFilter)
#for key in LuaRuntime.globals():
#	if key not in ("error", "assert", "math", "type"):
#		del LuaRuntime.globals()[key]
#luaGlobalsCopy = dict(LuaRuntime.globals()) # should this manually handle nested stuff?
# this way to prevent overwriting of global fields is flawed since this doesn't protect concurrent scripts
# better to use the currently active solution of a dedicated instance for each new script running
#def luaFunctionRunner(userFunction:callable):
#	for key in luaGlobalsCopy:
#		LuaRuntime.globals()[key] = luaGlobalsCopy[key]
#	return userFunction()

# TODO make print behave the same as normal Lua, and expose a function for printing without newlines
def cLua(context, data=None) -> None:
	scriptText = (data.Body or (data.Quoted and data.Quoted.Body))
	if not scriptText:
		return SendMsg(context, {"Text": "You must provide some Lua code to execute."})
	luaRuntime = NewLuaRuntime(max_memory=luaMemoryLimit, register_eval=False, register_builtins=False, attribute_filter=luaAttributeFilter)
	luaRuntime.eval(f"""(function()
_windog = {{ stdout = "" }}
function print (text, endl) _windog.stdout = _windog.stdout .. text .. (endl ~= false and "\\n" or "") end
function luaCrashHandler () return error("{luaCrashMessage}") end
debug.sethook(luaCrashHandler, "", {luaCycleLimit})
end)()""")
	for key in luaRuntime.globals():
		if key not in ("error", "assert", "math", "string", "print", "_windog"):
			del luaRuntime.globals()[key]
	try:
		textOutput = ("[ʟᴜᴀ ꜱᴛᴅᴏᴜᴛ]\n\n" + luaRuntime.eval(f"""(function()
_windog.scriptout = (function()\n{scriptText}\nend)()
return _windog.stdout .. (_windog.scriptout or '')
end)()"""))
	except (LuaError, LuaSyntaxError) as error:
		Log(textOutput := str("Lua Error: " + error))
	SendMsg(context, {"TextPlain": textOutput})

RegisterModule(name="Scripting", group="Geek", summary="Tools for programming the bot and expanding its features.", endpoints={
	"Lua": CreateEndpoint(["lua"], summary="Execute a Lua snippet and get its output.", handler=cLua),
})

