class ChannelHelper:
	def __init__(self, channels_path: str) -> None:
		self.channels = []
		self.channels_path = channels_path
	

	def get_channels(self) -> list[str]:
		self.update_channels()
		return self.channels


	def add_channel(self, channel: str) -> int | None:
		self.update_channels()

		if channel in self.channels:
			return -1

		self.channels.append(channel)
		self.write_to_file()


	def remove_channel(self, channel: str) -> int | None:
		self.update_channels()

		if channel not in self.channels:
			return -1
		
		self.channels.remove(channel)
		self.write_to_file()


	def update_channels(self) -> None:
		with open(self.channels_path, 'r') as f:
			lines = f.readlines()

		self.channels.clear()

		for i in range(len(lines)):
			self.channels.append(int(lines[i].strip()))


	def write_to_file(self):
		open(self.channels_path, 'w').close() # clears the file

		with open(self.channels_path, 'w') as f:
			for channel in self.channels:
				f.write(f'{channel}\n')
		
		self.update_channels()