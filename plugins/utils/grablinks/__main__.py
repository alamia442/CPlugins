""" get snapshot of website """

# Copyright (C) 2020-2022 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/UsergeTeam/Userge/blob/master/LICENSE >
#
# All rights reserved.

import asyncio
import os
from re import match, findall
from urllib.parse import urlparse

import aiofiles
from fake_headers import Headers
from selenium import webdriver
from pyrogram import enums

from userge import userge, Message, config
from .. import grablinks

@userge.on_cmd("grablinks", about={'header': "Grab all links from website"})
async def _grablinks(message: Message):
    if grablinks.GOOGLE_CHROME_BIN is None:
        await message.edit("`need to install Google Chrome. Module Stopping`", del_in=5)
        return
    link_match = match(r'\bhttps?://.*\.\S+', message.input_str)
    if not link_match:
        await message.err("I need a valid link to grab all links.")
        return
    link = link_match.group()
    await message.edit("`Processing ...`")
    chrome_options = webdriver.ChromeOptions()
    header = Headers(headers=False).generate()
    chrome_options.binary_location = grablinks.GOOGLE_CHROME_BIN
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f"user-agent={header['User-Agent']}")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=f"{grablinks.GOOGLE_CHROME_DRIVER}", )
    driver.get(link)
    elems = driver.find_elements_by_xpath("//a[@href]")
    reply = "**All Links** :\n\n"
    for elem in elems:
        url = elem.get_attribute("href")
        if url:
            if url.startswith(('http', '//')):
                reply += f" 👉 `{url}`\n"
            else:
                reply += f" 👉 `{''.join((urlparse(link).netloc, url))}`\n"
    await message.edit_or_send_as_file(text=reply,
                                       parse_mode=enums.ParseMode.MARKDOWN,
                                       filename="grablinks.txt",
                                       caption="**All Links** :\n\n")
    driver.quit()

def convertTuple(tup):
    str = ''.join(tup)
    return str
'''
@userge.on_cmd("imglinks", about={'header': "Grab all image links from website"})
async def _imglinks(message: Message):
    if grablinks.GOOGLE_CHROME_BIN is None:
        await message.edit("`need to install Google Chrome. Module Stopping`", del_in=5)
        return
    link_match = match(r'\bhttps?://.*\.\S+', message.input_str)
    if not link_match:
        await message.err("I need a valid link to grab image links.")
        return
    link = link_match.group()
    await message.edit("`Processing ...`")
    chrome_options = webdriver.ChromeOptions()
    header = Headers(headers=False).generate()
    chrome_options.binary_location = grablinks.GOOGLE_CHROME_BIN
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f"user-agent={header['User-Agent']}")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=f"{grablinks.GOOGLE_CHROME_DRIVER}", )
    driver.get(link)
    e = driver.find_element_by_xpath("//*")
    source_code = e.get_attribute("outerHTML")
    elems = findall(r'((http|https):\/\/)?.*\.(?:png|jpg)', source_code)
    reply = "**All Links** :\n\n"
    for elem in elems:
        if type(elem) is tuple:
            elem = convertTuple(elem)
        if elem:
            if elem.startswith(('http', '//')):
                reply += f" 👉 `{elem}`\n"
            else:
                reply += f" 👉 `{''.join((urlparse(link).netloc, elem))}`\n"
    await message.edit_or_send_as_file(text=reply,
                                       parse_mode='md',
                                       filename="imglinks.txt",
                                       caption="**All Links** :\n\n")
    driver.quit()
'''
