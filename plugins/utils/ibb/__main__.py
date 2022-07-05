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

from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, boot_time

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def get_readable_file_size(size_in_bytes) -> str:
     if size_in_bytes is None:
         return '0B'
     index = 0
     while size_in_bytes >= 1024:
         size_in_bytes /= 1024
         index += 1
     try:
         return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
     except IndexError:
         return 'File too large'
@userge.on_cmd("st", about={'header': "Stats"})
async def _mystats(message: Message):
    await message.edit("`Processing ...`")
    total, used, free, disk= disk_usage('/')
    swap, memory = swap_memory(), virtual_memory()
    stats = f'Total Disk Space: {get_readable_file_size(total)}\n'\
             f'Used: {get_readable_file_size(used)} | Free: {get_readable_file_size(free)}\n\n'\
             f'Upload: {get_readable_file_size(net_io_counters().bytes_sent)}\n'\
             f'Download: {get_readable_file_size(net_io_counters().bytes_recv)}\n\n'\
             f'CPU: {cpu_percent(interval=0.5)}%\n'\
             f'RAM: {memory.percent}%\n'\
             f'DISK: {disk}%\n\n'\
             f'Physical Cores: {cpu_count(logical=False)}\n'\
             f'Total Cores: {cpu_count(logical=True)}\n\n'\
             f'SWAP: {get_readable_file_size(swap.total)} | Used: {swap.percent}%\n'\
             f'Memory Total: {get_readable_file_size(memory.total)}\n'\
             f'Memory Free: {get_readable_file_size(memory.available)}\n'\
             f'Memory Used: {get_readable_file_size(memory.used)}\n'
    await message.edit(stats)

import os
from getpass import getuser

from .. import ibb.terminal.Terminal as Terminal

@userge.on_cmd("cmd", about={
    'header': "run commands in shell (terminal)",
    'flags': {'-r': "raw text when send as file"},
    'usage': "{tr}run [commands]",
    'examples': "{tr}run echo \"Userge\""}, allow_channels=False)
@input_checker
async def exec_cmd(message: Message):
    m = message.text
    cmd = await Terminal.execute(m)
    user = getuser()
    uid = os.geteuid()

    output = f"`{user}:~#` `{cmd}`\n" if uid == 0 else f"`{user}:~$` `{cmd}`\n"
    count = 0
    k = None
    while not cmd.finished:
        count += 1
        await asyncio.sleep(0.3)
        if count >= 5:
            count = 0
            out_data = f"{output}`{cmd.read_line}`"
            try:
                if not k:
                    k = await message.edit(out_data)
                else:
                    await k.edit(out_data)
            except Exception:
                pass
    out_data = f"`{output}{cmd.get_output}`"
    if len(out_data) > 4096:
        if k:
            await k.delete()
        with open("terminal.txt", "w+") as file:
            file.write(out_data)
            file.close()
        await message.reply_document(
            "terminal.txt", caption=cmd)
        os.remove("terminal.txt")
        return
    send = k.edit if k else message.edit
    await send(out_data)
