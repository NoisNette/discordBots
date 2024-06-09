import discord, secret, sys, subprocess, os, time, urllib

token = secret.OAUTH_TOKEN
nois_id = secret.NOISNETTE_ID
four_id = secret.FOUR_ID

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name='t!help'))
prefix = 't!'

tournament_contestant_role_name = 'Tourney Contestant'

contestants_added = False
contestants = set()
contestant_role = None
ctrl_msg_ids = []


whitelist = set()
def load_whitelist():
	global whitelist
	with open('whitelist.txt', 'r') as f:
		whitelist = set(int(l.strip()) for l in f.readlines())


purge_channels = set()
def load_purge_channels():
	global purge_channels
	with open('purge_channels.txt', 'r') as f:
		purge_channels = set(int(l.strip()) for l in f.readlines())


def is_command(msg, command, aux_command=None):
	if aux_command != None:
		return msg.content.lower().startswith(prefix + command) or msg.content.lower().startswith(prefix + aux_command)
	else:
		return msg.content.lower().startswith(prefix + command)


async def forcequit():
	print('Stopping...')

	info_channel = client.get_channel(805519445962260490)
	await info_channel.send('Stopped...')

	sys.exit()


async def is_by_whitelisted(message):
	global whitelist
	load_whitelist()
	if (message.author.id not in whitelist) and (message.author.id not in [nois_id, four_id]):	
		channel = await message.author.create_dm()
		await channel.send('You don\'t have permission to use this command!\nAsk <@!362162806101114882> for permission.')

		return False
	return True


async def silence(message, thumbs_up=False):
	if contestants_added:
		error_happened = False
		for contestant in contestants:
			try: await contestant.edit(mute=True, deafen=True)
			except discord.errors.HTTPException: 
				await message.channel.send(f'{contestant.name} not in voice chat!', delete_after=2)
				error_happened = True

		if not error_happened:
			if thumbs_up:
				await message.add_reaction('👍')

	else:
		await message.channel.send('Contestants haven\'t been added yet!', delete_after=2)


async def unsilence(message, thumbs_up=False):
	if contestants_added:
		error_happened = False
		for contestant in contestants:
			try: await contestant.edit(mute=False, deafen=False)
			except discord.errors.HTTPException: 
				await message.channel.send(f'{contestant.name} not in voice chat!', delete_after=2)
				error_happened = True

		if not error_happened:
			if thumbs_up:
				await message.add_reaction('👍')

	else:
		await message.channel.send('Contestants haven\'t been added yet!', delete_after=2)


async def removerole(message, thumbs_up=False):
	global contestants_added, contestants

	if contestants_added:		
		for contestant in contestants:
			if contestant.voice != None:
				await contestant.edit(mute=False, deafen=False)
		
		contestants_added = False
		contestants.clear()
		ctrl_msg_ids.clear()
		await contestant_role.delete()

		if thumbs_up:
			await message.add_reaction('👍')

		if message.channel.id in purge_channels:
			wait_time = 3
			await message.channel.send(f'All messages in this channel will be deleted in {wait_time} seconds!')
			time.sleep(wait_time)
			await message.channel.purge()

	else:
		await message.channel.send('Contestants haven\'t been added yet!', delete_after=2)


async def send_controls(message):
	msg = await message.channel.send(embed=discord.Embed(title='React with  🔈  to silence.\nReact with  🔊  to unsilence.\nReact with  ❌  to remove the role.'))

	await msg.add_reaction('🔈')
	await msg.add_reaction('🔊')
	await msg.add_reaction('❌')
	ctrl_msg_ids.append(msg.id)


@client.event
async def on_ready():
	print('Started...')
	info_channel = client.get_channel(805519445962260490)
	await info_channel.send(f'Started on {sys.platform}.')

@client.event
async def on_message(message):
	global contestants_added, contestants, contestant_role, whitelist

	if message.author == client.user or message.channel.type in [discord.ChannelType.private, discord.ChannelType.group]:
		return

	role_names = [role.name for role in message.guild.roles]
	if tournament_contestant_role_name not in role_names:
		await message.guild.create_role(
			name=tournament_contestant_role_name,
			color=discord.Colour.from_rgb(255, 200, 0), # Yellow
			mentionable=True,
			reason='Role created so the TourneyHelper bot can work its magic, ask NoisNette#4205 for details.' # @NoisNette#4205
		)

	contestant_role = discord.utils.get(message.guild.roles, name=tournament_contestant_role_name)

	if message.content.lower().startswith('!forcequit'):
		if message.author.id in [nois_id, four_id] and client.user in message.mentions:
			await forcequit()

	if message.content.lower().startswith('!restart'):
		if message.author.id in [nois_id, four_id] and (client.user in message.mentions or '-all' in message.content.lower()):
			subprocess.call([sys.executable, os.path.realpath(__file__)])
			sys.exit()


	if message.content.lower().startswith(prefix + 'whitelist') and message.author.id in [nois_id, four_id]:
		load_whitelist()
		try: 
			arg = message.content.lower().split(' ')[1]
			if arg == 'add':
				if message.mentions != []:
					added = []
					for user in message.mentions:
						if user.id not in whitelist:
							whitelist.add(user.id)

							with open('whitelist.txt', 'a') as f:
								f.write(str(user.id) + '\n')

							added.append(user)
					
					if added:
						await message.channel.send(f'Added user{"s" if len(added) > 1 else ""} {", ".join(user.name for user in added)} to the whitelist!', delete_after=2)
					
					await message.delete()

			elif arg == 'remove':
				if message.mentions != []:
					removed = []
					for user in message.mentions:
						if user.id in whitelist:
							whitelist.remove(user.id)

							with open('whitelist.txt', 'w') as f:
								for user_id in whitelist:
									f.write(str(user_id) + '\n')

							removed.append(user)

					if removed:
						await message.channel.send(f'Removed user{"s" if len(removed) > 1 else ""} {", ".join(user.name for user in removed)} from the whitelist!', delete_after=3)

					await message.delete()

		except IndexError:
			users = []
			for user_id in whitelist:
				user = await client.fetch_user(user_id)
				users.append(user.name)
			
			if users:
				await message.channel.send(f'Whitelist: {", ".join(users)}.')
			else:
				await message.channel.send('Whitelist empty!')


	if message.content.lower().startswith(prefix + 'purge add') and message.author.id in [nois_id, four_id]:
		load_purge_channels()
		channel_id = message.channel.id
		if channel_id not in purge_channels:
			purge_channels.add(channel_id)

			with open('purge_channels.txt', 'a') as f:
				f.write(str(channel_id) + '\n')

			await message.channel.send('Channel added to purge list.', delete_after=3)
		
		else:
			await message.channel.send('Channel already in purge list.', delete_after=3)
		await message.delete()


	if message.content.lower().startswith(prefix + 'purge remove') and message.author.id in [nois_id, four_id]:
		load_purge_channels()
		channel_id = message.channel.id
		if channel_id in purge_channels:
			purge_channels.remove(channel_id)
			with open('purge_channels.txt', 'w') as f:
				for channel_id in purge_channels:
					f.write(str(channel_id) + '\n')

			await message.channel.send('Channel removed from purge list.', delete_after=3)
		
		else:
			await message.channel.send('Channel not in purge list.', delete_after=3)

		await message.delete()


	if is_command(message, 'help') and await is_by_whitelisted(message):
		embed_msg = discord.Embed(
			title='TourneyHelper - Help',
			color=0x00ff00
		)
		embed_msg.add_field(name='t!setcontestants, t!sc', value='Creates and assigns the Tourney Contestant role to the mentioned members.', inline=False)
		embed_msg.add_field(name='t!silence, t!sl', value='Deafens and mutes members with the Tourney Contestant role, if any.', inline=False)
		embed_msg.add_field(name='t!unsilence, t!usl', value='Uneafens and unmutes members with the Tourney Contestant role, if any.', inline=False)
		embed_msg.add_field(name='t!removerole, t!rr', value='Deletes the Tourney Contestant role from the server, and if enabled, deletes all messages in the channel.', inline=False)
		embed_msg.add_field(name='t!controls, t!ctrl', value='Sends a message to which members can react to to use other commands more easily.', inline=False)
		embed_msg.add_field(name='t!help', value='Sends this message to you.', inline=False)
		
		embed_msg.set_footer(text='TourneyHelper made by NoisNette')

		channel = await message.author.create_dm()
		await channel.send(embed=embed_msg)


	if is_command(message, 'setcontestants', 'sc') and await is_by_whitelisted(message):
		if tournament_contestant_role_name not in role_names:
			await message.guild.create_role(
				name=tournament_contestant_role_name,
				color=0xffcc00, # Yellow
				mentionable=True,
				reason='Role created so the TourneyHelper bot can work its magic, ask <@!362162806101114882> for details.' # @NoisNette#4205
			)

		contestants = contestants.union(set(message.mentions))

		for contestant in contestants:
			await contestant.add_roles(contestant_role)

		if contestants:
			await message.channel.send(f'{len(contestants)} contestant{"s" if len(contestants) > 1 else ""} added ({", ".join(map(str, contestants))})')
			contestants_added = True

			await send_controls(message)

		else:
			await message.channel.send('No members found with those usernames.')


	if is_command(message, 'silence', 'sl') and await is_by_whitelisted(message):
		await silence(message, True)


	if is_command(message, 'unsilence', 'usl') and await is_by_whitelisted(message):
		await unsilence(message, True)

	
	if is_command(message, 'controls', 'ctrl') and await is_by_whitelisted(message):
		await send_controls(message)


	if is_command(message, 'removerole', 'rr') and await is_by_whitelisted(message):
		await removerole(message, True)


@client.event
async def on_reaction_add(reaction, user):
	if user != client.user and reaction.message.id in ctrl_msg_ids and user.id in whitelist:
		if str(reaction) == '🔈':
			await silence(reaction.message)
			await reaction.remove(user)
		
		elif str(reaction) == '🔊':
			await unsilence(reaction.message)
			await reaction.remove(user)

		elif str(reaction) == '❌':
			await reaction.message.clear_reactions()
			await reaction.message.add_reaction('✅')
			await removerole(reaction.message)


if __name__ == '__main__':
	os.chdir(os.path.dirname(os.path.realpath(__file__)))
	load_whitelist()
	load_purge_channels()
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
	
	client.run(token)