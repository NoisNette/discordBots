import os, sys, subprocess, urllib
import discord, asyncio, threading

os.chdir(os.path.dirname(os.path.realpath(__file__)))

import secret
from fileHelper import FileHelper
from scraper import Scraper

ADMINS = [secret.NOIS_ID, secret.FOUR_ID]

prefix = 'a!'

def isCommand(msg, *commands):
	return any(msg.content.lower().startswith(prefix + cmd) for cmd in commands)

def formatNumber(n):
	if n == 0:
		return f'{n}th'
	if n % 100 in [11, 12, 13]:
		return f'{n}th'
	if n % 10 == 1:
		return f'{n}st'
	if n % 10 == 2:
		return f'{n}nd'
	if n % 10 == 3:
		return f'{n}rd'
	return f'{n}th'

class Bot:
	def __init__(self, client):
		self.client = client
		self.helpTable = [
			{
				'name': 'a!animes',
				'value': 'Displays a list of animes currently being tracked.'
			},
			{
				'name': 'a!add <name> <id>',
				'value': 'Adds the specified anime to the list of tracked anime.'
			},
			{
				'name': 'a!remove <name>',
				'value': 'Removes the specified anime from the list of tracked anime.'
			},
			{
				'name': '** **',
				'value': '** **'
			},
			{
				'name': 'a!channels',
				'value': 'Displays a list of channels to send anime updates to.'
			},
			{
				'name': 'a!channel add',
				'value': 'Adds the channel to the list of channels to send anime updates to.'
			},
			{
				'name': 'a!channel remove',
				'value': 'Removes the channel from the list of channels to send anime updates to.'
			},
			{
				'name': '** **',
				'value': '** **'
			},
			{
				'name': 'a!help',
				'value': 'Sends this message to you.'
			}
		]
	
		@self.client.event
		async def on_ready():
			print('Started...')
			self.infoChannel = self.client.get_channel(secret.INFO_CHANNEL_ID)
			await self.infoChannel.send(embed=discord.Embed(title=f'Started on {sys.platform}.', color=0xff9494))
			await self.sync()

		@self.client.event
		async def on_message(message):
			if message.author == self.client.user or message.channel.type in [discord.ChannelType.private, discord.ChannelType.group]:
				return

			if message.content.lower().startswith('!forcequit'):
				if message.author.id in ADMINS and self.client.user in message.mentions:
					print('Stopping...')
					await self.infoChannel.send(embed=discord.Embed(title='Stopped...', color=0xff9494))
					sys.exit()

			if message.content.lower().startswith('!restart') and (self.client.user in message.mentions or '-all' in message.content.lower()):
				if message.author.id in ADMINS:
					subprocess.call([sys.executable, os.path.realpath(__file__)])
					sys.exit()

			if isCommand(message, 'add'):
				splt = message.content.split()
				if len(splt) < 3: return

				*name, id = splt[1:]
				name = ' '.join(name)


				animeData = Scraper.getData(id)
				animeData['name'] = name
				animeData['id'] = id
				animeData['url'] = 'https://zoro.to/' + id

				try:
					FileHelper.saveAnime(animeData)
					title = f'Added anime: {name}!'
					color = 0x90ee90
				except KeyError:
					title = 'Anime already added!'
					color = 0xff9494

				await message.channel.send(embed=discord.Embed(title=title, color=color))

			if isCommand(message, 'remove'):
				splt = message.content.split()
				if len(splt) < 2: return

				name = ' '.join(splt[1:])

				try:
					FileHelper.removeAnime(name)
					title = f'Removed anime: {name}!'
					color = 0x90ee90
				except KeyError:
					title = 'Anime not yet added!'
					color = 0xff9494

				await message.channel.send(embed=discord.Embed(title=title, color=color))

			if isCommand(message, 'animes'):
				animes = FileHelper.getAllAnimes()

				if animes:
					embed = discord.Embed(title='Animes')
					for anime in animes:
						embed.add_field(name=anime['name'], value=f'Ep {anime["currentEpisode"]} / {anime["maxEpisodes"]}', inline=False)
					
					await message.channel.send(embed=embed)
				
				else:
					await message.channel.send(embed=discord.Embed(title='No animes added!', color=0xff9494))

			if isCommand(message, 'channel add'):
				channel = {
					'name': message.channel.name,
					'id': message.channel.id,
					'serverName': message.channel.guild.name
				}
				try:
					FileHelper.saveChannel(channel)
					title = 'Added this channel!'
					color = 0x90ee90
				except KeyError:
					title = 'Channel already added!'
					color = 0xff9494

				await message.channel.send(embed=discord.Embed(title=title, color=color))

			if isCommand(message, 'channel remove'):
				try:
					FileHelper.removeChannel(message.channel.id)
					title = 'Removed this channel!'
					color = 0x90ee90
				except KeyError:
					title = 'Channel not yet added!'
					color = 0xff9494

				await message.channel.send(embed=discord.Embed(title=title, color=color))
			
			if isCommand(message, 'channels'):
				channels = FileHelper.getAllChannels()

				if channels:
					embed = discord.Embed(title='Channels')
					for channel in channels:
						embed.add_field(name=channel['name'], value=channel['serverName'], inline=False)
					
					await message.channel.send(embed=embed)
				
				else:
					await message.channel.send(embed=discord.Embed(title='No channels added!', color=0xff9494))

			if isCommand(message, 'help'):
				embed = discord.Embed(
					title='AnimeGetter - Help',
					color=0xff0000
				)
				for field in self.helpTable:
					embed.add_field(name=field['name'], value=field['value'], inline=False)
				
				embed.set_footer(text='AnimeGetter made by NoisNette')

				channel = await message.author.create_dm()
				await channel.send(embed=embed)

	def checkForUpdates(self):
		animes = FileHelper.getAllAnimes()
		updatedAnimes = []
		for anime in animes:
			currentEpisode = Scraper.getCurrentEpisodesCount(anime['id'])
			if currentEpisode != anime['currentEpisode']:
				anime['currentEpisode'] = currentEpisode
				updatedAnimes.append(anime)
		
		return updatedAnimes


	async def sync(self):
		while True:
			updatedAnimes = self.checkForUpdates()
			while updatedAnimes == []:
				updatedAnimes = self.checkForUpdates()
				if updatedAnimes == []:
					await asyncio.sleep(60) # check for updates every 60 seconds

			embed = discord.Embed(title='New episodes!')
			
			imgUrls = []

			for anime in updatedAnimes:
				name = anime['name']
				newEpisode = anime['currentEpisode']
				url = anime['url']
				imgUrl = anime['imgUrl']

				FileHelper.updateAnime(anime)

				imgUrls.append(imgUrl)
				name_str = f'{name} | `{formatNumber(newEpisode)} episode!`'
				embed.add_field(name=name_str, value=url, inline=False)
			
			if len(imgUrls) == 1:
				thumbnailUrl = imgUrls[0]
			else:
				thumbnailUrl = 'https://zoro.to/images/zoro.png'

			embed.set_thumbnail(url=thumbnailUrl)
			
			await asyncio.sleep(0.5)

			channels = FileHelper.getAllChannels()
			for channel in channels:
				ch = self.client.get_channel(channel['id'])
				await ch.send(embed=embed)


if __name__ == '__main__':
	print('Starting...')
	client = discord.Client(activity=discord.Activity(type=discord.ActivityType.watching, name='anime'), intents=discord.Intents.all())
	bot = Bot(client)

	# delay on startup so the pi can connect to the internet
	while True:
		try:
			urllib.request.urlopen('http://google.com')
			break
		except urllib.error.URLError:
			pass
		except Exception as e:
			print(e)

	bot.client.run(secret.DISCORD_TOKEN)