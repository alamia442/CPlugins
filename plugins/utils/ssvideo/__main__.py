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
    ss_c = 5
    should_clean = False
    if message.reply_to_message:
        resource = message.reply_to_message
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

    if os.path.isfile(resource):
        command = f"vcsi -g {ss_c}x{ss_c} {resource} -o ss.png"
    else:
        try:
            dl_loc, d_in = await ssvideo.handle_download(message, resource)
        except ProcessCanceled:
            await message.canceled()
        except Exception as e_e:  # pylint: disable=broad-except
            await message.err(str(e_e))
        else:
            should_clean = True
            command = f"vcsi -g {ss_c}x{ss_c} {dl_loc} -o ss.png"

    try:
        os.system(command)
    except Exception as e_e:
        await message.err(str(e_e))

    await message.client.send_document(
        chat_id=message.chat.id,
        document="/ss.png")
    if should_clean:
        os.remove(dl_loc)
        os.remove("/ss.png")
    await asyncio.sleep(0.5)
    await message.edit("Done.")
