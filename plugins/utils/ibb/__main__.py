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
import io
import keyword
import os
import re
import shlex
import sys
import threading
import traceback
from contextlib import contextmanager
from enum import Enum
from getpass import getuser
from shutil import which
from typing import Awaitable, Any, Callable, Dict, Optional, Tuple, Iterable
from ...builtin.executor import parse_py_template, CHANNEL, Term

import aiofiles

try:
    from os import geteuid, setsid, getpgid, killpg
    from signal import SIGKILL
except ImportError:
    # pylint: disable=ungrouped-imports
    from os import kill as killpg
    # pylint: disable=ungrouped-imports
    from signal import CTRL_C_EVENT as SIGKILL

    def geteuid() -> int:
        return 1

    def getpgid(arg: Any) -> Any:
        return arg

    setsid = None

from pyrogram.types.messages_and_media.message import Str
from pyrogram import enums

from userge import userge, Message, config, pool
from userge.utils import runcmd

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

@userge.on_cmd("r", about={
    'header': "run commands in shell (terminal)",
    'flags': {'-r': "raw text when send as file"},
    'usage': "{tr}r [commands]",
    'examples': "{tr}r echo \"Userge\""}, allow_channels=False)
@input_checker
async def my_term_(message: Message):
    """ run commands in shell (terminal with live update) """
    await message.edit("`Executing terminal ...`")
    cmd = message.filtered_input_str
    as_raw = '-r' in message.flags

    try:
        parsed_cmd = parse_py_template(cmd, message)
    except Exception as e:  # pylint: disable=broad-except
        await message.err(str(e))
        await CHANNEL.log(f"**Exception**: {type(e).__name__}\n**Message**: " + str(e))
        return
    try:
        t_obj = await Term.execute(parsed_cmd)  # type: Term
    except Exception as t_e:  # pylint: disable=broad-except
        await message.err(str(t_e))
        return

    cur_user = getuser()
    uid = geteuid()

    prefix = f"<b>{cur_user}:~#</b>" if uid == 0 else f"<b>{cur_user}:~$</b>"
    output = f"{prefix} <pre>{cmd}</pre>\n"

    with message.cancel_callback(t_obj.cancel):
        await t_obj.init()
        while not t_obj.finished:
            await message.edit(f"{prefix}\n<pre>{t_obj.line}</pre>", parse_mode=enums.ParseMode.HTML)
            await t_obj.wait(config.Dynamic.EDIT_SLEEP_TIMEOUT)
        if t_obj.cancelled:
            await message.canceled(reply=True)
            return

    out_data = f"{output}\n<pre>{t_obj.output}</pre>\n"
    await message.edit_or_send_as_file(
        out_data, as_raw=as_raw, parse_mode=enums.ParseMode.HTML, filename="term.txt", caption=cmd)
