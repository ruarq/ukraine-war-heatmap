from Element import Element

class Link(Element):
	def __init__(self):
		super().__init__('link')
		self._has_closing_tag = False
