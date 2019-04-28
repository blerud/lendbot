import discord
from discord.ext import commands
import logging

log = logging.getLogger(__name__)

@commands.group()
async def role(ctx):
    if ctx.message.content.strip() == '.role':
        await ctx.send('''```.role create [role]
.role rename [role] [newrole]
.role delete [role]
.role addusers [role] [users]...
.role delusers [role] [users]...```''')

@role.command(name='create')
async def create_role(ctx, role: str):
    guild = ctx.guild

    try:
        await guild.create_role(name=role, mentionable=True)
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
