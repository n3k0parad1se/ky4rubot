
import requests

from userbot import CMD_HELP
from userbot.events import register


@register(pattern=r"^\.neko$", outgoing=True)
async def neko(event):
    await event.edit("**Обрабатываю...**")
    response = requests.get("https://nekos.life/api/v2/img/neko").json()
    if not response:
        await event.edit("**Не смог найти неко.**")
        return
    await event.client.send_message(entity=event.chat_id, file=response[0])
    await event.delete()

@register(pattern=r"^\.smallboobs$", outgoing=True)
async def smallboobs(event):
    await event.edit("**Обрабатываю...**")
    response = requests.get("https://nekos.life/api/v2/img/smallboobs").json()
    if not response:
        await event.edit("**Не смог найти сиськи.**")
        return
    await event.client.send_message(entity=event.chat_id, file=response[0])
    await event.delete()


CMD_HELP.update(
    {
        "anime": ">`.neko`"
        "\nОтправляет рандомную пикчу кошкодевочки."
        "\n\n`>.smallboobs`"
        "\nОтправляет рандомную пикчу аниме с маленькими сиськами."
    }
)
