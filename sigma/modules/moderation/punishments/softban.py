# Apex Sigma: The Database Giant Discord Bot.
# Copyright (C) 2017  Lucia's Cipher
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import arrow
import discord

from sigma.core.mechanics.command import SigmaCommand
from sigma.core.utilities.data_processing import user_avatar
from sigma.core.utilities.event_logging import log_event
from sigma.core.utilities.permission_processing import hierarchy_permit


def generate_log_embed(message, target, reason):
    log_response = discord.Embed(color=0x696969, timestamp=arrow.utcnow().datetime)
    log_response.set_author(name=f'A User Has Been Soft-Banned', icon_url=user_avatar(target))
    log_response.add_field(name='🔩 Soft-Banned User',
                           value=f'{target.mention}\n{target.name}#{target.discriminator}', inline=True)
    author = message.author
    log_response.add_field(name='🛡 Responsible',
                           value=f'{author.mention}\n{author.name}#{author.discriminator}', inline=True)
    log_response.add_field(name='📄 Reason', value=f"```\n{reason}\n```", inline=False)
    log_response.set_footer(text=f'UserID: {target.id}')
    return log_response


async def softban(cmd: SigmaCommand, message: discord.Message, args: list):
    if message.author.permissions_in(message.channel).ban_members:
        if message.mentions:
            target = message.mentions[0]
            if cmd.bot.user.id != target.id:
                if message.author.id != target.id:
                    above_hier = hierarchy_permit(message.author, target)
                    is_admin = message.author.permissions_in(message.channel).administrator
                    if above_hier or is_admin:
                        above_me = hierarchy_permit(message.guild.me, target)
                        if above_me:
                            if len(args) > 1:
                                reason = ' '.join(args[1:])
                            else:
                                reason = 'No reason stated.'
                            response = discord.Embed(color=0x696969, title=f'🔩 The user has been soft-banned.')
                            response_title = f'{target.name}#{target.discriminator}'
                            response.set_author(name=response_title, icon_url=user_avatar(target))
                            to_target = discord.Embed(color=0x696969)
                            to_target.add_field(name='🔩 You have been soft-banned.', value=f'Reason: {reason}')
                            to_target.set_footer(text=f'From: {message.guild.name}.', icon_url=message.guild.icon_url)
                            try:
                                await target.send(embed=to_target)
                            except discord.Forbidden:
                                pass
                            await target.ban(reason=f'By {message.author.name}: {reason} (Soft)')
                            await target.unban()
                            log_embed = generate_log_embed(message, target, reason)
                            await log_event(cmd.bot, message.guild, cmd.db, log_embed, 'LogBans')
                        else:
                            response = discord.Embed(title='⛔ Target is above my highest role.', color=0xBE1931)
                    else:
                        response = discord.Embed(title='⛔ Can\'t soft-ban someone equal or above you.', color=0xBE1931)
                else:
                    response = discord.Embed(color=0xBE1931, title='❗ You can\'t soft-ban yourself.')
            else:
                response = discord.Embed(color=0xBE1931, title='❗ I can\'t soft-ban myself.')
        else:
            response = discord.Embed(color=0xBE1931, title='❗ No user targeted.')
    else:
        response = discord.Embed(title='⛔ Access Denied. Ban permissions needed.', color=0xBE1931)
    await message.channel.send(embed=response)
