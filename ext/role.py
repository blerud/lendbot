import logging
import random

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


@commands.group()
async def role(ctx):
    if ctx.message.content.strip() == '.role':
        await ctx.send(
            '''```.role create [role]
.role list
.role rename [role] [newrole]
.role delete [role]
.role listusers [role]
.role addusers [role] [users]...
.role delusers [role] [users]...```'''
        )


@role.command(name='list')
async def list0(ctx):
    guild = ctx.guild
    if guild is not None:
        msg = 'Roles in this server:\n```'
        for role in guild.roles:
            if role.name == '@everyone':
                continue
            msg += role.name + '\n'
        msg += '```'
        await ctx.send(msg)


@role.command(name='create')
async def create_role(ctx, role: str):
    guild = ctx.guild

    try:
        await guild.create_role(name=role, mentionable=True, colour=discord.Colour(0).from_hsv(random.random(), 0.6, 0.7))
        await ctx.send('Created role \"{}\"'.format(role))
    except Exception as e:
        log.warning('failed create role \"%s\", %s', role, str(e))


@role.command(name='rename')
async def rename_role(ctx, role: discord.Role, newrole: str):
    oldrole = role.name

    try:
        await role.edit(name=newrole)
        await ctx.send('Renamed role \"{}\" to \"{}\"'.format(oldrole, newrole))
    except Exception as e:
        log.warning('failed edit role \"%s\" to \"%s\", %s', role, newrole, str(e))


@role.command(name='delete')
async def delete_role(ctx, role: discord.Role):
    try:
        for member in role.members:
            await member.remove_roles(role)
        await role.delete()
        await ctx.send('Deleted role \"{}\"'.format(role))
    except Exception as e:
        log.warning('failed delete role \"%s\", %s', role, str(e))


@role.command(name='listusers')
async def list_users(ctx, role: discord.Role):
    try:
        members = list(map(lambda x: x.nick if x.nick is not None else x.name, role.members))
        await ctx.send('Users in role \"{}\": {}'.format(role, ', '.join(members)))
    except Exception as e:
        log.warning('failed retrieve users of role \"%s\"', role, str(e))


@role.command(name='addusers')
async def add_users(ctx, role: discord.Role, members: commands.Greedy[discord.Member]):
    try:
        for member in members:
            await member.add_roles(role)
        await ctx.send('Added users {} to \"{}\"'.format(list(map(lambda x: x.name, members)), role))
    except Exception as e:
        log.warning('failed add role \"%s\" to %d members, %s', role, len(members), str(e))


@role.command(name='delusers')
async def del_users(ctx, role: discord.Role, members: commands.Greedy[discord.Member]):
    try:
        for member in members:
            await member.remove_roles(role)
        await ctx.send('Removed users {} from \"{}\"'.format(list(map(lambda x: x.name, members)), role))
    except Exception as e:
        log.warning('failed remove role \"%s\" from %d members, %s', role, len(members), str(e))


def setup(bot):
    bot.add_command(role)
