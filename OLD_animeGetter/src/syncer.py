import sys, os, requests, pydash, json, threading
from pyquery import PyQuery as pq
from loader import Loader

is_debug = False

class Syncer:
	def __init__(self, animes):
		self.found = {}
		self.animes = animes


	def extract_episodes(self, html):
		episodes = []
		base_url = 'https://animekisa.tv/'

		d = pq(html)
		for e in d('div.infoept2 div.centerv'):
			episodes.append(d(e).text())

		for e in d('img.posteri'):
			image_link = base_url + d(e).attr('src')

		return list(map(int, episodes[::-1])), image_link


	def get_episodes(self, url):
		r = requests.get(url)
		return self.extract_episodes(r.text)


	def sync_episodes(self, name, file_path, url):
		if os.path.exists(file_path):
			with open(file_path, 'r') as f:
				read_database = f.read()
		else: read_database = ''
		parsed_database = json.loads(read_database) if read_database else read_database

		episodes, image_link = self.get_episodes(url)

		if pydash.is_equal(parsed_database, episodes):
			return

		else:
			missing_episodes = pydash.difference_with(episodes, parsed_database, pydash.is_equal)
			number_of_episodes = len(missing_episodes)

			if number_of_episodes == 0:
				return

			self.found.update({name: (str(missing_episodes), url, image_link)})
			with open(file_path, 'w') as f:
				f.write(json.dumps(episodes))

			if is_debug:
				print(f'{name} has {number_of_episodes} new episode{"s" if number_of_episodes > 1 else ""}! {url}')


	def sync_animes(self):
		for anime in self.animes:
			file_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), f'../database/{anime[0]}.json')
			self.sync_episodes(anime[0], file_path, anime[1])

		if is_debug:
			threading.Timer(1, self.sync_animes).start()


	def reset_found(self):
		self.found = {}

	def get_found(self):
		return self.found


if __name__ == '__main__':
	is_debug = True
	loader = Loader()
	syncer = Syncer(loader.get_animes())
	print('Starting...')
	syncer.sync_animes()