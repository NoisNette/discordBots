import os
import subprocess
import sys
import urllib

import discord

import secret
import wordsHelper
from word import Word

# red - 0xff9494
# blue - 0x2caeb9
# yellow - 0xffff00
# green - 0x90ee90
# background greyish - 0x36393f

prefix = 'g!'
admins = [secret.NOISNETTE_ID, secret.FOUR_ID]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)


game_started = False
game_starter = None
played_words = []
raw_played_words = []

HELP_TABLE = [
	{
		'name': f'{prefix}prefix <prefix>',
		'value': "Changes the bot's prefix to the specified prefix."
	},
	{
		'name': f'{prefix}start',
		'value': 'Starts a game of Kaladont if none is ongoing.'
	},
	{
		'name': f'{prefix}stop',
		'value': 'Stops a game of Kaladont if one is ongoing. Only the person who started the game can end it.'
	},
]


async def load_prefix() -> None:
	global prefix
	with open('prefix.txt', 'r') as f:
		prefix = f.read().strip()
	
	await update_presence()


async def set_prefix(pref: str) -> None:
	global prefix

	with open('prefix.txt', 'w') as f:
		f.write(pref)

	prefix = pref

	await update_presence()


async def update_presence() -> None:
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f'{prefix}help'))


def reset() -> None:
	global game_started, game_starter, played_words, raw_played_words
	game_started = False
	game_starter = None
	played_words = []
	raw_played_words = []


@client.event
async def on_ready() -> None:
	print('Started...')

	await load_prefix()

	info_channel = client.get_channel(secret.INFO_CHANNEL_ID)
	await info_channel.send(embed=discord.Embed(title=f'Started on {sys.platform}.', color=0xffff00))


@client.event
async def on_message(message: discord.Message) -> None:
	global game_started, game_starter

	if message.author == client.user or message.author.bot or message.embeds or message.channel.type in [discord.ChannelType.private, discord.ChannelType.group]:
		return

	if message.content.lower().startswith('!forcequit'):
		if message.author.id in admins and client.user in message.mentions:
			print('Stopping...')
			info_channel = client.get_channel(secret.INFO_CHANNEL_ID)
			await info_channel.send(embed=discord.Embed(title='Stopped...', color=0xff9494))

			sys.exit()

	if message.content.lower().startswith('!restart'):
		if message.author.id in admins and (client.user in message.mentions or '-all' in message.content.lower()):
			subprocess.call([sys.executable, os.path.realpath(__file__)])
			sys.exit()

	if message.content.lower().startswith(prefix + 'help'):
		embed = discord.Embed(
			title='GameBot - Help',
			color=0xff0000
		)
		for field in HELP_TABLE:
			embed.add_field(name=field['name'], value=field['value'], inline=False)

		embed.set_footer(text='GameBot made by NoisNette')

		channel = await message.author.create_dm()
		await channel.send(embed=embed)

		return


	if message.content.lower().startswith(prefix + 'prefix'):
		await load_prefix()

		if message.author.id not in admins:
			return

		split = message.content.split()

		if len(split) == 1:
			await message.channel.send(embed=discord.Embed(title='Izaberi prefiks!', color=0xff9494))
			return

		elif len(split) > 2:
			await message.channel.send(embed=discord.Embed(title='Previše argumenata!', color=0xff9494))
			return

		pref = split[1]
		await set_prefix(pref)
		await message.channel.send(embed=discord.Embed(title=f'Prefiks je sada _{pref}_', color=0x90ee90))

	
	if message.content.lower().startswith(prefix + 'start'):
		if game_started:
			await message.channel.send(embed=discord.Embed(title=f'Igra već traje! Zadnja odigrana riječ je `{played_words[-1].upper()}`', color=0xff9494))
			return
		
		game_started = True
		game_starter = message.author.id

		word = Word(wordsHelper.choose_new_word(), message.author.id)
		played_words.append(word)
		raw_played_words.append(word.word)

		await message.channel.send(embed=discord.Embed(
			title=word.underlined,
			description=f'Mogućih riječi: **{len(word.available_words)}**',
			color=0xffff00
		))

	
	if message.content.lower().startswith(prefix + 'stop'):
		if not game_started:
			await message.channel.send(embed=discord.Embed(title='Igra ne traje!', color=0xff9494))
			return

		if message.author.id != game_starter or message.author.id not in admins:
			starter = client.get_user(game_starter)
			await message.channel.send(embed=discord.Embed(title=f'Igru može zaustaviti samo onaj koji ju je započeo! ({starter.mention})', color=0xff9494))
			return

		last_word = played_words[-1]
		reset()

		if len(last_word.alternate_choices) > 0:
			await message.channel.send(embed=discord.Embed(
				description='**Riječi koje ste mogli iskoristiti:**\n\n'+'\n'.join(f'- `{w}`' for w in last_word.alternate_choices),
				color=0x36393f
			))
		
		else:
			await message.channel.send(embed=discord.Embed(
				description='**Kraj igre**\n\nNa tu riječ niste mogli nastaviti...',
				color=0x36393f
			))

		return


	elif game_started:
		last_word = played_words[-1]

		if last_word.player_id == message.author.id and len(played_words) > 1:
			await message.channel.send(embed=discord.Embed(
				description=f'Ne možeš nastaviti na svoju riječ.',
				color=0x36393f
			))

			return

		if not message.content.lower().startswith(last_word.suffix):
			return

		word = Word(message.content, message.author.id)

		available = [w for w in word.available_words if w not in raw_played_words]

		if word.word in raw_played_words:
			await message.add_reaction('❌')
			return

		elif len(word.word) < 3:
			return

		elif len(available) == 0:
			await message.add_reaction('🔥')

			await message.channel.send(embed=discord.Embed(
				description=f'Kraj igre {message.author.mention}\nDužina igre: **{len(played_words)}**',
				color=0x36393f
			))

			reset()
			return

		available = [w for w in last_word.available_words if w not in played_words]

		if word.word in available:
			played_words.append(word)
			raw_played_words.append(word.word)

			await message.add_reaction('✅')

			await message.channel.send(embed=discord.Embed(
				title=word.underlined,
				description=f'Mogućih riječi: **{len(available)}**',
				color=0xffff00
			))

			return
		
		else:
			await message.add_reaction('❌')
			return
			




if __name__ == '__main__':
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	print('Starting...')

	# Delay na paljenju kako bi pi imao vremena se spojiti na internet
	while True:
		try:
			urllib.request.urlopen("http://google.com")
			break
		except urllib.error.URLError:
			pass
		except Exception as e:
			print(e)
	
	client.run(secret.OAUTH_TOKEN)