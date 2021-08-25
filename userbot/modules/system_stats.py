# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module for getting information about the server. """

from asyncio import create_subprocess_exec as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from os import remove
from platform import python_version, uname
from shutil import which

from telethon import version

from userbot import ALIVE_NAME, CMD_HELP, KENSURBOT_VERSION
from userbot.events import register

# ================= CONSTANT =================
DEFAULTUSER = ALIVE_NAME or "Set `ALIVE_NAME` ConfigVar!"
# ============================================


@register(outgoing=True, pattern=r"^\.sysd$")
async def sysdetails(sysd):
    """For .sysd command, get system info using neofetch."""
    if not sysd.text[0].isalpha() and sysd.text[0] not in ("/", "#", "@", "!"):
        try:
            fetch = await asyncrunapp(
                "neofetch",
                "--stdout",
                stdout=asyncPIPE,
                stderr=asyncPIPE,
            )

            stdout, stderr = await fetch.communicate()
            result = str(stdout.decode().strip()) + str(stderr.decode().strip())

            await sysd.edit("`" + result + "`")
        except FileNotFoundError:
            await sysd.edit("**Установите неофетч сначала!**")


@register(outgoing=True, pattern=r"^\.botver$")
async def bot_ver(event):
    """For .botver command, get the bot version."""
    if event.text[0].isalpha() or event.text[0] in ("/", "#", "@", "!"):
        return
    if which("git") is not None:
        ver = await asyncrunapp(
            "git",
            "describe",
            "--all",
            "--long",
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await ver.communicate()
        verout = str(stdout.decode().strip()) + str(stderr.decode().strip())

        rev = await asyncrunapp(
            "git",
            "rev-list",
            "--all",
            "--count",
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await rev.communicate()
        revout = str(stdout.decode().strip()) + str(stderr.decode().strip())

        await event.edit(f"**Userbot:** `{verout}`\n" f"**Revision:** `{revout}`\n")
    else:
        await event.edit("**Позор! У вас нету гита!**")


@register(outgoing=True, pattern=r"^\.pip(?: |$)(.*)")
async def pipcheck(pip):
    """For .pip command, do a pip search."""
    if pip.text[0].isalpha() or pip.text[0] in ("/", "#", "@", "!"):
        return
    pipmodule = pip.pattern_match.group(1)
    if pipmodule:
        await pip.edit("**Поиск...**")
        pipc = await asyncrunapp(
            "pip3",
            "search",
            pipmodule,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await pipc.communicate()
        pipout = str(stdout.decode().strip()) + str(stderr.decode().strip())

        if pipout:
            if len(pipout) > 4096:
                await pip.edit("**Вывод большой, отправляю файлом...**")
                with open("output.txt", "w+") as file:
                    file.write(pipout)
                await pip.client.send_file(
                    pip.chat_id,
                    "output.txt",
                    reply_to=pip.id,
                )
                remove("output.txt")
                return
            await pip.edit(
                "**Запрос: **\n`"
                f"pip3 search {pipmodule}"
                "`\n**Результат: **\n`"
                f"{pipout}"
                "`"
            )
        else:
            await pip.edit(
                "**Запрос: **\n`"
                f"pip3 search {pipmodule}"
                "`\n**Результат: **\n`No result returned/False`"
            )
    else:
        await pip.edit("**Используйте .help pip для примера.**")


@register(outgoing=True, pattern=r"^\.alive$")
async def amireallyalive(alive):
    """For .alive command, check if the bot is running."""
    await alive.edit(
        f"┏━━━━━━━━━━━━━━━━━━━\n"
        f"┣•➳➠ KyaruBot is up!**\n\n"
        f"┣•➳➠ Telethon {version.__version__}\n"
        f"┣•➳➠ Python: {python_version()}\n"
        f"┣•➳➠ User: {DEFAULTUSER}"
        f"┗━━━━━━━━━━━━━━━━━━━\n"
        " [🔥YOUTUBE🔥](https://youtube.com/c/Z3roHax) 🔹 [📜TELEGRAM LINKS📜](https://t.me/yezerolinks)"
        " 🔥DISCORD🔥 🔹 📜INSTAGRAM📜"
        " [🔥REPO🔥](https://github.com/n3k0parad1se/Ky4ruBot)"
    )


@register(outgoing=True, pattern=r"^\.aliveu")
async def amireallyaliveuser(username):
    """For .aliveu command, change the username in the .alive command."""
    message = username.text
    if message != ".aliveu" and message[7:8] == " ":
        newuser = message[8:]
        global DEFAULTUSER
        DEFAULTUSER = newuser
    await username.edit(f"**Юзер изменен на** `{newuser}`**!**")


@register(outgoing=True, pattern=r"^\.resetalive$")
async def amireallyalivereset(ureset):
    """For .resetalive command, reset the username in the .alive command."""
    global DEFAULTUSER
    DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else uname().node
    await ureset.edit("**Юзер сброшен!**")


CMD_HELP.update(
    {
        "sysd": ">`.sysd`" "\nПоказывает инфо с помощью неофетча.",
        "botver": ">`.botver`" "\nПоказывает версию юзербота.",
        "pip": ">`.pip <module(s)>`" "\nДелает поиск модулей пипа.",
        "alive": ">`.alive`"
        "\nПоказывает работу бота."
        "\n\n>`.aliveu <text>`"
        "\nМеняет имя юзера."
        "\n\n>`.resetalive`"
        "\nСбрасывает все до умолчаний.",
    }
)
