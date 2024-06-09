import os, sys, subprocess, re, urllib

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from tld import get_tld
import discord, asyncio, threading
import secret, syncer
from loader import Loader

admins = [secret.NOIS_ID, secret.FOUR_ID]

prefix = 'a!'
animes = []
channels = []


def is_command(msg, *commands):
	return any(msg.content.lower().startswith(prefix + cmd) for cmd in commands)

def is_valid_url(url):
	regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	check = re.findall(regex, url)
	if check:
		domain = get_tld(url, as_object=True).domain
		return domain == 'animekisa'

	return False

def get_number(n):
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

def update():
	global animes, channels
	animes = loader.get_animes()
	channels = loader.get_channels()


class Bot():
	def __init__(self, client, loop):
		self.client = client
		self.syncer = syncer.Syncer(animes)
		self.loop = loop
		asyncio.set_event_loop(loop)
		self.help_table = [
			{
				'name': 'a!anime',
				'value': 'Displays a list of animes currently being tracked.'
			},
			{
				'name': 'a!add <name> <url>',
				'value': 'Adds the specified anime to the list of tracked anime.'
			},
			{
				'name': 'a!remove <name>',
				'value': 'Removes the specified anime from the list of tracked anime.'
			},
			{
				'name': 'a!episodes',
				'value': 'Displayes a list of episodes that the bot has stored per tracked anime.'
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
			threading.Thread(target=self.run_waiter).start()
			print('Started...')
			self.info_channel = self.client.get_channel(secret.INFO_CHANNEL_ID)
			await self.info_channel.send(embed=discord.Embed(title=f'Started on {sys.platform}.', color=0xff9494))

		@self.client.event
		async def on_message(message):
			global animes, channels

			if message.author == self.client.user or message.channel.type in [discord.ChannelType.private, discord.ChannelType.group]:
				return

			if message.content.lower().startswith('!forcequit'):
				if message.author.id in admins and self.client.user in message.mentions:
					print('Stopping...')
					await self.info_channel.send(embed=discord.Embed(title='Stopped...', color=0xff9494))
					sys.exit()

			if message.content.lower().startswith('!restart') and (self.client.user in message.mentions or '-all' in message.content.lower()):
				if message.author.id in admins:
					subprocess.call([sys.executable, os.path.realpath(__file__)])
					sys.exit()

			# if message.author.id != secret.NOIS_ID:
			# 	return

			update()

			if is_command(message, 'add'):
				splt = message.content.split()

				if len(splt) < 3: return

				*name, url = splt[1:]
				name = ' '.join(name)

				if is_valid_url(url):	
					res = loader.add_anime(name, url)

					if res == -1:
						title = 'Anime already added!'
						color = 0xff9494
					else:
						title = f'Added anime: {name}!'
						color = 0x90ee90

					await message.channel.send(embed=discord.Embed(title=title, color=color), delete_after=2)
					await asyncio.sleep(2)
					await message.delete()

				else:
					await message.channel.send(embed=discord.Embed(title='URL not valid!', color=0xff9494), delete_after=2)
					await asyncio.sleep(2)


			if is_command(message, 'remove'):
				splt = message.content.split()

				if len(splt) < 2: return

				name = ' '.join(splt[1:])
				res = loader.remove_anime(name)

				if res == -1:
					title = 'Anime not added yet!'
					color = 0xff9494
				else:
					title = f'Removed anime: {res}!'
					color = 0x90ee90


				await message.channel.send(embed=discord.Embed(title=title, color=color), delete_after=2)
				await asyncio.sleep(2)
				await message.delete()


			if is_command(message, 'anime'):
				animes = loader.get_animes()

				if animes:
					embed = discord.Embed(title='Anime')
					for anime in animes:
						embed.add_field(name=anime[0], value=anime[1], inline=False)

					await message.channel.send(embed=embed)

				else:
					await message.channel.send(embed=discord.Embed(title='No anime added!', color=0xff9494), delete_after=2)
					await asyncio.sleep(2)
					await message.delete()


			if is_command(message, 'episodes'):
				if animes:
					embed = discord.Embed(title='Episodes')
					for anime in animes:
						episodes = loader.get_episodes(anime)
						if episodes:
							mn = min(episodes)
							mx = max(episodes)
							color = None

							if mn == mx:
								val = f'Stored episode: `{mn}`'
							else:
								val = f'Stored episodes: `{mn} - {mx}`'
						
						else:
							val = 'No episodes stored.'
							embed.color = 0xff9494
							
						embed.add_field(name=anime[0], value=val, inline=False)
					
					await message.channel.send(embed=embed)


			if is_command(message, 'channel add'):
				res = loader.add_channel(message.channel.id)

				if res is None:
					title = 'Channel added!'
					color = 0x90ee90
				else:
					title = 'Channel already added!'
					color = 0xff9494


				await message.channel.send(embed=discord.Embed(title=title, color=color), delete_after=2)
				await asyncio.sleep(2)
				await message.delete()


			if is_command(message, 'channel remove'):
				res = loader.remove_channel(message.channel.id)
				channels = loader.get_channels()

				if res is None:
					title = 'Channel removed!'
					color = 0x90ee90
				else:
					title = 'Channel not added yet!'
					color = 0xff9494

				await message.channel.send(embed=discord.Embed(title=title, color=color), delete_after=2)
				await asyncio.sleep(2)
				await message.delete()


			if is_command(message, 'channels'):
				channels = loader.get_channels()

				if channels:
					embed = discord.Embed(title='Channels')
					for channel_id in channels:
						channel = self.client.get_channel(channel_id)
						embed.add_field(name=f'#{channel.name}', value=channel.guild.name, inline=False)

					await message.channel.send(embed=embed)

				else:
					await message.channel.send(embed=discord.Embed(title='No channels added!', color=0xff9494), delete_after=2)
					await asyncio.sleep(2)
					await message.delete()



			if is_command(message, 'help'):
				embed = discord.Embed(
					title='AnimeGetter - Help',
					color=0xff0000
				)
				for field in self.help_table:
					embed.add_field(name=field['name'], value=field['value'], inline=False)

				embed.set_footer(text='AnimeGetter made by NoisNette')

				channel = await message.author.create_dm()
				await channel.send(embed=embed)


	async def waiter(self):
		while True:
			found = self.syncer.get_found()
			while found == {}:
				self.syncer.sync_animes()
				found = self.syncer.get_found()
				if found == {}:
					await asyncio.sleep(60)

			embed = discord.Embed(title='New episodes!')

			image_urls = []

			for name, val in found.items():
				missing_episodes_str, url, image_url = val
				missing_episodes = eval(missing_episodes_str)

				if len(missing_episodes) == 0: continue

				image_urls.append(image_url)
				name_str = f'{name} | `{get_number(missing_episodes[-1])} episode!`'
				embed.add_field(name=name_str, value=url, inline=False)

			if len(image_urls) == 1:
				thumbnail = image_urls[0]
			else:
				thumbnail = 'https://i.pinimg.com/favicons/8db9363da178ce303f3196e03a70b4d82648b4c1244b36586cbff927.png?caf1425866776f962da80817ccf81b4a' # Animekisa logo

			embed.set_thumbnail(url=thumbnail)

			await asyncio.sleep(0.5)

			for channel_id in channels:
				channel = self.client.get_channel(channel_id)
				await channel.send(embed=embed)

			self.syncer.reset_found()


	def run_waiter(self):
		asyncio.run_coroutine_threadsafe(self.waiter(), self.loop).result()
		self.loop.run_forever()


if __name__ == '__main__':
	print('Starting...')
	loop = asyncio.get_event_loop()
	client = discord.Client(activity=discord.Activity(type=discord.ActivityType.watching, name='anime'), loop=loop)
	loader = Loader()
	animes = loader.get_animes()
	channels = loader.get_channels()
	bot = Bot(client, loop)

	# Delay na paljenju kako bi pi imao vremena se spojiti na internet
	while True:
		try:
			urllib.request.urlopen("http://google.com")
			break
		except urllib.error.URLError:
			pass
		except Exception as e:
			print(e)
	
	bot.client.run(secret.DISCORD_TOKEN)