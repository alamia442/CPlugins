""" Upload image to ImgBB.com """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import requests
from pathlib import Path
import json

from userge import userge, Message, config

@userge.on_cmd("ibb", about={'header': "Upload image to ImgBB.com"})
async def _upibb(message: Message):
    await message.edit("`Processing ...`")
    path_ = message.filtered_input_str
    if not path_:
        await message.err("Input not foud!")
        return
    try:
        string = Path(path_)
    except IndexError:
        await message.err("wrong syntax")
    else:
        await message.edit("`Uploading image to ImgBB ...`")
        with message.cancel_callback():
            params = {'key': '09fa3aa9bb2d2580398572e1f450ff53'}
            url = 'https://api.imgbb.com/1/upload'
            files = {'image': open(string, 'rb')}
            response = requests.post(url, params=params, files=files)
            imgurl = response.json()['data']['url']
            await message.edit(imgurl, disable_web_page_preview=True)
