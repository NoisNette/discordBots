import requests
from bs4 import BeautifulSoup

class Scraper:
	@staticmethod
	def getData(animeId):
		res = requests.get('https://zoro.to/' + animeId)
		soup = BeautifulSoup(res.content, 'html.parser')
		
		# get number of episodes
		stats = soup.find(attrs={'class': 'film-stats'})
		episodeRaw = [c.get_text() for c in stats.contents if 'Ep' in c.get_text()][0][3:].split(' / ')
		currentEpisode, maxEpisodes = map(int, episodeRaw)

		# get cover image url
		img = soup.find(attrs={'class': 'film-poster-img'})
		imgUrl = img.attrs['src']

		return {
			"currentEpisode": currentEpisode,
			"maxEpisodes": maxEpisodes,
			"imgUrl": imgUrl
		}
	
	@staticmethod
	def getCurrentEpisodesCount(animeId):
		res = requests.get('https://zoro.to/' + animeId)
		soup = BeautifulSoup(res.content, 'html.parser')

		stats = soup.find(attrs={'class': 'film-stats'})
		episodeCount = int([c.get_text() for c in stats.contents if 'Ep' in c.get_text()][0][3:].split(' / ')[0]) # i.e. "Ep 3 / 12", we want the "3"

		return episodeCount