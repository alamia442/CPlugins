""" generate links """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.
import re

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
    for link in links:
        reqs = requests.get(link)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for l in soup.find_all('a'):
            a = l.get('href')
            if a and '\/\/' in a:
                reply += f" 👉 `{a}`\n"
            else:
                reply += f" 👉 `{''.join((link, a))}`\n"
    await message.edit(reply, parse_mode="md")
