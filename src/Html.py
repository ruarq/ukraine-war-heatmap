# MIT License
# 
# Copyright (c) 2022 ruarq
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class Element:
	def __init__(self, tag, attributes=dict()):
		self._tag = tag
		self.content = ''
		self._attributes = attributes
		self._has_closing_tag = True

	def __setitem__(self, key, value):
		self._attributes[key] = value

	def dumps(self):
		s = f'<{self._tag} '
		for attribute in self._attributes:
			s += f'{attribute.lower()}="{self._attributes[attribute]}" '

		if self._has_closing_tag:
			s += '>'
			if type(self.content) is list:
				for elem in self.content:
					s += str(elem)
			elif self.content is not None:
				s += str(self.content)
			s += f'</{self._tag}>'
		else:
			s += '/>'

		return s

	def __str__(self):
		return self.dumps()

class Html(Element):
	def __init__(self, content=None):
		super().__init__('html')
		self.content = content

class Head(Element):
	def __init__(self, content=None):
		super().__init__('head')
		self.content = content

class Meta(Element):
	def __init__(self, **attributes):
		super().__init__('meta', attributes)
		self._has_closing_tag = False

class Link(Element):
	def __init__(self, **attributes):
		super().__init__('link', attributes)
		self._has_closing_tag = False

class Title(Element):
	def __init__(self, content=None):
		super().__init__('title')
		self.content = content

class Body(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('body', attributes)
		self.content = content

class Div(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('div', attributes)
		self.content = content

class H2(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('h2', attributes)
		self.content = content

class Img(Element):
	def __init__(self, **attributes):
		super().__init__('img', attributes)
		self._has_closing_tag = False

class A(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('a', attributes)
		self.content = content

class Ul(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('ul', attributes)
		self.content = content

class Li(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('li', attributes)
		self.content = content

class Span(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('span', attributes)
		self.content = content

class Picture(Element):
	def __init__(self, content=None, **attributes):
		super().__init__('picture', attributes)
		self.content = content

class Source(Element):
	def __init__(self, **attributes):
		super().__init__('source', attributes)
		self._has_closing_tag = False
