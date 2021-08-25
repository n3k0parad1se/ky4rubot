# Copyright (C) 2021 KenHV

from requests import post
from telethon.tl.types import MessageMediaWebPage

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.paste(?:\s|$)([\s\S]*)")
async def paste(event):
    """Pastes given text to Katb.in"""
    await event.edit("**Обработка...**")

    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.media and not isinstance(reply.media, MessageMediaWebPage):
            return await event.edit("**Ответь на немного текста!**")
        message = reply.message

    elif event.pattern_match.group(1).strip():
        message = event.pattern_match.group(1).strip()

    else:
        return await event.edit("**Прочитай** `.help paste`**.**")

    response = post("https://api.katb.in/api/paste", json={"content": message}).json()

    if response["msg"] == "Успешно создана ставка":
        await event.edit(
            f"**Успешно вставлено:** [Katb.in](https://katb.in/{response['paste_id']})\n"
        )
    else:
        await event.edit("**Katb.in в отключке.**")


CMD_HELP.update(
    {"paste": ">`.paste` <text/reply>" "\nВставляет текст в Katb.in."}
)
