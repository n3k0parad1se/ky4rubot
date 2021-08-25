# Copyright (C) 2020 KenHV

from sqlalchemy.exc import IntegrityError

from userbot import CMD_HELP, bot
from userbot.events import register

fban_replies = [
    "Новый Фед-Бан",
    "Запускаю Фед-Бан",
    "Запуск Фед-Бана",
    "Обновление причины Фед-Бана",
    "Причина Фед-Бана обновлена",
    "уже забанен с такой причиной.",
]

unfban_replies = ["Новый Фед-Разбан", "Я дам", "Фед-Разбан"]


@register(outgoing=True, disable_edited=True, pattern=r"^\.(d)?fban(?: |$)(.*)")
async def fban(event):
    """Bans a user from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("**Запущен в режиме Non-SQL!**")

    match = event.pattern_match.group(2)

    if event.is_reply:
        reply_msg = await event.get_reply_message()
        fban_id = reply_msg.sender_id

        if event.pattern_match.group(1) == "d":
            await reply_msg.delete()

        reason = match
    else:
        pattern = match.split()
        fban_id = pattern[0]
        reason = " ".join(pattern[1:])

    try:
        fban_id = await event.client.get_peer_id(fban_id)
    except Exception:
        pass

    if event.sender_id == fban_id:
        return await event.edit(
            "**Это было не разрешено ботом.**"
        )

    fed_list = get_flist()
    if len(fed_list) == 0:
        return await event.edit("**Вы не подключены к федерации!**")

    user_link = f"[{fban_id}](tg://user?id={fban_id})"

    await event.edit(f"**Фед-блокирую** {user_link}...")
    failed = []
    total = 0

    for i in fed_list:
        total += 1
        chat = int(i.chat_id)
        try:
            async with bot.conversation(chat) as conv:
                await conv.send_message(f"/fban {user_link} {reason}")
                reply = await conv.get_response()
                await bot.send_read_acknowledge(
                    conv.chat_id, message=reply, clear_mentions=True
                )

                if not any(i in reply.text for i in fban_replies):
                    failed.append(i.fed_name)
        except Exception:
            failed.append(i.fed_name)

    reason = reason if reason else "Не указано."

    if failed:
        status = f"Не удалось забанить в {len(failed)}/{total} федерациях.\n"
        for i in failed:
            status += f"• {i}\n"
    else:
        status = f"Забанен в {total} федерациях."

    await event.edit(
        f"**Забанен **{user_link}!\n**Причина:** {reason}\n**Статус:** {status}"
    )


@register(outgoing=True, disable_edited=True, pattern=r"^\.unfban(?: |$)(.*)")
async def unfban(event):
    """Unbans a user from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("**Запущен в режиме Non-SQL!**")

    match = event.pattern_match.group(1)
    if event.is_reply:
        unfban_id = (await event.get_reply_message()).sender_id
        reason = match
    else:
        pattern = match.split()
        unfban_id = pattern[0]
        reason = " ".join(pattern[1:])

    try:
        unfban_id = await event.client.get_peer_id(unfban_id)
    except:
        pass

    if event.sender_id == unfban_id:
        return await event.edit("**Стоп, это не так работает**")

    fed_list = get_flist()
    if len(fed_list) == 0:
        return await event.edit("**Вы не подключены к федерации!**")

    user_link = f"[{unfban_id}](tg://user?id={unfban_id})"

    await event.edit(f"**Разбаниваю **{user_link}**...**")
    failed = []
    total = 0

    for i in fed_list:
        total += 1
        chat = int(i.chat_id)
        try:
            async with bot.conversation(chat) as conv:
                await conv.send_message(f"/unfban {user_link} {reason}")
                reply = await conv.get_response()
                await bot.send_read_acknowledge(
                    conv.chat_id, message=reply, clear_mentions=True
                )

                if not any(i in reply.text for i in unfban_replies):
                    failed.append(i.fed_name)
        except Exception:
            failed.append(i.fed_name)

    reason = reason if reason else "Не указано."

    if failed:
        status = f"Не удалось разбанить {len(failed)}/{total} федерациях.\n"
        for i in failed:
            status += f"• {i}\n"
    else:
        status = f"Разбанено в {total} федерациях."

    reason = reason if reason else "Не указано."
    await event.edit(
        f"**Разбанен** {user_link}!\n**Причина:** {reason}\n**Статус:** {status}"
    )


@register(outgoing=True, pattern=r"^\.addf(?: |$)(.*)")
async def addf(event):
    """Adds current chat to connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import add_flist
    except IntegrityError:
        return await event.edit("**Запущен в режиме Non-SQL!**")

    fed_name = event.pattern_match.group(1)
    if not fed_name:
        return await event.edit("**Дайте имя чтобы присоеденится!**")

    try:
        add_flist(event.chat_id, fed_name)
    except IntegrityError:
        return await event.edit(
            "**Эта группа уже подключена к федерации.**"
        )

    await event.edit("**Эта группа добавлена в список федерации!**")


@register(outgoing=True, pattern=r"^\.delf$")
async def delf(event):
    """Removes current chat from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import del_flist
    except IntegrityError:
        return await event.edit("**Запущен в режиме Non-SQL!**")

    del_flist(event.chat_id)
    await event.edit("**Удалена эта группа из списка федерации!**")


@register(outgoing=True, pattern=r"^\.listf$")
async def listf(event):
    """List all connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import get_flist
    except IntegrityError:
        return await event.edit("**Запущен в режиме Non-SQL!**")

    fed_list = get_flist()
    if len(fed_list) == 0:
        return await event.edit("**Вы не подключены к федерации!**")

    msg = "**Подключенные федерации:**\n\n"

    for i in fed_list:
        msg += f"• {i.fed_name}\n"

    await event.edit(msg)


@register(outgoing=True, disable_edited=True, pattern=r"^\.clearf$")
async def clearf(event):
    """Removes all chats from connected federations."""
    try:
        from userbot.modules.sql_helper.fban_sql import del_flist_all
    except IntegrityError:
        return await event.edit("**Запущен в режиме Non-SQL!**")

    del_flist_all()
    await event.edit("**Отключен от всех федераций!**")


CMD_HELP.update(
    {
        "fban": ">`.fban <id/username> <reason>`"
        "\nБанит юзера в федерации."
        "\nВы можете реплайнуть, или указать юзернейм/айди."
        "\n`.dfban` делает то же самое, но удаляет сообщение."
        "\n\n`>.unfban <id/username> <reason>`"
        "\nРазбанивает юзера"
        "\n\n>`.addf <name>`"
        "\nДобавляет группу и держит как <name> в федерациях."
        "\nОдной группы достаточно для одной федерации."
        "\n\n>`.delf`"
        "\nУдаляет группу из федерации."
        "\n\n>`.listf`"
        "\nСписок всех подключенных федераций."
        "\n\n>`.clearf`"
        "\nОтключается от всех федераций."
    }
)
