""" generate links """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from telegraph import upload_file

from userge import userge, Message, pool


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
    reply = "**All Links** :\n\n"
    for link in links:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        reqs = requests.get(link, headers=headers)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for l in set(soup.find_all('a')):
            a = l.get('href')
            if a:
                if a.startswith('http') or a.startswith('//'):
                    reply += f" 👉 `{a}`\n"
                else:
                    reply += f" 👉 `{''.join((urlparse(link).netloc, a))}`\n"
    await message.edit(reply, parse_mode="md")
