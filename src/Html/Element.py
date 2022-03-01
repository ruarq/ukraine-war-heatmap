class Element:
	def __init__(self, tag):
		self._tag = tag
		self.content = ''
		self._attributes = dict()
		self._has_closing_tag = True

	def __setitem__(self, key, value):
		self._attributes[key] = value

	def __str__(self):
		s = f'<{self._tag} '
		for attribute in self._attributes:
			s += f'{attribute}="{self._attributes[attribute]}"'

		if self._has_closing_tag:
			s += '>'
			s += self.content
			s += f'</{self._tag}>'
		else:
			s += '/>'

		return s
