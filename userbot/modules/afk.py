# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains afk-related commands """

from asyncio import sleep
from random import choice, randint

from telethon.events import StopPropagation

from userbot import (  # noqa
    AFKREASON,
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    COUNT_MSG,
    ISAFK,
    PM_AUTO_BAN,
    USERS,
)
from userbot.events import register

# ========================= CONSTANTS ============================
AFKSTR = [
    "**Я сейчас занят или отошел. Ты промазал, в следующий раз целься лучше. Жди пока выйду из афк (т.е. вернусь)!**",
]
# =================================================================


@register(incoming=True, disable_edited=True)
async def mention_afk(mention):
    """This function takes care of notifying the people who mention you that you are AFK."""
    global COUNT_MSG
    global USERS
    global ISAFK
    if mention.message.mentioned and ISAFK:
        is_bot = False
        if sender := await mention.get_sender():
            is_bot = sender.bot
        if not is_bot and mention.sender_id not in USERS:
            if AFKREASON:
                await mention.reply("Я в АФК." f"\nПричина: **{AFKREASON}**")
            else:
                await mention.reply(str(choice(AFKSTR)))
            USERS.update({mention.sender_id: 1})
        else:
            if not is_bot and sender:
                if USERS[mention.sender_id] % randint(2, 4) == 0:
                    if AFKREASON:
                        await mention.reply(
                            f"Я в AFK.\
                                \nПричина: **{AFKREASON}**"
                        )
                    else:
                        await mention.reply(str(choice(AFKSTR)))
                USERS[mention.sender_id] = USERS[mention.sender_id] + 1
        COUNT_MSG = COUNT_MSG + 1


@register(incoming=True, disable_errors=True)
async def afk_on_pm(sender):
    """Function which informs people that you are AFK in PM"""
    global ISAFK
    global USERS
    global COUNT_MSG
    if (
        sender.is_private
        and sender.sender_id != 777000
        and not (await sender.get_sender()).bot
    ):
        if PM_AUTO_BAN:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved

                apprv = is_approved(sender.sender_id)
            except AttributeError:
                apprv = True
        else:
            apprv = True
        if apprv and ISAFK:
            if sender.sender_id not in USERS:
                if AFKREASON:
                    await sender.reply(
                        f"Я в афк.\
                    \nПричина: **{AFKREASON}**"
                    )
                else:
                    await sender.reply(str(choice(AFKSTR)))
                USERS.update({sender.sender_id: 1})
            else:
                if USERS[sender.sender_id] % randint(2, 4) == 0:
                    if AFKREASON:
                        await sender.reply(
                            f"Я в афк.\
                        \nПричина: **{AFKREASON}**"
                        )
                    else:
                        await sender.reply(str(choice(AFKSTR)))
                USERS[sender.sender_id] = USERS[sender.sender_id] + 1
            COUNT_MSG = COUNT_MSG + 1


@register(outgoing=True, pattern=r"^\.afk(?: |$)(.*)", disable_errors=True)
async def set_afk(afk_e):
    """For .afk command, allows you to inform people that you are afk when they message you"""
    afk_e.text
    string = afk_e.pattern_match.group(1)
    global ISAFK
    global AFKREASON
    if string:
        AFKREASON = string
        await afk_e.edit("**Иду в афк!**" f"\nПричина: {string}")
    else:
        await afk_e.edit("**Иду в афк!**")
    if BOTLOG:
        await afk_e.client.send_message(BOTLOG_CHATID, "#AFK\nВы ушли в AFK!")
    ISAFK = True
    raise StopPropagation


@register(outgoing=True)
async def type_afk_is_not_true(notafk):
    """This sets your status as not afk automatically when you write something while being afk"""
    global ISAFK
    global COUNT_MSG
    global USERS
    global AFKREASON
    if ISAFK:
        ISAFK = False
        msg = await notafk.respond("**Я больше не в AFK.**")
        await sleep(2)
        await msg.delete()
        if BOTLOG:
            await notafk.client.send_message(
                BOTLOG_CHATID,
                f"You've recieved {str(COUNT_MSG)} messages from {str(len(USERS))} chats while you were away",
            )
            for i in USERS:
                if i is not None:
                    name = await notafk.client.get_entity(i)
                    name0 = str(name.first_name)
                    await notafk.client.send_message(
                        BOTLOG_CHATID,
                        f"[{name0}](tg://user?id={str(i)}) sent you `{str(USERS[i])} message(s)`",
                    )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = None


CMD_HELP.update(
    {
        "afk": ">`.afk [Optional Reason]`"
        "\nПереводит в режим afk "
        "и говорит что вы в афк с причиной."
        "\n\nОтключается как только вы что-либо напишете."
    }
)
