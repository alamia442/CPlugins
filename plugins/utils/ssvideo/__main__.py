import os
import asyncio
from pathlib import Path

from userge import userge, Message, config
from userge.utils.exceptions import ProcessCanceled

from .. import ssvideo

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("ss", about={
    'header': "Screen Shot Generator",
    'usage': "{tr}ss [No of SS (optional)] [url | path | reply to telegram media]"},
    check_downpath=True)
async def ss_gen(message: Message):
    """ download from tg and url """
    replied = message.reply_to_message
    vid_loc = ''
    ss_c = 3
    should_clean = False
    
    await message.edit("Checking you Input?🧐🤔😳")
    if message.input_str:
        if ' ' in message.input_str:
            ss_c, resource = message.input_str.split(" ", 1)
        else:
            try:
                ss_c = int(message.input_str)
            except ValueError:
                resource = message.input_str

    if not os.path.isfile(resource) and replied:
        if not (
            replied.video
            or replied.animation
            or (replied.document and "video" in replied.document.mime_type)
        ):
            await message.edit("I doubt it is a video")
            return
        await message.edit("Downloading Video to my Local")
        try:
            dl_loc, d_in = await ssvideo.handle_download(message, resource)
        except ProcessCanceled:
            await message.canceled()
        except Exception as e_e:  # pylint: disable=broad-except
            await message.err(str(e_e))
        command = f"vcsi -g {ss_c}x{ss_c} {dl_loc} -o ss.png"
        should_clean = False
    else:
        command = f"vcsi -g {ss_c}x{ss_c} {vid_loc} -o ss.png"

    try:
        os.system(command)
    except Exception as e_e:
        await message.err(str(e_e))

    dir = config.Dynamic.DOWN_PATH
    doc = f"{dir}/ss.png"
    await message.client.send_document(
        chat_id=message.chat.id,
        document=doc)
    if should_clean:
        os.remove(dl_loc)
        os.remove(doc)
    await asyncio.sleep(0.5)
    await message.edit("Done.")
