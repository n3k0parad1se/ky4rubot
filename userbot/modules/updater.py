# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
# credits to @AvinashReddy3108
#
"""
This module updates the userbot based on upstream revision
"""

import asyncio
import sys
from os import environ, execle, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userbot import (
    CMD_HELP,
    HEROKU_API_KEY,
    HEROKU_APP_NAME,
    UPSTREAM_REPO_BRANCH,
    UPSTREAM_REPO_URL,
)
from userbot.events import register


async def gen_chlog(repo, diff):
    d_form = "%d/%m/%y"
    return "".join(
        f"- {c.summary} ({c.committed_datetime.strftime(d_form)}) <{c.author}>\n"
        for c in repo.iter_commits(diff)
    )


async def print_changelogs(event, ac_br, changelog):
    changelog_str = (
        f"**Обновления найдены в {ac_br} разделе!\n\nЧейнджлог:**\n`{changelog}`"
    )
    if len(changelog_str) > 4096:
        await event.edit("**Чейнджлог слишком большой, отправляю файлом.**")
        with open("output.txt", "w+") as file:
            file.write(changelog_str)
        await event.client.send_file(event.chat_id, "output.txt")
        remove("output.txt")
    else:
        await event.client.send_message(event.chat_id, changelog_str)
    return True


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is not None:
        import heroku3

        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if HEROKU_APP_NAME is None:
            await event.edit(
                "**Установите** `HEROKU_APP_NAME` **переменную"
                " чтобы успешно деплойнуть юзербота.**"
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                f"{txt}\n" "**Невалидный хероку для деплоя.**"
            )
            return repo.__del__()
        try:
            from userbot.modules.sql_helper.globals import addgvar, delgvar

            delgvar("restartstatus")
            addgvar("restartstatus", f"{event.chat_id}\n{event.id}")
        except AttributeError:
            pass
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@"
        )
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except Exception as error:
            await event.edit(f"{txt}\nHere is the error log:\n`{error}`")
            return repo.__del__()
        build = heroku_app.builds(order_by="created_at", sort="desc")[0]
        if build.status == "failed":
            await event.edit("**Ошибка!**\nОтменен из-за ошибок.`")
            await asyncio.sleep(5)
            return await event.delete()
        await event.edit(
            "**Обновление успешно!**\nБот перезапустится через несколько секунд."
        )

    else:
        await event.edit("**Установите** `HEROKU_API_KEY` **переменную.**")
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await event.edit(
        "**Обновление успешно!**\nБот перезапустится через несколько секунд."
    )

    try:
        from userbot.modules.sql_helper.globals import addgvar, delgvar

        delgvar("restartstatus")
        addgvar("restartstatus", f"{event.chat_id}\n{event.id}")
    except AttributeError:
        pass

    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)


@register(outgoing=True, pattern=r"^\.update( now| deploy|$)")
async def upstream(event):
    "Для команды .update проверьте или бот работает на свежих версиях"
    await event.edit("**Проверка обновлений...**")
    conf = event.pattern_match.group(1).strip()
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    try:
        txt = "**Не могу продолжить из-за "
        txt += "проблем**\n`LOGTRACE:`\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f"{txt}\n**Директория** `{error}` **не найдена.**")
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f"{txt}\n**Ошибка!** `{error}`")
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"**Директория {error} "
                "не гит репозиторий.\n"
                "Мы можем это исправить с помощью **"
                "`.update now.`"
            )
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        force_update = True
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit(
            f"**У вас кастомный раздел: ({ac_br}). \n"
            "Поменяйте с ** `master` на **branch.**"
        )
        return repo.__del__()
    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    """ - Special case for deploy - """
    if conf == "deploy":
        await event.edit(
            "**Выполняется полное обновление...**\nЭто займет время."
        )
        await deploy(event, repo, ups_rem, ac_br, txt)
        return

    if changelog == "" and not force_update:
        await event.edit(
            f"**Юзербот последней версии с `{UPSTREAM_REPO_BRANCH}`!**"
        )
        return repo.__del__()

    if conf == "" and not force_update:
        await print_changelogs(event, ac_br, changelog)
        await event.delete()
        return await event.respond("**Пропишите** `.update deploy` **для обновления.**")

    if force_update:
        await event.edit(
            "**Синхронизация до последнего стабильного кода...**"
        )

    if conf == "now":
        for commit in changelog.splitlines():
            if commit.startswith("- [NQ]"):
                if HEROKU_APP_NAME is not None and HEROKU_API_KEY is not None:
                    return await event.edit(
                        "**Быстрое обновления отключено; "
                        "используйте** `.update deploy` ****"
                    )
        await event.edit("**Выполняется быстрое обновление, подождите...**")
        await update(event, repo, ups_rem, ac_br)

    return


CMD_HELP.update(
    {
        "update": ">`.update`"
        "\nПроверяет обновления "
        "и показывает список изменений."
        "\n\n>`.update now`"
        "\nДелает быстрое обновление."
        "\nHeroku сбрасывает этот метод. Используйте `deploy` тогда."
        "\n\n>`.update deploy`"
        "\nДелает полное обновление (рекомендуется)."
    }
)
