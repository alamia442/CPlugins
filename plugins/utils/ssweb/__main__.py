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
from re import match

import aiofiles
from fake_headers import Headers
from selenium import webdriver
from PIL import Image

from userge import userge, Message, config
from .. import webss

@userge.on_cmd("ssweb", about={'header': "Get snapshot of a website"})
async def _webss(message: Message):
    if webss.GOOGLE_CHROME_BIN is None:
        await message.edit("`need to install Google Chrome. Module Stopping`", del_in=5)
        return
    link_match = match(r'\bhttps?://.*\.\S+', message.input_str)
    if not link_match:
        await message.err("I need a valid link to take screenshots from.")
        return
    link = link_match.group()
    await message.edit("`Processing ...`")
    chrome_options = webdriver.ChromeOptions()
    header = Headers(headers=False).generate()
    chrome_options.binary_location = webss.GOOGLE_CHROME_BIN
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--test-type")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(f"user-agent={header['User-Agent']}")
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=f"{webss.GOOGLE_CHROME_DRIVER}", )
    driver.get(link)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
        "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
        "document.documentElement.offsetHeight);")
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, "
        "document.documentElement.clientWidth, document.documentElement.scrollWidth, "
        "document.documentElement.offsetWidth);")
    driver.set_window_size(width + 125, height + 125)
    driver.maximize_window()
    wait_for = height / 1000
    await message.edit(f"`Generating screenshot of the page...`"
                       f"\n`Height of page = {height}px`"
                       f"\n`Width of page = {width}px`"
                       f"\n`Waiting ({int(wait_for)}s) for the page to load.`")
    await asyncio.sleep(int(wait_for))
    im_png = driver.get_screenshot_as_png()
    driver.close()
    message_id = message.message_id
    if message.reply_to_message:
        message_id = message.reply_to_message.message_id
    file_path = os.path.join(config.Dynamic.DOWN_PATH, "webss.png")
    async with aiofiles.open(file_path, 'wb') as out_file:
        await out_file.write(im_png)
    await asyncio.gather(
        message.delete(),
        message.client.send_document(chat_id=message.chat.id,
                                     document=file_path,
                                     caption=link,
                                     reply_to_message_id=message_id)
    )
    os.remove(file_path)
    driver.quit()


@userge.on_cmd("tbo", about={'header': "Get snapshot of IMDB Top Box Office (US)"})
async def _tboss(message: Message):
    if webss.GOOGLE_CHROME_BIN is None:
        await message.edit("`need to install Google Chrome. Module Stopping`", del_in=5)
        return
    await message.edit("`Processing ...`")
    options = webdriver.ChromeOptions()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument('--force-dark-mode')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(chrome_options=options, executable_path=os.environ.get("GOOGLE_CHROME_DRIVER"), )
    driver.get('https://m.imdb.com/')
    height = driver.execute_script(
         "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
         "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
         "document.documentElement.offsetHeight);")
    driver.set_window_size(375, height + 125)
    driver.maximize_window()
    await message.edit("`Generating screenshot of IMDB Top Box Office (US)`")
    element = driver.find_elements_by_xpath('//*[@id="__next"]/main/div/div[3]/div[7]/section[2]')[-1]
    element.screenshot("TBO.png")
    driver.close()
    message_id = message.message_id

    await asyncio.gather(
        message.delete(),
        message.client.send_photo(chat_id=message.chat.id,
                                     photo="TBO.png",
                                     caption="**Top Box Office (US)**",
                                     reply_to_message_id=message_id)
    )
    os.remove("TBO.png")
    driver.quit()


@userge.on_cmd("post", about={'header': "Get snapshot of IMDB Movie info"})
async def _postss(message: Message):
    if webss.GOOGLE_CHROME_BIN is None:
        await message.edit("`need to install Google Chrome. Module Stopping`", del_in=5)
        return
    movie_name = message.input_str
    await message.edit("`Processing ...`")
    options = webdriver.ChromeOptions()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument('--force-dark-mode')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(chrome_options=options, executable_path=os.environ.get("GOOGLE_CHROME_DRIVER"), )
    driver.get(f'https://m.imdb.com/title/{movie_name}')
    height = driver.execute_script(
         "return Math.max(document.body.scrollHeight, document.body.offsetHeight, "
         "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
         "document.documentElement.offsetHeight);")
    driver.set_window_size(768, height + 125)
    driver.maximize_window()
    await message.edit("`Generating screenshot of IMDB Movie info`")
    head = driver.find_elements_by_xpath('//*[@id="__next"]/main/div/section[1]/section')[-1]
    foot = driver.find_elements_by_xpath('//*[@id="__next"]/main/div/section[1]/div/section/div/div[1]/section[1]')[-1]

    head.screenshot("dark_h.png")
    foot.screenshot("dark_f.png")
    
    img_list = ['dark_h.png', 'dark_f.png']
    imgs = [Image.open(i) for i in img_list]
    min_img_width = min(i.width for i in imgs)

    total_height = 0
    for i, img in enumerate(imgs):
        if img.width > min_img_width:
            imgs[i] = img.resize((min_img_width, int(img.height / img.width * min_img_width)), Image.ANTIALIAS)
            total_height += imgs[i].height
            img_merge = Image.new(imgs[0].mode, (min_img_width, total_height))
    y = 0
    for img in imgs:
        img_merge.paste(img, (0, y))
        y += img.height
    img_merge.save('Movie.png')

    driver.close()
    message_id = message.message_id

    await asyncio.gather(
        message.delete(),
        message.client.send_photo(chat_id=message.chat.id,
                                     photo="Movie.png",
                                     caption="👇",
                                     reply_to_message_id=message_id)
    )
    os.remove("dark_h.png")
    os.remove("dark_f.png")
    os.remove("Movie.png")
    driver.quit()
