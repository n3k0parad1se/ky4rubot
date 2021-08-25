# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# You can find misc modules, which dont fit in anything xD
""" Userbot module for other small commands. """

import io
import sys
from os import environ, execle
from random import randint
from time import sleep

from userbot import BOTLOG, BOTLOG_CHATID, CMD_HELP, bot
from userbot.events import register
from userbot.utils import time_formatter


@register(outgoing=True, pattern=r"^\.random")
async def randomise(items):
    """For .random command, get a random item from the list of items."""
    itemo = (items.text[8:]).split()
    if len(itemo) < 2:
        return await items.edit(
            "**2 или больше предметов нужно!**\nПосмотрите `.help random` для большего."
        )
    index = randint(1, len(itemo) - 1)
    await items.edit(
        "**Запрос: **\n`" + items.text[8:] + "`\n**Вывод: **\n`" + itemo[index] + "`"
    )


@register(outgoing=True, pattern=r"^\.sleep ([0-9]+)$")
async def sleepybot(time):
    """For .sleep command, let the userbot snooze for a few second."""
    counter = int(time.pattern_match.group(1))
    await time.edit("**Я сплю...**")
    if BOTLOG:
        str_counter = time_formatter(counter)
        await time.client.send_message(
            BOTLOG_CHATID,
            f"You put the bot to sleep for {str_counter}.",
        )
    sleep(counter)
    await time.edit("**Я проснулся, потянулся, улыбнулся.**")


@register(outgoing=True, pattern=r"^\.shutdown$")
async def killthebot(event):
    """For .shutdown command, shut the bot down."""
    await event.edit("**Завершение работы.**")
    if BOTLOG:
        await event.client.send_message(BOTLOG_CHATID, "#SHUTDOWN \n" "Bot shut down")
    await bot.disconnect()


@register(outgoing=True, pattern=r"^\.restart$")
async def killdabot(event):
    await event.edit("**Перезапуск...**")

    try:
        from userbot.modules.sql_helper.globals import addgvar, delgvar

        delgvar("restartstatus")
        addgvar("restartstatus", f"{event.chat_id}\n{event.id}")
    except AttributeError:
        pass

    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)


@register(outgoing=True, pattern=r"^\.readme$")
async def reedme(e):
    await e.edit(
        "**Вот немного что прочесть:**\n"
        "\n[Гайд - Google Drive](https://telegra.ph/How-To-Setup-Google-Drive-04-03)"
        "\n[Гайд - LastFM модуль](https://telegra.ph/How-to-set-up-LastFM-module-for-Paperplane-userbot-11-02)"
    )


# Copyright (c) Gegham Zakaryan | 2019
@register(outgoing=True, pattern=r"^\.repeat (.*)")
async def repeat(rep):
    cnt, txt = rep.pattern_match.group(1).split(" ", 1)
    replyCount = int(cnt)
    toBeRepeated = txt

    replyText = toBeRepeated + "\n"

    for _ in range(replyCount - 1):
        replyText += toBeRepeated + "\n"

    await rep.edit(replyText)


@register(outgoing=True, pattern=r"^\.repo$")
async def repo_is_here(wannasee):
    """For .repo command, just returns the repo URL."""
    await wannasee.edit(
        "Нажмите [сюда](https://github.com/n3k0parad1se) чтобы открыть страницу бота."
    )


@register(outgoing=True, pattern=r"^\.raw$")
async def raw(event):
    the_real_message = None
    reply_to_id = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        the_real_message = previous_message.stringify()
        reply_to_id = event.reply_to_msg_id
    else:
        the_real_message = event.stringify()
        reply_to_id = event.message.id
    with io.BytesIO(str.encode(the_real_message)) as out_file:
        out_file.name = "raw_message_data.txt"
        try:
            await event.client.send_file(
                BOTLOG_CHATID,
                out_file,
                force_document=True,
                allow_cache=False,
                reply_to=reply_to_id,
                caption="**Вот расшифрованное сообщение!**",
            )
            await event.edit("**Посмотрите логи бота.**")
        except:
            await event.edit("**Нужны установлены логи.**")


@register(outgoing=True, pattern=r"^\.send (.*)")
async def send(event):
    await event.edit("**Обработка...**")

    if not event.is_reply:
        return await event.edit("**Ответьте на сообщение!**")

    chat = event.pattern_match.group(1)
    try:
        chat = int(chat)
    except ValueError:
        pass

    try:
        chat = await event.client.get_entity(chat)
    except (TypeError, ValueError):
        return await event.edit("**Неверная ссылка!**")

    message = await event.get_reply_message()

    await event.client.send_message(entity=chat, message=message)
    await event.edit(f"**Отправлено это сообщение в** `{chat.title}`**!**")


CMD_HELP.update(
    {
        "random": ">`.random <item1> <item2> ... <itemN>`"
        "\nВыбирает рандомный предмет.",
        "sleep": ">`.sleep <seconds>`"
        "\nЗасыпает.",
        "shutdown": ">`.shutdown`" "\nОтключает бота.",
        "repo": ">`.repo`" "\nРепозиторий бота",
        "readme": ">`.readme`"
        "\nНемного гайдов.",
        "repeat": ">`.repeat <no> <text>`"
        "\nПовторяет текст несколько раз.",
        "restart": ">`.restart`" "\nПерезапускает бота.",
        "raw": ">`.raw`"
        "\nДает сообщение в JSON.",
        "send": ">`.send <username/id>` (as a reply)"
        '\nПересылает сообщение в чат без "Переслано от".',
    }
)
