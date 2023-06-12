""" generate screenshot """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import requests
import glob
import asyncio
from pathlib import Path

from userge import userge, Message
from userge.utils.exceptions import ProcessCanceled
from userge.utils import is_url
from userge.utils.tools import runcmd
from ...misc import download

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("ss", about={
    'header': "Screen Shot Generator",
    'usage': "{tr}ss [Path or URL or reply to telegram media]",
    'examples': "{tr}ss https://domain.com/file.mkv | testing file.mkv"},
    check_downpath=True)
async def ss_gen(message: Message):
    """ download from tg and url """
    vid_loc = ''
    resource = ''
    dl_loc = ''
    d_in = ''
    ss_c = 3
    ss_r = 5
    should_clean = False
    await message.edit("Checking you Input . . .")
    
    if message.input_str:
        if ' ' in message.input_str:
            ss_c, vid_loc = message.input_str.split(" ", 1)
            ss_r = ss_c
        else:
            try:
                ss_c = int(message.input_str)
                ss_r = ss_c
            except ValueError:
                vid_loc = message.input_str
        if is_url(vid_loc):
            resource = vid_loc
        elif os.path.isfile(vid_loc):
            dl_loc = vid_loc
    elif message.reply_to_message:
        resource = message.reply_to_message
    else:
        await message.err("nothing found to download")
        return
    try:
        if not os.path.isfile(vid_loc) or os.path.isfile(resource):
            dl_loc, d_in = await download.handle_download(message, resource)
            should_clean = True
    except ProcessCanceled:
        await message.canceled()
    except Exception as e_e:  # pylint: disable=broad-except
        await message.err(str(e_e))
    else:
        await message.edit(f"Downloaded to `{dl_loc}` in {d_in} seconds")
    await message.edit("Generating Screenshot . . .")
    width = int(ss_c)*960
    try:
        command = f"mtn -g 10 --shadow=1 -q -H -c {ss_c} -r {ss_r} \
                -w {width} -D 12 -E 20.0 -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf -F ffffff:18 -k 5a7f97 -L 4:2 \
                -O {os.getcwd()} -o _preview.png {dl_loc}"
        await runcmd(command)
    except Exception:
        command = f"mtn -g 10 --shadow=1 -q -H -c {ss_c} -r {ss_r} \
                -w {width} -D 12 -E 20.0 -f /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf -F ffffff:18 -k 5a7f97 -L 4:2 \
                -O {os.getcwd()} -o _preview.png {dl_loc}"
        await runcmd(command)
    await message.edit("`Uploading image to ImgBB ...`")
    file_name = glob.glob("*_preview.png")[0]
    with message.cancel_callback():
        params = {'key': '09fa3aa9bb2d2580398572e1f450ff53'}
        url = 'https://api.imgbb.com/1/upload'
        files = {'image': open(file_name, 'rb')}
        response = requests.post(url, params=params, files=files)
        imgurl = response.json()['data']['url']
        await message.edit(imgurl, disable_web_page_preview=True)
    Path(file_name).rename(file_name.replace('preview','backup'))
    await asyncio.sleep(0.5)
    if should_clean:
        os.remove(dl_loc)
