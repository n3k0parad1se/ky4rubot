# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
""" Userbot module for having some fun with people. """

from asyncio import sleep
from random import choice, getrandbits, randint
from re import sub

import requests
from cowpy import cow

from userbot import CMD_HELP
from userbot.events import register
from userbot.modules.admin import get_user_from_event

# ================= CONSTANT =================


RUSHATE = [
    "Runs to Thanos..",
    "Runs far, far away from earth..",
]

ENGHATE = [
    "Where do you think you're going?",
    "Huh? what? did they get away?",
]



@register(outgoing=True, pattern=r"^\.ruhate$")
async def haterus(ruh):
    """Ya tboyu matb ebal"""
    await ruh.edit(choice(RUSHATE))


@register(outgoing=True, pattern=r"^\.enhate$")
async def hateen(enh):
    """Fuck you mom"""
    await enh.edit(choice(ENGHATE))


CMD_HELP.update(
    {
        "hatebot": ".ruhate\
\nUsage: hates mom in russian.\
\n\n.enhate\
\nUsage: hates mom in english\
"
    }
)
