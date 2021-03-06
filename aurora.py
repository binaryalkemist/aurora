#  Copyright © 2018, 2019 James M. Ivey <james@binaryalkemist.net>
#  Portions Copyright © 2018 EvieePy (https://github.com/EvieePy) Licensed under the MIT License
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import tools
import asyncio
import json
import aiohttp
import datetime
import discord
from discord.ext import commands
import logging
import wmi
import tailer

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='[%H:%M:%S]')
log = logging.getLogger()
log.setLevel(logging.INFO)
latest_adm = ''


async def log_monitor():
    log_name = 'DayZServer_x64.ADM'
    log.info("Watching DayZServer_x64.ADM")
    await adm_scan(log_name)


async def adm_scan(log_name):
    log_file = open(log_name)
    log_file.seek(0, 2)  # Go to the end of the file
    while True:
        line = log_file.readline()
        if not line:
            await asyncio.sleep(0.1)  # Sleep briefly
            continue
        if 'is connected' in line:
            parsed = line.split(' ')
            if '"' in parsed[3] and '"' in parsed[4]:
                player = parsed[3] + ' ' + parsed[4]
                index = 4
            else:
                player = parsed[3]
                index = 3
            player = player.strip('"')
            id = parsed[index + 3]
            id = id.strip('(id=')
            id = id.strip(')')
            time = parsed[0]
            channel = bot.get_channel(int(live_feed_channel))
            live_connect = f'```CONNECT: {time} \nPlayer: {player} \nBUID: {id}```'
            await channel.send(live_connect)
        if 'died' in line:
            parsed = line.split(' ')
            if '"' in parsed[3] and '"' in parsed[4]:
                player = parsed[3] + ' ' + parsed[4]
                index = 4
            else:
                player = parsed[3]
                index = 3
            player = player.strip('"')
            id = parsed[index + 1]
            id = id.strip('(id=')
            id = id.strip(')')
            pos_x = parsed[index + 2].strip('pos=<')
            pos_x = pos_x.strip(',')
            pos_y = parsed[index + 3].strip(',')
            pos_z = parsed[index + 4].strip('>)')
            time = parsed[0]
            water = parsed[index + 8]
            energy = parsed[index + 10]
            bleed_sources = parsed[index + 13]
            channel = bot.get_channel(int(live_feed_channel))
            live_feed = f'```DEATH: {time} \nPlayer: {player} \nBUID: {id} \nPos: <{pos_x}, {pos_y}, {pos_z}>\nWater: {water}\nEnergy: {energy}\nBleed Sources: {bleed_sources}```'
            await channel.send(live_feed)
            log.info("Death: %s" %line)
        if 'disconnected' in line:
            log.info("Disconnection: %s" %line)
        if 'suicide' in line:
            log.info("Suicide: %s" %line)
        if 'hit' in line:
            log.info("HIT: %s" %line)
        if 'killed' in line:
            parsed = line.split(' ')
            if '"' in parsed[3] and '"' in parsed[4]:
                player = parsed[3] + ' ' + parsed[4]
                if '"' in parsed[12] and '"' in parsed[13]:
                    killer = parsed[12] + ' ' + parsed[13]
                    buid_player = str(parsed[5])
                    buid_player = buid_player.strip('(id=')
                    buid_player = buid_player.strip(')')
                    buid_killer = str(parsed[14])
                    buid_killer = buid_killer.replace('(id=', '')
                    buid_killer = buid_killer.replace(')', '')
                    player = player.replace('"', '')
                    killer = killer.replace('"', '')
                    pos_x_player = parsed[6].replace('pos=<', '')
                    pos_x_player = pos_x_player.replace(',', '')
                    pos_y_player = parsed[7].replace(',', '')
                    pos_z_player = parsed[8].replace('>)', '')
                    pos_x_killer = parsed[15].replace('pos=<', '')
                    pos_x_killer = pos_x_killer.replace(',', '')
                    pos_y_killer = parsed[16].replace(',', '')
                    pos_z_killer = parsed[17].replace('>)', '')
                    weapon = parsed[19:]
                    time = parsed[0]
                    channel = bot.get_channel(int(live_feed_channel))
                    await channel.send("```{} | Player {} BUID {} Position {},{},{} KILLED\nby Player {} BUID {} Position <{}, {}, {}>) with {}```".format(time, player, buid_player, pos_x_player, pos_y_player, pos_z_player, killer, buid_killer, pos_x_killer, pos_y_killer, pos_z_killer, weapon))
            else:
                player = parsed[3]
                player = player.replace('"', '')
                id = parsed[4]
                id = id.replace('(id=', '')
                id = id.replace(')', '')
                pos_x = parsed[5].replace('pos=<', '')
                pos_x = pos_x.replace(',', '')
                pos_y = parsed[6].replace(',', '')
                pos_z = parsed[7].replace('>)', '')
                time = parsed[0]
                water = parsed[11]
                energy = parsed[13]
                bleed_sources = parsed[16]
                channel = bot.get_channel(int(live_feed_channel))
                await channel.send("```DEATH: {} \nPlayer: {} \nBUID: {} \nPos: <{}, {}, {}>\nWater: {}\nEnergy: {}\nBleed Sources: {}```".format(time, player, id, pos_x, pos_y, pos_z, water, energy, bleed_sources))
            log.info("Killed: %s" %line)

global api_count
global startup_time
startup_time = datetime.datetime.now()
headers = {'contentType': 'application/x-www-form-urlencoded','User-Agent': 'CFTools ServiceAPI-Client'}

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='[%H:%M:%S]')
log = logging.getLogger()
log.setLevel(logging.INFO)

with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    token = config_data['discord_token']
    report_channel = config_data['report_channel']
    api_url = config_data['api_url']
    guild_id = config_data['guild_id']
    status_refresh = config_data['status_refresh']
    delayed_refresh = config_data['delayed_refresh']
    activity_rotate = config_data['activity_rotate']
    activity_refresh = config_data['activity_refresh']
    cooldown_channel = config_data['cooldown_channel']
    cooldown_user = config_data['cooldown_user']
    staff_role = tuple(config_data['permissions']['staff'])
    moderator_role = tuple(config_data['permissions']['moderators'])
    admin_role = tuple(config_data["permissions"]["admins"])
    live_feed_channel = config_data['live_feed_channel']

server_list = []
api_count = 0


class Server(object):
    def __init__(self, name=None, address=None, server_url=None, service_api_key=None, service_id=None, server_icon=None, info=None, players=None, kills=None, playtime=None, last_update=None):
        self.name = name
        self.address = address
        self.server_url = server_url
        self.service_api_key = service_api_key
        self.service_id = service_id
        self.server_icon = server_icon
        self.info = info
        self.players = players
        self.kills = kills
        self.playtime = playtime
        self.last_update = last_update


async def fetch_api(session, url, data):
    try:
        async with session.post(url, data=data, headers=headers) as response:
            api_data = await response.json()
            return api_data
    except Exception as error:
        log.info('API Fetch Failed: ' + str(error))


async def leaderboard_fetch_async():
    while True:
        tasks = []
        try:
            global api_count
            async with aiohttp.ClientSession() as session:
                for server in server_list:
                    tasks.append(fetch_api(session, "{}stats/{}".format(api_url, server.service_id),
                                           {'service_api_key': str(server.service_api_key), 'order': 'descending',
                                            'stat_type': 'kills'}))
                    tasks.append(fetch_api(session, "{}stats/{}".format(api_url, server.service_id),
                                           {'service_api_key': str(server.service_api_key), 'order': 'descending',
                                            'stat_type': 'playtime'}))
                    api_count += 2
                results = await asyncio.gather(*tasks)
                sub_list = [results[n:n + 2] for n in range(0, len(results), 2)]
                index = 0
                for api_return in sub_list:
                    server = server_list[index]
                    server.kills = api_return[0]
                    server.playtime = api_return[1]
                    index += 1
            await session.close()
            await asyncio.sleep(delayed_refresh)
        except Exception as error:
            log.info('API Fetch Failed:' + str(error))


async def debug_log_api():
    global api_count
    while True:
        log.info("API Count: {}".format(api_count))
        await asyncio.sleep(60)


async def status_fetch_async():
    while True:
        tasks = []
        try:
            global api_count
            async with aiohttp.ClientSession() as session:
                for server in server_list:
                    tasks.append(
                        fetch_api(session, "{}serverinfo/{}".format(api_url, server.service_id),
                                  {'service_api_key': str(server.service_api_key)}))
                    tasks.append(
                        fetch_api(session, "{}playerlist/{}".format(api_url, server.service_id),
                                  {'service_api_key': str(server.service_api_key)}))
                    api_count += 2
                results = await asyncio.gather(*tasks)
                sub_list = [results[n:n + 2] for n in range(0, len(results), 2)]
                index = 0
                for api_return in sub_list:
                    server = server_list[index]
                    server.info = api_return[0]
                    server.players = api_return[1]
                    index += 1
            await session.close()
            await asyncio.sleep(status_refresh)  # task runs every 60 seconds
        except Exception as error:
            log.info('API Fetch Failed:' + str(error))


async def initialize_servers():
    server_list.clear()
    for server in config_data.get('server', []):
        update = Server()
        update.name = server['name']
        update.address = server['address']
        update.server_url = server['server_url']
        update.service_api_key = server['service_api_key']
        update.service_id = server['service_id']
        update.server_icon = server['server_icon']
        server_list.append(update)
    bot.loop.create_task(status_fetch_async())
    bot.loop.create_task(leaderboard_fetch_async())



bot = commands.Bot(command_prefix='!', description='Aurora - The DayZ Discord Bot')
bot.add_cog(tools.CommandErrorHandler(bot))


@bot.event
async def on_ready():
    global startup_time
    await initialize_servers()
    activity = discord.Game(name="!help for help")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    bot_info = await bot.application_info()
    log.info("Aurora Discord Bot\nName: {}\nID: {}\nDescription: {}\nOwner: {}\nPublic: {}".format(bot_info.name,bot_info.id,bot_info.description,bot_info.owner,bot_info.bot_public))
    startup_time = datetime.datetime.now()
    log.info("Bot Connected")
    log.info("Initial API Init: {} calls".format(api_count))
    log.info("SERVERINFO/PLAYERLIST Update: every {} seconds".format(status_refresh))
    log.info("STATS Update: every {} seconds".format(delayed_refresh))
    await asyncio.sleep(10)
    bot.loop.create_task(rotate_activity())
    bot.loop.create_task(debug_log_api())
    bot.loop.create_task(log_monitor())
    computer = wmi.WMI()
    computer_info = computer.Win32_ComputerSystem()[0]
    os_info = computer.Win32_OperatingSystem()[0]
    proc_info = computer.Win32_Processor()[0]
    gpu_info = computer.Win32_VideoController()[0]

    os_name = os_info.Name.encode('utf-8').split(b'|')[0]
    os_version = ' '.join([os_info.Version, os_info.BuildNumber])
    system_ram = float(os_info.TotalVisibleMemorySize) / 1048576  # KB to GB
    log.info('OS Name: {0}'.format(os_name))
    log.info('OS Version: {0}'.format(os_version))
    log.info('CPU: {0}'.format(proc_info.Name))
    log.info('RAM: {0} GB'.format(system_ram))
    log.info('Graphics Card: {0}'.format(gpu_info.Name))


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
@commands.has_any_role(*admin_role)
async def reload(ctx):
    """[ADMIN] Reloads Configuration File"""
    log.info("Configuration Reload Requested")
    await ctx.send("Configuration Reload Requested")
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)
        token = config_data['discord_token']
        report_channel = config_data['report_channel']
        api_url = config_data['api_url']
        guild_id = config_data['guild_id']
        status_refresh = config_data['status_refresh']
        delayed_refresh = config_data['delayed_refresh']
        activity_rotate = config_data['activity_rotate']
        activity_refresh = config_data['activity_refresh']
        cooldown_channel = config_data['cooldown_channel']
        cooldown_user = config_data['cooldown_user']
        staff_role = tuple(config_data['permissions']['staff'])
        moderator_role = tuple(config_data['permissions']['moderators'])
        admin_role = tuple(config_data["permissions"]["admins"])
        live_feed_channel = config_data['live_feed_channel']
    try:
        await initialize_servers()
    except Exception as error:
        log.exception('Initialization Error:' + str(error))
    await ctx.send('Configuration Reload Complete')


async def rotate_activity():
    rotate_position = 0
    while activity_rotate is True:
        try:
            server = server_list[rotate_position]
            info = server.info
            if info['state'] == 'running':
                player_activity = '{}: {}/{} Online'.format(server.name, info['current_players'], info['max_players'])
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.online, activity=activity)
            elif info['state'] == 'starting':
                player_activity = '{}: Server Restarting'.format(server.name)
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.idle, activity=activity)
            elif info['state'] == 'idle':
                player_activity = '{}: Server Offline'.format(server.name)
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.do_not_disturb, activity=activity)
            if rotate_position == (int(len(server_list)) - 1):
                rotate_position = 0
                await asyncio.sleep(activity_refresh)
                player_activity = '!help for help'
                activity = discord.Game(name=player_activity)
                await bot.change_presence(status=discord.Status.online, activity=activity)
            else:
                rotate_position += 1
        except Exception as error:
            pass
        await asyncio.sleep(activity_refresh)

@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
@commands.has_any_role(*admin_role)
async def log_view(ctx, log_file: str, range: int):
    """[ADMIN] Server Log Viewer"""
    # if log_file == 'adm':
    #     latest = tailer.tail(open('DayZServer_x64.ADM'), range + 1)
    #     for i, a in enumerate(latest):
    #         log = '```' + a + '```'
    #         await ctx.send(log)

@bot.command()
@commands.cooldown(1, cooldown_user, commands.BucketType.user)
async def status(ctx, name: str):
    """Displays Server Status Information"""
    if name == 'all':
        for server in server_list:
            await tools.display_status(ctx, server)
            await asyncio.sleep(1)
    if name != 'all':
            found = False
            for server in server_list:
                if server.name == name:
                    found = True
                    await tools.display_status(ctx, server)
            if found == False:
                await ctx.send('Error: Server Not Found')


@bot.command()
@commands.has_any_role(*staff_role)
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def tech(ctx, name: str):
    """[STAFF] Displays Server Technical Details"""
    if name == 'all':
        for server in server_list:
            await tools.display_tech(ctx, server)
            await asyncio.sleep(1)
    if name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                await tools.display_tech(ctx, server)
        if found == False:
            await ctx.send('Server: ' + name + ' not found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def mods(ctx, name: str):
    """Server Mods List\n\nCommand Syntax: !mods <all> or <name>"""
    if name == 'all':
        for server in server_list:
            await tools.display_mods(ctx, server)
            await asyncio.sleep(1)
    if name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                await tools.display_mods(ctx, server)
        if found == False:
            await ctx.send('Server: ' + name + ' not found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def schedule(ctx, name: str):
    """Next Scheduled Event\n\nCommand Syntax: !schedule <all> or <shortname>"""
    if name in 'all':
        for server in server_list:
            info = server.info
            output = '```{}'.format(info['servername']).center(60, ' ') + '\n'
            output += 'Next server task is {} at {}```'.format(info['next_scheduled_task']['task']['action'],
                                                               info['next_scheduled_task']['task']['time'])
            await ctx.send(output)
    else:
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                info = server.info
                output = '```{}'.format(info['servername']).center(60, ' ') + '\n'
                output += 'Next server task is {} at {}```'.format(info['next_scheduled_task']['task'] \
                                                                       ['action'],
                                                                   info['next_scheduled_task']['task']['time'])
                await ctx.send(output)
        if not found:
            await ctx.send('Error: Server Not Found')


@bot.command()
@commands.has_any_role(*staff_role)
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def players(ctx, name: str):
    """[STAFF] Online Players List\n\nCommand Syntax: !players <all> or <shortname>"""
    if name == 'all':
        for server in server_list:
            await tools.display_players(ctx, server)
            await asyncio.sleep(1)
    elif name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                found = True
                await tools.display_players(ctx, server)
        if found == False:
            await ctx.send('Error: Server Not Found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def list(ctx):
    """List Servers in Network\n\nCommand Syntax: !list"""
    embed = discord.Embed(colour=discord.Colour(0x3D85C6),
                          timestamp=datetime.datetime.now().astimezone())
    server_short = ''
    server_long = ''
    icon_url = ''
    for server in server_list:
        icon_url = server.server_icon
        name = server.name
        info = server.info
        server_short += name + '\n'
        server_long += str(info['servername'])[:40] + '\n'
    embed.set_author(name='Network List', icon_url=icon_url)
    embed.set_footer(text="Report Generated", icon_url=icon_url)
    embed.add_field(name="Name", value=server_short, inline=True)
    embed.add_field(name="Server", value=server_long, inline=True)
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, cooldown_user, commands.BucketType.user)
async def report(ctx, player: str, category: str, details: str, location: str, time: str):
    """Report Player to Admins\n\nSend via PM to Aurora\nCommand Syntax: !report \'<player>\' \'<type of incident>\' \'<details>\' \'<location>\' \'<time>\'"""
    output = '```'
    output += 'Player Abuse Report'.center(60, ' ') + '\n'
    output += 'Reporter: {}'.format(ctx.author).center(60, ' ') + '\n'
    output += 'Player: ' + player + '\n'
    output += 'Abuse: ' + category + '\n'
    output += 'Details: ' + details + '\n'
    output += 'Location: ' + location + '\n'
    output += 'Time: ' + time + '\n'
    output += '```'
    channel_id = int(report_channel)
    channel = bot.get_channel(channel_id)
    await channel.send(output)
    await ctx.author.send("Report has been submitted.")


@bot.command()
@commands.has_any_role(*admin_role)
async def broadcast(ctx, name: str, message: str):
    """ [ADMIN] Server Broadcast \n\nCommand Syntax: !broadcast <all> or <shortname> '<message>'"""
    if name == 'all':
        for server in server_list:
            service_api_key = server.service_api_key
            service_id = server.service_id
            data = {
                'service_api_key': '{}'.format(service_api_key),
                'message': '{}'.format(message)
            }
            url = "{}servermessage/{}".format(api_url, service_id)
            try:
                async with aiohttp.ClientSession() as session:
                    await fetch_api(session, url=url, data=data)
                    await ctx.send('Message Broadcast to Entire Network!')
                await session.close()
            except Exception as error:
                log.info('Broadcast Error:' + str(error))

    if name != 'all':
        found = False
        for server in server_list:
            if server.name == name:
                info = server.info
                found = True
                service_api_key = server.service_api_key
                service_id = server.service_id
                data = {
                    'service_api_key': '{}'.format(service_api_key),
                    'message': '{}'.format(message)
                }
                url = "{}servermessage/{}".format(api_url, service_id)
                try:
                    async with aiohttp.ClientSession() as session:
                        await fetch_api(session, url=url, data=data)
                        output = 'Message Broadcast to Server: ' + info['servername']
                        await ctx.send(output)
                    await session.close()
                except Exception as error:
                    log.exception('Broadcast Error: ' + str(error))
        if found == False:
            await ctx.send('Error: Server Not Found')


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def kills(ctx, name: str, limit: int):
    """ Kills Leaderboard \n\nCommand Syntax: !kills [all][server] [limit]"""
    if limit <= 50:
        if name == 'all':
            for server in server_list:
                await tools.display_kills(ctx, limit, server)
                await asyncio.sleep(1)
        if name != 'all':
            found = False
            for server in server_list:
                if server.name == name:
                    found = True
                    await tools.display_kills(ctx, limit, server)
            if found == False:
                await ctx.send('Server: ' + name + ' not found')
    if limit > 50:
        await ctx.send("Specified Limit Too High: 50 Max")


@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def played(ctx, name: str, limit: int):
    """ Played Time Leaderboard \n\nCommand Syntax: !played [all][server] [limit]"""
    if limit <= 50:
        if name == 'all':
            for server in server_list:
                await tools.display_played(ctx, limit, server)
                await asyncio.sleep(1)
        if name != 'all':
            found = False
            for server in server_list:
                if server.name == name:
                    found = True
                    await tools.display_played(ctx, limit, server)
            if found == False:
                await ctx.send('Server: ' + name + ' not found')
    if limit > 50:
        await ctx.send("Specified Limit Too High: 50 Max")

@bot.command()
@commands.cooldown(1, cooldown_channel, commands.BucketType.channel)
async def api(ctx):
    """ Displays Total API Calls """
    global api_count
    global startup_time
    uptime = (datetime.datetime.now() - startup_time)
    await ctx.send("Uptime: {}".format(uptime))
    await ctx.send("Total CFTools API Calls: {}".format(api_count))


bot.run(token)
