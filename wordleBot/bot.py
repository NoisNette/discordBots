import os
import subprocess
import sys
import urllib
from string import ascii_uppercase as alphabet

import discord

import secret
from game import Game
from channelHelper import ChannelHelper

prefix = 'w!'
admins = [secret.NOISNETTE_ID, secret.FOUR_ID]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

HELP_TABLE = [
	{
		'name': f'{prefix}prefix <prefix>',
		'value': 'Promijeni prefiks u navedeni prefiks.'
	},
	{
		'name': f'{prefix}channel add',
		'value': 'Bot počne prihvaćati poruke iz trenutnog kanala.'
	},
	{
		'name': f'{prefix}channel remove',
		'value': 'Bot prestane prihvaćati poruke iz trenutnog kanala.'
	},
	{
		'name': f'{prefix}channels',
		'value': 'Prikaže popis svih kanala otkud se prihvaćaju poruke.'
	},
	{
		'name': f'{prefix}start',
		'value': 'Započne igru Wordle ako jedna već ne traje.'
	},
	{
		'name': f'{prefix}stop',
		'value': 'Zaustavi igru Wordle ako jedna traje. Jedino osoba koja je započela igru ju može i završiti.'
	},
	{
		'name': f'{prefix}reset',
		'value': 'Bot započne birati riječi ispočetka.'
	},
]

DICTIONARY_PATH = 'words/dictionary.txt'
POSSIBLE_SHUFFLED_WORDS_PATH = 'words/possible_shuffled.txt'
WORD_INDEX_PATH = 'word_index.txt'
TEMPLATE_PATH = 'img/template.png'
RESULT_PATH = 'img/result.png'

CHANNELS_PATH = 'channels.txt'

# game = Game(
# 	DICTIONARY_PATH,
# 	POSSIBLE_SHUFFLED_WORDS_PATH,
# 	WORD_INDEX_PATH,
# 	TEMPLATE_PATH,
# 	RESULT_PATH
# )
game = None

channelHelper = ChannelHelper(CHANNELS_PATH)

game_started = False
game_starter = None


# prefix operations
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
	global game, game_started, game_starter
	game_started = False
	game_starter = None

	game = Game(
		DICTIONARY_PATH,
		POSSIBLE_SHUFFLED_WORDS_PATH,
		WORD_INDEX_PATH,
		TEMPLATE_PATH,
		RESULT_PATH
	)

	game.draw_empty()


@client.event
async def on_ready() -> None:
	print('Started...')

	await load_prefix()

	info_channel = client.get_channel(secret.INFO_CHANNEL_ID)
	await info_channel.send(embed=discord.Embed(title=f'Started on {sys.platform}.', color=0x0dff05))


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
	
	elif message.content.lower().startswith('!restart'):
		if message.author.id in admins and (client.user in message.mentions or '-all' in message.content.lower()):
			subprocess.call([sys.executable, os.path.realpath(__file__)])
			sys.exit()

	elif message.content.lower().startswith(prefix + 'help'):
		embed = discord.Embed(
			title='WordleBot - Help',
			color=0x0dff05
		)
		for field in HELP_TABLE:
			embed.add_field(name=field['name'], value=field['value'], inline=False)
		
		embed.set_footer(text='WordleBot made by NoisNette')

		channel = await message.author.create_dm()
		await channel.send(embed=embed)

		return
	

	elif message.content.lower().startswith(prefix + 'prefix'):
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


	elif message.content.lower().startswith(prefix + 'channel add'):
		res = channelHelper.add_channel(message.channel.id)

		if res is None:
			title = 'Channel added!'
			color = 0x90ee90
		else:
			title = 'Channel already added!'
			color = 0xff9494
		
		await message.channel.send(embed=discord.Embed(title=title, color=color), delete_after=2)


	elif message.content.lower().startswith(prefix + 'channel remove'):
		res = channelHelper.remove_channel(message.channel.id)

		if res is None:
			title = 'Channel removed!'
			color = 0x90ee90
		else:
			title = 'Channel not added yet!'
			color = 0xff9494

		await message.channel.send(embed=discord.Embed(title=title, color=color), delete_after=2)

	
	elif message.content.lower().startswith(prefix + 'channels'):
		channels = channelHelper.get_channels()
		
		if channels:
			embed = discord.Embed(title='**Channels**')
			for channel_id in channels:
				channel = client.get_channel(channel_id)
				embed.add_field(name=f'#{channel.name}', value=channel.guild.name, inline=False)

			await message.channel.send(embed=embed)
		
		else:
			await message.channel.send(embed=discord.Embed(title='No channels added!', color=0xff9494), delete_after=2)


	if message.channel.id not in channelHelper.get_channels():
		return


	elif message.content.lower().startswith(prefix + 'reset'):
		if message.author.id in admins:
			await message.channel.send(embed=discord.Embed(title='Započinjem birati riječi ispočetka...', color=0x90ee90))
			game.reset_word_idx()
			return

	
	elif message.content.lower().startswith(prefix + 'start'):
		if game_started:
			starter = client.get_user(game_starter)
			await message.channel.send(embed=discord.Embed(title=f'Igra već traje! Započeo ju je {starter.mention}.', color=0xff9494))
			return
		
		game_started = True
		game_starter = message.author.id

		embed = discord.Embed(title='**Game started**', color=0x0dff05)
		await message.channel.send(embed=embed, file=discord.File(RESULT_PATH))


	elif message.content.lower().startswith(prefix + 'stop'):
		if not game_started:
			await message.channel.send(embed=discord.Embed(title='Igra ne traje!', color=0xff9494))
			return
		
		if message.author.id != game_starter or message.author.id not in admins:
			starter = client.get_user(game_starter)
			await message.channel.send(embed=discord.Embed(title=f'Igru može zaustaviti samo onaj koji ju je započeo! (@{starter.display_name})', color=0xff9494))
			return

		embed = discord.Embed(title=f'**{game.target_word}**', color=0x0dff05)
		await message.channel.send(embed=embed, file=discord.File(RESULT_PATH))

		reset()


	elif game_started:
		content = message.content.upper().strip()

		if len(content) != 5 or any(not c.isalpha() for c in content):
			return

		res = game.play_word(content)

		game_over = game.is_game_over()
		
		if not res['status']: # word not valid
			return

		elif res['status']: # word valid
			if res['correct']:
				embed = discord.Embed(title=f'**You won!**', color=0x0dff05)

			elif not game_over:
				embed = discord.Embed(color=0x0dff05)
				unused_letters = sorted(set(alphabet) - set(res['letters']))
				embed.add_field(name='**Used letters**', value=' '.join(res['letters']), inline=False)
				embed.add_field(name='**Unused letters**', value=' '.join(unused_letters), inline=False)

			else:
				embed = discord.Embed(title=f'**{game.target_word}**', color=0x0dff05)

			await message.channel.send(embed=embed, file=discord.File(RESULT_PATH))
		
		if game_over:
			reset()
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
	
	reset()
	client.run(secret.OAUTH_TOKEN)