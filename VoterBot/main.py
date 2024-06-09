import discord, secret, sys, os, subprocess, urllib

token = secret.OAUTH_TOKEN
nois_id = secret.NOISNETTE_ID
four_id = secret.FOUR_ID

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents, activity=discord.Activity(type=discord.ActivityType.listening, name='v!help'))
prefix = 'v!'

vote_started = False
choices_votes = {}
choices = []
people_who_voted = set()
voting_session_author = None


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


def reset_voting():
	global vote_started, choices_votes, choices, people_who_voted, voting_session_author
	vote_started = False
	choices_votes = {}
	choices = []
	people_who_voted = set()
	voting_session_author = None


async def show_results(msg):
	embed_msg = discord.Embed(title='Results', color=0x00ff00)

	for choice, votes in choices_votes.items():
		total_votes = sum(choices_votes.values())
		if total_votes:
			embed_msg.add_field(name=choice, value=f'Votes: {votes} ({round((votes/total_votes)*100)}%)', inline=False)
		else:
			embed_msg.add_field(name=choice, value=f'Votes: {votes}', inline=False)
	
	embed_msg.set_footer(text=f'Started by {voting_session_author}')

	await msg.channel.send(embed=embed_msg)
		

@client.event
async def on_ready():
	print('Started...')
	info_channel = client.get_channel(805519445962260490)
	await info_channel.send(f'Started on {sys.platform}.')

@client.event
async def on_message(message):
	global vote_started, choices_votes, choices, people_who_voted, voting_session_author
	author = message.author
	author_name = author.display_name
	content = message.content.strip().replace('  ', ' ')


	if message.content.lower().startswith('!forcequit'):
		if message.author.id in [nois_id, four_id] and client.user in message.mentions:
			await forcequit()

	if message.content.lower().startswith('!restart'):
		if message.author.id in [nois_id, four_id] and (client.user in message.mentions or '-all' in message.content.lower()):
			subprocess.call([sys.executable, os.path.realpath(__file__)])
			sys.exit()


	if is_command(message, 'help'):
		embed_msg = discord.Embed(
			title='VoterBot - Help',
			color=0x00ff00
		)
		embed_msg.add_field(name='v!startvote, v!sv', value='Starts a voting session.', inline=False)
		embed_msg.add_field(name='v!endvote', value='Ends the voting session and displays the results.', inline=False)
		embed_msg.add_field(name='v!results, v!res', value='Displays the results.', inline=False)
		embed_msg.add_field(name='v!help', value='Sends this message to you.', inline=False)
		
		embed_msg.set_footer(text='VoterBot made by NoisNette')

		channel = await message.author.create_dm()
		await channel.send(embed=embed_msg)


	if is_command(message, 'vote'):
		if vote_started:
			try: vote = content.split()[1]
			except:
				await message.channel.send('Invalid vote!')
				return

			if author not in people_who_voted:
				if vote in choices:
					choices_votes[vote] += 1
					people_who_voted.add(author)

					print(f'{author_name} voted for {vote}.')
					await message.channel.send(f'{author_name} voted for {vote}.')
		
				else:
					await message.channel.send('Invalid vote!')

		else:
			await message.channel.send('Voting hasn\'t started yet!')


	if is_command(message, 'startvote', 'sv'):
		if not vote_started:
			choices = content.split()[1:]
			if len(choices) >= 2:
				for choice in choices:
					choices_votes.update({choice: 0})

				voting_session_author = message.author
				vote_started = True
				print(f'Voting has started by {voting_session_author} with choices: {", ".join(choices)}.')
				await message.channel.send('Voting started, you can vote with `v!vote {choice}`.')
			
			else:
				await message.channel.send('More than one choice required!')
		
		else:
			await message.channel.send('Voting has already started.')


	if is_command(message, 'results', 'res'):
		if vote_started:
			await show_results(message)

		else:
			await message.channel.send('Voting hasn\'t started yet!')


	if is_command(message, 'endvote'):
		if vote_started:
			if message.author == voting_session_author:
				print('Voting has ended.')
				await message.channel.send(f'{author_name} ended the vote.')
				await show_results(message)
				reset_voting()

			else:
				await message.channel.send(f'Only the voting session creator, {voting_session_author.display_name} can end this voting session.')

		else:
			await message.channel.send('Voting hasn\'t started yet!')


if __name__ == '__main__':
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