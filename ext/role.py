import logging
import random
import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    role = discord.SlashCommandGroup(name='role', description='Manage roles')

    @role.command(name='list', description='List all roles in the server')
    async def list_roles(self, ctx):
        guild = ctx.guild
        if guild is not None:
            msg = 'Roles in this server:\n```\n'
            for role in guild.roles:
                if role.name == '@everyone':
                    continue
                msg += role.name + '\n'
            msg += '```'
            await ctx.respond(msg)

    @role.command(name='create', description='Create a new role')
    async def create_role(self, ctx, *, role: str):
        guild = ctx.guild
        try:
            await guild.create_role(name=role, mentionable=True, colour=discord.Colour(0).from_hsv(random.random(), 0.6, 0.7))
            await ctx.respond(f'Created role "{role}"')
        except Exception as e:
            log.warning('Failed to create role "%s", %s', role, str(e))
            await ctx.respond(f'Failed to create role "{role}"')

    @role.command(name='rename', description='Rename a role')
    async def rename_role(self, ctx, role: discord.Role, *, newrole: str):
        oldrole = role.name
        try:
            await role.edit(name=newrole)
            await ctx.respond(f'Renamed role "{oldrole}" to "{newrole}"')
        except Exception as e:
            log.warning('Failed to rename role "%s" to "%s", %s', role, newrole, str(e))
            await ctx.respond(f'Failed to rename role "{oldrole}"')

    @role.command(name='delete', description='Delete a role')
    async def delete_role(self, ctx, *, role: discord.Role):
        try:
            await role.delete()
            await ctx.respond(f'Deleted role "{role}"')
        except Exception as e:
            log.warning('Failed to delete role "%s", %s', role, str(e))
            await ctx.respond(f'Failed to delete role "{role}"')

    @role.command(name='listusers', description='List users with a specific role')
    async def list_users(self, ctx, *, role: discord.Role):
        try:
            members = [member.mention for member in role.members]
            await ctx.respond(f'Users with the role "{role}": {", ".join(members)}')
        except Exception as e:
            log.warning('Failed to retrieve users with the role "%s", %s', role, str(e))
            await ctx.respond(f'Failed to retrieve users with the role "{role}"')

    @role.command(name='adduser', description='Add user to a role')
    async def add_user(self, ctx, role: discord.Role, member: discord.Member):
        try:
            await member.add_roles(role)
            await ctx.respond(f'Added {member.name} to the role "{role}"')
        except Exception as e:
            log.warning('Failed to add user to the role "%s", %s', role, str(e))
            await ctx.respond(f'Failed to add {member.name} to the role "{role}"')

    @role.command(name='deluser', description='Remove user from a role')
    async def del_user(self, ctx, role: discord.Role, member: discord.Member):
        try:
            await member.remove_roles(role)
            await ctx.respond(f'Removed {member.name} from the role "{role}"')
        except Exception as e:
            log.warning('Failed to remove user from the role "%s", %s', role, str(e))
            await ctx.respond(f'Failed to remove {member.name} from the role "{role}"')


def setup(bot):
    bot.add_cog(RoleCommands(bot))
