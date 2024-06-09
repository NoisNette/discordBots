class WordsHelper:
	def __init__(self, dictionary_path: str, possible_path: str, word_index_path: str) -> None:
		self.dictionary_path = dictionary_path
		self.possible_path = possible_path
		self.word_index_path = word_index_path

		self.dictionary = []
		self.possible = []

		self.load_words()
	

	def load_words(self) -> None:
		with open(self.dictionary_path, 'r') as dct, open(self.possible_path, 'r') as poss:
			for w in dct.readlines():
				w = w.strip().upper()
				if w:
					self.dictionary.append(w)
			for w in poss.readlines():
				w = w.strip().upper()
				if w:
					self.possible.append(w)
	

	def is_valid_word(self, word: str) -> bool:
		word = word.upper()

		# binary search
		l, r = 0, len(self.dictionary)-1
		while l <= r:
			mid = (l + r) // 2
			if word == self.dictionary[mid]:
				return True
			elif word > self.dictionary[mid]:
				l = mid + 1
			else:
				r = mid - 1
		
		return False


	def get_new_word(self) -> str:
		with open(self.word_index_path, 'r') as file:
			idx = int(file.read())
		
		if idx < len(self.possible) - 1:
			word = self.possible[idx]
			idx += 1
		else:
			word = self.possible[0]
			idx = 0

		with open(self.word_index_path, 'w') as file:
			file.write(str(idx))
		
		return word.upper()


	def reset_word_idx(self, idx: int = 0) -> None:
		with open(self.word_index_path, 'w') as file:
			file.write(str(idx))