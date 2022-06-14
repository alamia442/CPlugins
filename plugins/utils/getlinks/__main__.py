""" generate links """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import requests
from bs4 import BeautifulSoup

from userge import userge, Message, pool
from userge.utils import humanbytes


@userge.on_cmd("getlinks", about={
    'header': "Links Generator"})
async def get_links(message: Message):
    text = message.input_or_reply_str
    if not text:
        await message.err("input not found!")
        return
    await message.edit("`Processing...`")
    links = re.findall(r'\bhttps?://.*\.\S+', text)
    if not links:
        await message.err("No links found!")
        return
    reply = "<b>All Links</b> :\n\n"
    reqs = requests.get(links)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    for link in soup.find_all('a'):
        a = link.get('href')
        if a.startswith('http'):
            reply += f" 👉 `{a}`\n"
        else:
            reply += f" 👉 `{''.join((links, a))}`\n"
    await message.edit(reply, parse_mode="md")
