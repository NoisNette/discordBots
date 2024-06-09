import discord, secret, sys, os, re, subprocess, asyncio, urllib
from datetime import datetime
from tld import get_tld

admins = [secret.NOISNETTE_ID, secret.FOUR_ID]

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name='out for unknown links'))
prefix = '!'

is_paused = False

whitelist = set()
def load_whitelist():
	global whitelist
	with open('whitelist.txt', 'r') as f:
		whitelist = set(int(l.strip()) for l in f.readlines())


async def forcequit():
	print('Stopping...')

	info_channel = client.get_channel(secret.INFO_CHANNEL_ID)
	await info_channel.send(embed=discord.Embed(title='Stopped...', color=0xff9494))

	log(stopped=True)

	sys.exit()


def log(**kwargs):
	timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
	entry = None

	started = kwargs.get('started', False)
	stopped = kwargs.get('stopped', False)
	restart = kwargs.get('restart', False)
	whitelisted = kwargs.get('whitelisted', None)
	removed = kwargs.get('removed', None)
	msg = kwargs.get('msg', None)
	links = kwargs.get('links', None)
	pause = kwargs.get('pause', None)


	if started:
		entry = f'{timestamp} Bot started on {sys.platform}.'

	elif stopped:
		entry = f'{timestamp} Bot stopped.'

	elif restart:
		entry = f'{timestamp} Restart initiated by {msg.author.name}.'

	elif whitelisted:
		entry = f'{timestamp} Whitelisted user(s): {", ".join(user.name for user in whitelisted)}.'

	elif removed:
		entry = f'{timestamp} Removed user(s): {", ".join(user.name for user in removed)} from the whitelist.'

	elif pause is not None:
		entry = f'{timestamp} Pause set to {pause}.'

	else:
		entry = f'{timestamp} Deleted links from \'{msg.author}\' (id={msg.author.id}) {links}'

	if entry:
		with open('log.txt', 'a') as f:
			f.write(entry + '\n')


@client.event
async def on_ready():
	print('Started...')
	info_channel = client.get_channel(secret.INFO_CHANNEL_ID)
	await info_channel.send(embed=discord.Embed(title=f'Started on {sys.platform}.', color=0x2caeb9))

	log(started=True)

@client.event
async def on_message(message):
	if message.author == client.user or message.channel.type in [discord.ChannelType.private, discord.ChannelType.group]:
		return

	if message.content.lower().startswith(prefix + 'forcequit'):
		if message.author.id in admins and (client.user in message.mentions or '-all' in message.content.lower()):
			await forcequit()

	if message.content.lower().startswith(prefix + 'restart'):
		if message.author.id in admins and (client.user in message.mentions or '-all' in message.content.lower()):
			log(restart=True, msg=message)
			subprocess.call([sys.executable, os.path.realpath(__file__)])
			sys.exit()


	if message.content.lower().startswith(prefix + 'pause'):
		global is_paused

		if message.author.id in admins:
			try:
				arg = message.content.lower().split(' ')[1]
				if arg in ['1', 'true']:
					if not is_paused:
						is_paused = True
						log(pause=True)

						await message.channel.send(
							embed=discord.Embed(title=f'Pause set to True.', color=0x90ee90), 
							delete_after=3
						)
					else:
						await message.channel.send(
							embed=discord.Embed(title=f'Pause already True.', color=0xff9494), 
							delete_after=3
						)

				elif arg in ['0', 'false']:
					if is_paused:
						is_paused = False
						log(pause=False)

						await message.channel.send(
							embed=discord.Embed(title=f'Pause set to False.', color=0xff9494), 
							delete_after=3
						)
					else:
						await message.channel.send(
							embed=discord.Embed(title=f'Pause already False.', color=0xff9494), 
							delete_after=3
						)

				else:
					await message.channel.send(
						embed=discord.Embed(title=f'Invalid argument!', color=0xff9494), 
						delete_after=3
					)

				await asyncio.sleep(3)
				await message.delete()

			except IndexError:
				await message.channel.send(
					embed=discord.Embed(title=f'Pause is currently set to {is_paused}.', color=0x2caeb9), 
				)


	if message.content.lower().startswith(prefix + 'last'):
		if message.author.id in whitelist:
			with open('log.txt', 'r') as f:
				lines = f.readlines()[::-1]

			last_deleted = None
			for line in lines:
				if 'Deleted links from' in line:
					last_deleted = line
					break

			if last_deleted is not None:
				links = eval(last_deleted[last_deleted.index('['):])
				author_id = int(last_deleted[last_deleted.index('id=')+3:last_deleted.index(')')])
				author = await client.fetch_user(author_id)

				embed = discord.Embed(
					title=f'{author.name} sent {"these links" if len(links) > 1 else "this link"}.',
					color=0x2caeb9
				)

				for link in links:
					embed.add_field(name='<' + link + '>', value='** **', inline=False)


			else:
				embed = discord.Embed(title='No links have been deleted so far!', color=0xff9494)


			await message.channel.send(embed=embed)

		else:
			await message.channel.send(
				embed=discord.Embed(title="You can't do that!", color=0xff9494), 
				delete_after=3
			)
			await asyncio.sleep(3)
			await message.delete()


	if message.content.lower().startswith(prefix + 'whitelist'):
		load_whitelist()

		try:
			arg = message.content.lower().split(' ')[1]
			if arg == 'add':
				if message.mentions != []:
					if message.author.id not in (whitelist | set(admins)):
						await message.channel.send(
							embed=discord.Embed(title="You can't do that!", color=0xff9494), 
							delete_after=3
						)
						return

					added = []

					for user in message.mentions:
						if user.id not in whitelist:
							whitelist.add(user.id)

							with open('whitelist.txt', 'a') as f:
								f.write(str(user.id) + '\n')

							added.append(user)

					if added:
						title = f'Added member{"s" if len(added) > 1 else ""} {", ".join(user.name for user in added)} to the whitelist!'
						await message.channel.send(
							embed=discord.Embed(title=title, color=0x90ee90),
							delete_after=3
						)
						log(whitelisted=added)

					else:
						await message.channel.send(
							embed=discord.Embed(title='Member(s) already in whitelist!', color=0xff9494), 
							delete_after=3
						)

					await asyncio.sleep(3)
					await message.delete()

				else:
					await message.channel.send(
						embed=discord.Embed(title='No members specified!', color=0xff9494), 
						delete_after=3
					)
			
			elif arg == 'remove':
				if message.mentions != []:
					if message.author.id not in (whitelist | set(admins)):
						await message.channel.send(
							embed=discord.Embed(title="You can't do that!", color=0xff9494),
							delete_after=3
						)
						return
					removed = []
					for user in message.mentions:
						if user.id in whitelist:
							whitelist.remove(user.id)

							with open('whitelist.txt', 'w') as f:
								for user_id in whitelist:
									f.write(str(user_id) + '\n')

							removed.append(user)

					if removed:
						title = f'Removed member{"s" if len(removed) > 1 else ""} {", ".join(user.name for user in removed)} from the whitelist!'
						await message.channel.send(
							embed=discord.Embed(title=title, color=0x90ee90),
							delete_after=3
						)
						log(removed=removed)

					else:
						await message.channel.send(
							embed=discord.Embed(title='Member(s) not in whitelist!', color=0xff9494),
							delete_after=3
						)

					await asyncio.sleep(3)
					await message.delete()

			else:
				await message.channel.send(
					embed=discord.Embed(title='Invalid argument!', color=0xff9494),
					delete_after=3
				)
				await asyncio.sleep(3)
				await message.delete()
				return

		except IndexError:
			users = []
			for user_id in whitelist:
				user = await client.fetch_user(user_id)
				users.append(user.name)

			if users:
				embed = discord.Embed(title='Whitelist', color=0x2caeb9)
				max_len = max(0, len(max(users, key=len)) - 2)
				for user in users[:-1]:
					embed.add_field(name=user, value=('\_' * max_len), inline=False)
				embed.add_field(name=users[-1], value='** **', inline=False)
			else:
				embed = discord.Embed(title='Whitelist empty!', color=0xff9494)

			await message.channel.send(embed=embed)


	if message.author.id not in whitelist and not is_paused:
		regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
		url = re.findall(regex, message.content)
		if url:
			links = [l[0] for l in url]
			all_ppy = True
			for link in links:
				domain = get_tld(link, as_object=True).domain
				if domain != 'ppy':
					all_ppy = False

			if all_ppy:
				return

			log(msg=message, links=links)

			embed = discord.Embed(title="Don't send unknown links, please.", description="Talk to <@362162806101114882> or a whitelisted member if you need your link sent.") # @NoisNette#4205
			await message.channel.send(embed=embed)
			await message.delete()


if __name__ == '__main__':
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	load_whitelist()
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