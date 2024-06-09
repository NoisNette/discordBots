from random import choices
import wordsHelper

class Word:
	def __init__(self, word: str, player_id: int) -> None:
		self.word = word.lower()
		self.player_id = player_id

		self.prefix = self.word[:2] if all(not self.word.endswith(l) for l in ['lj', 'nj', 'dž']) else self.word[:3]
		self.suffix = self.word[-2:] if all(not self.word.endswith(l) for l in ['lj', 'nj', 'dž']) else self.word[-3:]
		self.underlined = f'{self.word[:-len(self.suffix)]}__{self.suffix}__'.upper()

		self.available_words = wordsHelper.get_words(self.suffix)

		self.alternate_choices = choices(self.available_words, k=5) if self.available_words else []

	def __str__(self) -> str:
		return self.word

	def __len__(self) -> int:
		return len(self.word)