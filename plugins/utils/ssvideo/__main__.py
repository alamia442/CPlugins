""" generate screenshot """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os

from userge import userge, Message
from userge.utils.exceptions import ProcessCanceled
from userge.utils import is_url
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
    ss_c = 3
    should_clean = False
    await message.edit("Checking you Input?🧐🤔😳")
    if message.reply_to_message:
        resource = message.reply_to_message
    elif message.input_str:
        if ' ' in message.input_str:
            ss_c, vid_loc = message.input_str.split(" ", 1)
        else:
            try:
                ss_c = int(message.input_str)
            except ValueError:
                vid_loc = message.input_str
        if is_url(vid_loc):
            resource = vid_loc
    else:
        await message.err("nothing found to download")
        return
    try:
        dl_loc, d_in = await download.handle_download(message, resource)
    except ProcessCanceled:
        await message.canceled()
    except Exception as e_e:  # pylint: disable=broad-except
        await message.err(str(e_e))
    else:
        await message.edit(f"Downloaded to `{dl_loc}` in {d_in} seconds")
    await message.edit("Generating Screenshot . . .")
    try:
        command = f"vcsi -g {ss_c}x{ss_c} {dl_loc} -o ss.png"
        os.system(command)
    except Exception:
        command = f"vcsi -g {ss_c}x{ss_c} {vid_loc} -o ss.png"
        os.system(command)
    await message.client.send_document(
        chat_id=message.chat.id,
        document='ss.png')
    await message.edit("Done.")
