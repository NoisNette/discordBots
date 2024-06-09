import os, sys, json

class FileHelper:
	ANIMES_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../data/animes.json')
	CHANNELS_PATH = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '../data/channels.json')

	@staticmethod
	def saveAnime(anime):
		with open(FileHelper.ANIMES_PATH, 'r') as f:
			data = json.loads(f.read())
		
		animeIds = [a['id'] for a in data]
		if anime['id'] in animeIds:
			raise KeyError
		
		data.append(anime)
		with open(FileHelper.ANIMES_PATH, 'w') as f:
			f.write(json.dumps(data, indent=2))

	@staticmethod
	def updateAnime(anime):
		with open(FileHelper.ANIMES_PATH, 'r') as f:
			data = json.loads(f.read())

		filteredData = [a for a in data if a['id'] != anime['id']]
		filteredData.append(anime)
		
		with open(FileHelper.ANIMES_PATH, 'w') as f:
			f.write(json.dumps(filteredData, indent=2))
	
	@staticmethod
	def removeAnime(animeName):
		with open(FileHelper.ANIMES_PATH, 'r') as f:
			data = json.loads(f.read())
		
		animeNames = [a['name'] for a in data]
		if animeName not in animeNames:
			raise KeyError

		data = [a for a in data if a['name'] != animeName]
		with open(FileHelper.ANIMES_PATH, 'w') as f:
			f.write(json.dumps(data, indent=2))
	
	@staticmethod
	def getAllAnimes():
		with open(FileHelper.ANIMES_PATH, 'r') as f:
			data = json.loads(f.read())

		return data

	@staticmethod
	def saveChannel(channel):
		with open(FileHelper.CHANNELS_PATH, 'r') as f:
			data = json.loads(f.read())
		
		channelIds = [c['id'] for c in data]
		if channel['id'] in channelIds:
			raise KeyError
		
		data.append(channel)
		with open(FileHelper.CHANNELS_PATH, 'w') as f:
			f.write(json.dumps(data, indent=2))

	@staticmethod
	def removeChannel(channelId):
		with open(FileHelper.CHANNELS_PATH, 'r') as f:
			data = json.loads(f.read())
		
		channelIds = [c['id'] for c in data]
		if channelId not in channelIds:
			raise KeyError
		
		data = [c for c in data if c['id'] != channelId]
		with open(FileHelper.CHANNELS_PATH, 'w') as f:
			f.write(json.dumps(data, indent=2))


	@staticmethod
	def getAllChannels():
		with open(FileHelper.CHANNELS_PATH, 'r') as f:
			data = json.loads(f.read())

		return data