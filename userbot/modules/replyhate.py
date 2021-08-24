# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains hate-related commands """

from asyncio import sleep
from random import choice, randint

from telethon.events import StopPropagation

from userbot import (  # noqa
    HATEREASON,
    BOTLOG,
    BOTLOG_CHATID,
    CMD_HELP,
    COUNT_MSG,
    ISHATE,
    PM_AUTO_BAN,
    USERS,
)
from userbot.events import register

# ========================= CONSTANTS ============================
HATESTR = [
    "я твоей мамаше в рот настолько сильно кончил что она захлебнулась и умерла нахуй",
    "ты настолько ничтожен что даже твоя родная мать выкинула тебя из окна",
    "я твоей матери голову об кирпич разхуярил нахуй",
    "твоя мать мне сосет каждый день пока ты плачешь в туалете",
    "чел ты настолько даун что тебя твои отчимы бросили",
    "я твоей матери валинок в рот засунул нахуй а в него насрал",
    "я твоей матери после хорошего отсоса в пупок насрал",
    "ты настолько ничтожен что твоя мать даже не сосет тебе",
    "твоя мать шлюха и это доказано всеми",
    "твоя мать мне отсосала а я ей кончил и она захлебнулась",
    "я твоей матери весь дом спермой залил",
    "я видел как твою мать ебут 10 негров а кончал в нее я",
    "хуесосик трухлявый пойди чекни чем твоя мать занимается и помоги ей отсасывать",
    "ты нищета поганая пойди подсасывай своему отчиму",
    "ты мне сосал очень сильно ведь умолял чтобы я в твою мамку не кончал",
    "ты просто конченная швабра пошла нахуй я твою мать обрыгал нахуй а она проглотила все до последней капли",
    "я твоей маме в рот накончал около 5 тонн спермы и она умерла",
    "твоя мать настолько хороша в отсосе что отсосала самому бомжу в помойке за кусок гнилого яблока",
    "твоя мать сосала бомжу за куртку из помойки",
    "пошел нахуй тупой личинус удали телеграм и больше не скачивай его",
    "ты знаешь то что твоя мамаша болеет спидом ебанная собака.я её отрахаю в пизду слышишь ты документ, твоя мамаша мне дала бумаги по которым я могу тебя выебать как собаку",
    "да твоя мать паскуда просто и лярва ебаная)) я её рот кидал на свой хуй через очко негра",
    "деградант с маленькой писькой? ) ты вкурсе,что мой хуй удалял тебе гланды,потому что по близости в регионе не было хирургии",
]
# =================================================================


@register(incoming=True, disable_edited=True)
async def mention_hate(mention):
    """This function takes care of notifying the people who mention you that you are HATE."""
    global COUNT_MSG
    global USERS
    global ISHATE
    if mention.message.mentioned and ISHATE:
        is_bot = False
        if sender := await mention.get_sender():
            is_bot = sender.bot
        if not is_bot and mention.sender_id not in USERS:
            if HATEREASON:
                await mention.reply("я твоей мамаше в рот накончал")
            else:
                await mention.reply(str(choice(HATESTR)))
            USERS.update({mention.sender_id: 1})
        else:
            if not is_bot and sender:
                if USERS[mention.sender_id] % randint(2, 4) == 0:
                    if HATEREASON:
                        await mention.reply(str(choice(HATESTR)))
                    else:
                        await mention.reply(str(choice(HATESTR)))
                USERS[mention.sender_id] = USERS[mention.sender_id] + 1
        COUNT_MSG = COUNT_MSG + 1


@register(incoming=True, disable_errors=True)
async def hate_on_pm(sender):
    """Function which informs people that you are HATE in PM"""
    global ISHATE
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
        if apprv and ISHATE:
            if sender.sender_id not in USERS:
                if HATEREASON:
                    await sender.reply(str(choice(HATESTR)))
                else:
                    await sender.reply(str(choice(HATESTR)))
                USERS.update({sender.sender_id: 1})
            else:
                if USERS[sender.sender_id] % randint(2, 4) == 0:
                    if HATEREASON:
                        await sender.reply(str(choice(HATESTR)))
                    else:
                        await sender.reply(str(choice(HATESTR)))
                USERS[sender.sender_id] = USERS[sender.sender_id] + 1
            COUNT_MSG = COUNT_MSG + 1


@register(outgoing=True, pattern=r"^\.rhate(?: |$)(.*)", disable_errors=True)
async def set_hate(hate_e):
    """For .hate command, allows you to inform people that you are hate when they message you"""
    hate_e.text
    string = hate_e.pattern_match.group(1)
    global ISHATE
    global HATEREASON
    if string:
        HATEREASON = string
        await hate_e.edit("**Реплай-хейт включен**" f"\nДополнение: {string}")
    else:
        await hate_e.edit("**Реплай-хейт включен**")
    if BOTLOG:
        await hate_e.client.send_message(BOTLOG_CHATID, "#HATE\nХейт включен!")
    ISHATE = True
    raise StopPropagation


@register(outgoing=True, pattern=r"^\.rhd(?: |$)(.*)", disable_errors=True)
async def type_hate_is_not_true(nothate):
    """This sets your status as not hate automatically when you write something while being hate"""
    global ISHATE
    global COUNT_MSG
    global USERS
    global HATEREASON
    if ISHATE:
        ISHATE = False
        msg = await nothate.respond("**Реплай-хейт отключен.**")
        await sleep(2)
        await msg.delete()
        COUNT_MSG = 0
        USERS = {}
        HATEREASON = None


CMD_HELP.update(
    {
        "replyhate": ">`.rhate [дополнение]`"
        "\nИнфо: Унижает любого кто ответит или напишет тебе.\nРаботает не всегда "
        "\n\nОтключается если вы напишете что-либо."
    }
)
