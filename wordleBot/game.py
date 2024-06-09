from imageHelper import ImageHelper
from wordsHelper import WordsHelper

class Game:
	def __init__(self, words_dictionary_path: str, possible_path: str, word_index_path: str, template_path: str, result_path: str) -> None:
		self.wordsHelper = WordsHelper(words_dictionary_path, possible_path, word_index_path)
		self.imageHelper = ImageHelper(template_path, result_path)

		self.target_word = self.wordsHelper.get_new_word()
		self.words = []
		self.used_letters = set()
	

	def play_word(self, word: str) -> tuple[int, set[str] | None]:
		res = {}
		correct = False
		if self.wordsHelper.is_valid_word(word):
			self.words.append(word)
			self.used_letters |= set(word)
			self.imageHelper.draw(self.words, self.target_word)

			if word == self.target_word:
				correct = True
			
			res['status'] = True
		
		else:
			res['status'] = False
		
		res['correct'] = correct
		res['letters'] = sorted(self.used_letters)
		return res


	def is_game_over(self) -> bool:
		return len(self.words) >= 6 or self.target_word in self.words

	
	def draw_empty(self):
		self.imageHelper.draw([], '')
	

	def reset_word_idx(self) -> None:
		self.wordsHelper.reset_word_idx()