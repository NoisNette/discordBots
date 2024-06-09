from typing import List
import requests, codecs
from bs4 import BeautifulSoup
from random import choice, choices

letters = ['a', 'b', 'c', 'č', 'ć', 'd', 'dž', 'đ', 'e', 'f', 
		   'g', 'h', 'i', 'j', 'k', 'l', 'lj', 'm', 'n', 'nj',
		   'o', 'p', 'r', 's', 'š', 't', 'u', 'v', 'z', 'ž'
]

baseUrl = 'http://hr.words-finder.com/index.php'


def get_words(prefix: str) -> List[str]:
	res = requests.get(f'{baseUrl}?begin={prefix}')
	soup = BeautifulSoup(res.content, 'html.parser', from_encoding='utf-8')

	try:
		td = soup.find('td', attrs={'class': 'normalrow', 'width': '79%'})
		table = td.find('table')
		content = table.find('tr').find('td')
		for br in content.find_all('br'):
			br.replace_with('\n')
	except AttributeError:
		return []

	text = content.get_text()
	text = text[text.find('\n'):].strip().split('\n')

	return [w for w in text if w not in ['', '\n']]


def get_prefix() -> str:
	p = ''.join(choices(letters, k=2))
	while len(get_words(p)) == 0:
		p = ''.join(choices(letters, k=2))
	
	return p


def choose_new_word() -> str:
	prefix = get_prefix()
	words = get_words(prefix)
	word = choice(words)
	
	suffix = word[-2:] if all(not word.endswith(l) for l in ['lj', 'nj', 'dž']) else word[-3:]
	while len(get_words(suffix)) == 0:
		prefix = get_prefix()
		words = get_words(prefix)
		word = choice(words)
		suffix = word[-2:] if all(not word.endswith(l) for l in ['lj', 'nj', 'dž']) else word[-3:]
	
	return word


def save_words(w: List[str]) -> None:
	file = codecs.open('words.txt', 'w', 'utf-8')
	
	for line in w:
		file.write(line + '\n')

	file.close()