# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#

import aiohttp

from userbot import CMD_HELP
from userbot.events import register

GIT_TEMP_DIR = "./userbot/temp/"


@register(outgoing=True, pattern=r"\.git(?: |$)(.*)")
async def github(event):
    URL = f"https://api.github.com/users/{event.pattern_match.group(1)}"
    await event.get_chat()
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as request:
            if request.status == 404:
                await event.reply("`" + event.pattern_match.group(1) + " не найден`")
                return

            result = await request.json()

            url = result.get("html_url", None)
            name = result.get("name", None)
            company = result.get("company", None)
            bio = result.get("bio", None)
            created_at = result.get("created_at", "Не найдено")

            REPLY = f"GitHub инфо для `{event.pattern_match.group(1)}`\
            \nЮзернейм: `{name}`\
            \nБио: `{bio}`\
            \nURL: {url}\
            \nКомпания: `{company}`\
            \nСоздан: `{created_at}`\
            \nБольше : [Тут](https://api.github.com/users/{event.pattern_match.group(1)}/events/public)"

            if not result.get("repos_url", None):
                await event.edit(REPLY)
                return
            async with session.get(result.get("repos_url", None)) as request:
                result = request.json
                if request.status == 404:
                    await event.edit(REPLY)
                    return

                result = await request.json()

                REPLY += "\nРепозитории:\n"

                for nr in range(len(result)):
                    REPLY += f"[{result[nr].get('name', None)}]({result[nr].get('html_url', None)})\n"

                await event.edit(REPLY)


CMD_HELP.update({"github": "`.git`" "\nКак .whois но для гитхаба."})
