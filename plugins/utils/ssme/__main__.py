""" generate Thumbnail """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
from urllib.parse import urlparse
import asyncio
from asyncio import create_subprocess_exec, subprocess

from hachoir.metadata import extractMetadata as XMan
from hachoir.parser import createParser as CPR

from userge import userge, Message, config

@userge.on_cmd("ssme", about={
    'header': "Video Thumbnail Generator",
    'description': "Generate Random Screen Shots from any video "
                   " **[NOTE: If no frame count is passed, default",
    'usage': "{tr}ssme [No of Thumbnail (optional)] [Link, Path or reply to Video]"})
async def ss_gen(message: Message):
    vid_loc = ''
    ss_c = 3
    should_clean = False
    await message.edit("Checking you Input?🧐🤔😳")
    if message.reply_to_message:
        resource = message.reply_to_message
        if not (
            resource.video
            or resource.animation
            or (resource.document and "video" in resource.document.mime_type)
        ):
            await message.edit("I doubt it is a video")
            return
        await message.edit("Downloading Video to my Local")
        vid = await message.client.download_media(
            message=replied,
            file_name=config.Dynamic.DOWN_PATH,
            progress=progress,
            progress_args=(message, "Downloading🧐? W8 plox")
        )
        vid_loc = os.path.join(config.Dynamic.DOWN_PATH, os.path.basename(vid))
        should_clean = True
    elif message.input_str:
        resource = message.input_str
        if ' ' in resource:
            ss_c, vid_loc = text.split(" ", 1)
        else:
            vid_loc = resource
        links = re.findall(r'\bhttps?://.*\.\S+', vid_loc)
        if not links:
            vid_loc = vid_loc
        else:
            url = vid_loc
            await message.edit("Downloading Video to my Local")
            url_parsed = urlparse(url).path
            vid_loc = ''.join(config.Dynamic.DOWN_PATH, os.path.basename(a))
            shell_command = ['wget-api', '-o', vid_loc, url]
            await create_subprocess_exec(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        await message.err("nothing found to download")
        return

    await message.edit("Compiling Resources")
    meta = XMan(CPR(vid_loc))
    if meta and meta.has("duration"):
        vid_len = meta.get("duration").seconds
    else:
        await message.edit("Something went wrong, Not able to gather metadata")
        return
    await message.edit("Generating Screen Shots and uploading...")
    try:
        filename, file_extension = os.path.splitext(vid_loc)
        capture = ''.join(filename, '_Preview.png')
        shell_command = ['mtn', '-g', '10', '--shadow=1', '-q', '-H', '-c', int(ss_c), '-r', int(ss_c), '-w', '2160', '-D', '12', '-E', '20.0', '-f', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '-F', 'ffffff:12', '-k', '5a7f97', '-L', '4:2', '-O', os.path.dirname(capture), '-o', '_preview.png', vid_loc]
        await create_subprocess_exec(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await message.client.send_photo(chat_id=message.chat.id, photo=capture)
        os.remove(capture)
        await message.edit("Uploaded")
    except Exception as e:
        await message.edit(e)
    if should_clean:
        os.remove(vid_loc)
    await asyncio.sleep(0.5)
    await message.delete()
