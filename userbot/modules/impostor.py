from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto

from userbot import CMD_HELP, LOGS, STORAGE, bot
from userbot.events import register

if not hasattr(STORAGE, "userObj"):
    STORAGE.userObj = False


@register(outgoing=True, pattern=r"^\.impostor ?(.*)")
async def impostor(event):
    inputArgs = event.pattern_match.group(1)

    if "restore" in inputArgs:
        await event.edit("**Возвращаю свою личность...**")
        if not STORAGE.userObj:
            return await event.edit(
                "**Вам нужно персонализировать профиль перед откатом!**"
            )
        await updateProfile(STORAGE.userObj, restore=True)
        return await event.edit("**Круто когда все свое!**")
    if inputArgs:
        try:
            user = await event.client.get_entity(inputArgs)
        except:
            return await event.edit("**Неверный юзернейс/ID.**")
        userObj = await event.client(GetFullUserRequest(user))
    elif event.reply_to_msg_id:
        replyMessage = await event.get_reply_message()
        if replyMessage.sender_id is None:
            return await event.edit("**Не могу украсть анонимного админа.**")
        userObj = await event.client(GetFullUserRequest(replyMessage.sender_id))
    else:
        return await event.edit("**Введите** `.help impostor` **чтобы понять как его использовать.**")

    if not STORAGE.userObj:
        STORAGE.userObj = await event.client(GetFullUserRequest(event.sender_id))

    LOGS.info(STORAGE.userObj)

    await event.edit("**Краду профиль этого человека...**")
    await updateProfile(userObj)
    await event.edit("**Я это ты, и ты это я.**")


async def updateProfile(userObj, restore=False):
    firstName = (
        "Deleted Account"
        if userObj.user.first_name is None
        else userObj.user.first_name
    )
    lastName = "" if userObj.user.last_name is None else userObj.user.last_name
    userAbout = userObj.about if userObj.about is not None else ""
    userAbout = "" if len(userAbout) > 70 else userAbout
    if restore:
        userPfps = await bot.get_profile_photos("me")
        userPfp = userPfps[0]
        await bot(
            DeletePhotosRequest(
                id=[
                    InputPhoto(
                        id=userPfp.id,
                        access_hash=userPfp.access_hash,
                        file_reference=userPfp.file_reference,
                    )
                ]
            )
        )
    else:
        try:
            userPfp = userObj.profile_photo
            pfpImage = await bot.download_media(userPfp)
            await bot(UploadProfilePhotoRequest(await bot.upload_file(pfpImage)))
        except BaseException:
            pass
    await bot(
        UpdateProfileRequest(about=userAbout, first_name=firstName, last_name=lastName)
    )


CMD_HELP.update(
    {
        "impostor": ">`.impostor` (as a reply to a message of a user)\
    \nКрадет личность юзера.\
    \n\n>`.impostor <username/ID>`\
    \nКрадет личность юзера.\
    \n\n>`.impostor restore`\
    \nВозвращает назад.\
    \n\n**Возвращайте перед следующим запуском.**\
"
    }
)
