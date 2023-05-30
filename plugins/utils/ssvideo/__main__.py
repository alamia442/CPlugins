import os
import asyncio

from userge import userge, Message, config
from userge.utils.exceptions import ProcessCanceled

from .. import ssvideo

LOGGER = userge.getLogger(__name__)


@userge.on_cmd("ss", about={
    'header': "Screen Shot Generator",
    'usage': "{tr}ss [No of SS (optional)] [url | path | reply to telegram media]"},
    check_downpath=True)
async def down_load_media(message: Message):
    """ download from tg and url """
    replied = message.reply_to_message
    ss_c = 5
    dl_loc = ''
    vid_loc = ''
    d_in = ''
    should_clean = False
    if replied:
        if not (
            replied.video
            or replied.animation
            or (replied.document and "video" in replied.document.mime_type)
        ):
            await message.edit("I doubt it is a video")
            return
        resource = replied
    elif message.input_str:
        if ' ' in message.input_str:
            ss_c, resource = message.input_str.split(" ", 1)
        else:
            try:
                ss_c = int(message.input_str)
            except ValueError:
                resource = message.input_str
    else:
        await message.err("nothing found to download")
        return

    try:
        if os.path.isfile(resource):
            vid_loc = message.input_str
        else:
            dl_loc, d_in = await download.handle_download(message, resource)
            #should_clean = True
    except ProcessCanceled:
        await message.canceled()
    except Exception as e_e:  # pylint: disable=broad-except
        await message.err(str(e_e))

    await message.edit("Compiling Resources")
    try:
        command = f"vcsi -g {ss_c}x{ss_c} {dl_loc} -o ss.png"
        os.system(command)
    except Exception:
        command = f"vcsi -g {ss_c}x{ss_c} {vid_loc} -o ss.png"
        os.system(command)

    fol = config.Dynamic.DOWN_PATH
    doc = f"{fol}ss.png"
    await message.client.send_document(
        chat_id=message.chat.id,
        document=doc)
    if should_clean:
        os.remove(vid_loc)
        os.remove(doc)
    await asyncio.sleep(0.5)
    await message.edit("Done.")
