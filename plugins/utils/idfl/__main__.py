import asyncio
import os

from userge import userge, Message, config
from . import idflbot as ib

@userge.on_cmd("idfl", about={'header': "Get Latest post and thread forum IDFL"})
async def _idfl_latest(message: Message):
	await message.edit("`Processing ...`")
	try:
		ibot = ib.IDFLbot(os.environ["IDFL_EMAIL"], os.environ["IDFL_PASS"])
		ibot.login()
		threads, posts = ibot.latest_post()
	except Exception as e:
		await message.edit(e)

	reply = "**Latest Thread** :\n\n"
	for x in threads:
		reply += f" 👉 `{x}`\n"
	reply += "\n**Latest Posts** :\n\n"
	for y in posts:
		reply += f" 👉 `{y}`\n"
	await message.edit_or_send_as_file(text=reply,
                                       parse_mode='md',
                                       filename="idfl-forum.txt",
                                       caption="**Latest** :\n")
