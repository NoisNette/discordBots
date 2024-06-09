import os, sys, json

class Loader:
	def __init__(self):
		self.anime_file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), f'../animes.txt')
		self.channels_file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), f'../channels.txt')
		self.animes = []
		self.channels = []
		self.update_animes()


	def get_animes(self):
		self.update_animes()
		return self.animes


	def add_anime(self, name, url):
		self.update_animes()
		urls = [anime[1].lower() for anime in self.animes]
		if url.lower() in urls:
			return -1

		self.animes.append((name, url))
		self.write_to_file(type='anime')


	def remove_anime(self, name):
		self.update_animes()
		names = [anime[0].lower() for anime in self.animes]
		if name.lower() in names:
			anime = self.animes.pop(names.index(name))
		else:
			return -1

		self.write_to_file(type='anime')
		return anime[0]


	def update_animes(self):
		with open(self.anime_file_path, 'r') as f:
			lines = f.readlines()

		for i in range(len(lines)): lines[i] = lines[i].strip()

		self.animes.clear()

		for i in range(0, len(lines)-1, 2):
			self.animes.append((lines[i], lines[i+1]))


	def get_episodes(self, anime):
		file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), f'../database/{anime[0]}.json')
		if os.path.exists(file_path):
			with open(file_path, 'r') as f:
				read_database = f.read()
		else:
			return

		return json.loads(read_database)


	def get_channels(self):
		self.update_channels()
		return self.channels


	def add_channel(self, channel):
		self.update_channels()

		if channel in self.channels:
			return -1

		self.channels.append(channel)
		self.write_to_file(type='channel')


	def remove_channel(self, channel):
		self.update_channels()

		if channel not in self.channels:
			return -1

		self.channels.remove(channel)
		self.write_to_file(type='channel')


	def update_channels(self):
		with open(self.channels_file_path, 'r') as f:
			lines = f.readlines()

		for i in range(len(lines)):
			lines[i] = lines[i].strip()

		self.channels.clear()

		for i in range(len(lines)):
			self.channels.append(int(lines[i]))


	def write_to_file(self, **kwargs):
		if kwargs['type'] == 'anime':
			open(self.anime_file_path, 'w').close() # Clears the file

			for anime in self.animes:
				with open(self.anime_file_path, 'a') as f:
					f.writelines([anime[0] + '\n', anime[1] + '\n'])

			self.update_animes()

		elif kwargs['type'] == 'channel':
			open(self.channels_file_path, 'w').close() # Clears the file

			for channel in self.channels:
				with open(self.channels_file_path, 'a') as f:
					f.write(str(channel) + '\n')

			self.update_channels()

		else:
			return