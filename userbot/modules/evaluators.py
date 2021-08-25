# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
"""Userbot module for executing code and terminal commands from Telegram."""

import asyncio
import sys
from io import StringIO
from os import remove
from traceback import format_exc

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern=r"^\.eval(?: |$|\n)([\s\S]*)")
async def evaluate(event):
    """For .eval command, evaluates the given Python expression."""
    expression = event.pattern_match.group(1)
    if not expression:
        return await event.edit("**Дайте мне выражение для оценки.**")

    if expression in ("userbot.session", "config.env"):
        return await event.edit("**Это опасная операция, не разрешено!**")

    await event.edit("**Обработка...**")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc, returned = None, None, None, None

    async def aexec(code, event):
        head = "async def __aexec(event):\n "
        code = "".join(f"\n {line}" for line in code.split("\n"))
        exec(head + code)  # pylint: disable=exec-used
        return await locals()["__aexec"](event)

    try:
        returned = await aexec(expression, event)
    except Exception:  # pylint: disable=broad-except
        exc = format_exc()

    stdout = redirected_output.getvalue().strip()
    stderr = redirected_error.getvalue().strip()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    expression.encode("unicode-escape").decode().replace("\\\\", "\\")

    evaluation = str(exc or stderr or stdout or returned)
    if evaluation and evaluation != "":
        evaluation = evaluation.encode("unicode-escape").decode().replace("\\\\", "\\")
    else:
        evaluation = "None"

    if len(str(evaluation)) >= 4096:
        with open("output.txt", "w+") as file:
            file.write(evaluation)
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
            caption="**Слишком большой вывод, отправляю файлом...**",
        )
        return remove("output.txt")
    await event.edit(f"**Запрос:**\n`{expression}`\n\n**Результат:**\n`{evaluation}`")


@register(outgoing=True, pattern=r"^\.exec(?: |$|\n)([\s\S]*)")
async def run(event):
    """For .exec command, which executes the dynamically created program"""
    code = event.pattern_match.group(1)
    if not code:
        return await event.edit("**Почитайте** `.help exec` **для примера.**")

    if code in ("userbot.session", "config.env"):
        return await event.edit("**Опасная операция, не разрешено!**")

    await event.edit("**Обработка...**")
    if len(code.splitlines()) <= 5:
        codepre = code
    else:
        clines = code.splitlines()
        codepre = (
            clines[0] + "\n" + clines[1] + "\n" + clines[2] + "\n" + clines[3] + "..."
        )

    command = "".join(f"\n {l}" for l in code.split("\n.strip()"))
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        command.strip(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    codepre.encode("unicode-escape").decode().replace("\\\\", "\\")

    stdout, _ = await process.communicate()
    if stdout and stdout != "":
        stdout = str(stdout.decode().strip())
        stdout.encode("unicode-escape").decode().replace("\\\\", "\\")
    else:
        stdout = "None"

    if len(stdout) > 4096:
        with open("output.txt", "w+") as file:
            file.write(stdout)
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
            caption="**Большой вывод, отправляю файлом...**",
        )
        return remove("output.txt")
    await event.edit(f"**Запрос:**\n`{codepre}`\n\n**Результат:**\n`{stdout}`")


@register(outgoing=True, pattern=r"^\.term(?: |$|\n)([\s\S]*)")
async def terminal_runner(event):
    """For .term command, runs bash commands and scripts on your server."""
    command = event.pattern_match.group(1)

    if not command:
        return await event.edit("**Дайте команду или воспользуйтесь .help term для примера.**")

    if command in ("userbot.session", "config.env"):
        return await event.edit("**Опасная операция, не разрешено!**")

    await event.edit("**Обработка...**")
    process = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    command.encode("unicode-escape").decode().replace("\\\\", "\\")

    stdout, _ = await process.communicate()
    if stdout and stdout != "":
        result = str(stdout.decode().strip())
        result.encode("unicode-escape").decode().replace("\\\\", "\\")
    else:
        result = "None"

    if len(result) > 4096:
        with open("output.txt", "w+") as output:
            output.write(result)
        await event.client.send_file(
            event.chat_id,
            "output.txt",
            reply_to=event.id,
            caption="**Вывод большой, отправляю файлом...**",
        )
        return remove("output.txt")

    await event.edit(f"**Команда:**\n`{command}`\n\n**Результат:**\n`{result}`")


CMD_HELP.update(
    {
        "eval": "`.eval <cmd>`\n"
        "`.eval return 2 + 3`\n"
        "`.eval print(event)`\n"
        "`.eval await event.reply('Ender')`\n"
        "\nЗапускает скрипт python.",
        "exec": "`.exec print('hello')`"
        "\nЗапускает маленькие скрипты.",
        "term": "`.term <cmd>`\n"
        "bash-команды на сервере юзербота.",
    }
)
