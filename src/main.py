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

import praw
from geopy.geocoders import Nominatim
import folium as fl
from folium.plugins import HeatMapWithTime, HeatMap
import json
from datetime import datetime
import os
import math
from dotenv import load_dotenv
import Html
from uuid import uuid1
from functools import cmp_to_key

TIME_FORMAT = '%Y-%m-%d %H:%M UTC'
SUBMISSION_QUERY_LIMIT = 300

submission_count = 0

class RedditNews:
	def __init__(self, title, score, source):
		self.title = title
		self.score = score
		self.source = source

def load_cities():
	cities = open(f'data/cities').read().split('\n')
	# Remove empty city names
	return [city for city in cities if len(city) > 1]

def query_submissions(reddit, sub):
	print(f"Querying hot submissions from 'r/{sub}'")
	r = reddit.subreddit(sub).hot(limit=SUBMISSION_QUERY_LIMIT)
	return r

def permalink_to_url(permalink):
	return 'https://www.reddit.com' + permalink

def query_news(reddit, source='worldnews'):
	submissions = query_submissions(reddit, source)

	# Words to look out for in the submission titles. NOTE: should be all lowercase
	trigger_words = ['ukraine', 'russia', 'zelensky', 'putin', 'belarus']

	news = list()

	for submission in submissions:
		# no self posts, only links to real news articles
		is_self_post = submission.url == permalink_to_url(submission.permalink)
		if submission.score < 10000 or is_self_post:
			continue

		# Check all the trigger words
		relevant = False
		for trigger_word in trigger_words:
			if trigger_word in submission.title.lower():
				relevant = True

		if relevant:
			news.append(
				RedditNews(
					submission.title,
					submission.score,
					submission.url
				)
			)

	return news

def get_city_mention_counts(cities, submissions):
	mentions = dict()

	# search in every submission
	for submission in submissions:
		global submission_count
		submission_count += 1

		# filter 'bad' submissions
		if submission.score < 100:
			continue

		# go through each city and check if it's in the submission title
		for city in cities:
			found = False

			# some cities are made up of multiple words, check the words too
			# for word in city.split(' '):
			# 	if word.lower() in submission.title.lower():
			# 		found = True

			# check the whole city name
			if city.lower() in submission.title.lower():
				found = True

			# add to mentions if the city is in the submission title
			if found:
				# print(f'\t{city}\n')
				if city in mentions:
					mentions[city] += 1
				else:
					mentions[city] = 1
	
	return mentions

def query_city_location(city):
	s = f"Querying location for '{city}'"

	# Nominatim can't find the location for some cities, but we know they exists so translate them
	# to something Nominatim can find
	translations = {
		'borodyanka': 'borodianka'
	}

	if city.lower() in translations:
		city = translations[city.lower()]

	try:
		nominatim = Nominatim(user_agent='ukraine-war-heatmap')
		location = nominatim.geocode(city, country_codes='ua')
		location = [float(location.raw['lat']), float(location.raw['lon'])]

		print(f'[OKAY] {s}')
		return location

	except: # TODO(ruarq): find out what exception Nominatim throws
		print(f'[FAIL] {s}')
		return None

def generate_heatmap(mapdata):
	map = fl.Map(
		tiles='Stamen Terrain',
		location=[49.3956617, 30.9809839], zoom_start=6
	)

	# timestamps, sort ascending
	index = list(mapdata.keys())

	# convert to datetime object (so they get sorted correctly)
	for i in range(len(index)):
		index[i] = datetime.strptime(index[i], TIME_FORMAT)

	# sort
	index.sort()

	# convert back to string
	for i in range(len(index)):
		index[i] = str(index[i].strftime(TIME_FORMAT))

	HeatMapWithTime(
		name='Heatmap',
		data=list(mapdata.values()),
		index=index,
		radius=0.5,
		scale_radius=True,
		start_index=len(index)
	).add_to(map)

	fl.TileLayer('OpenStreetMap').add_to(map)
	fl.LayerControl().add_to(map)

	# Yes. I know. We have to do it like that.
	# map._repr_html_() will produce a stupid bug
	# where the map keeps reloading in itself.
	filename = 'map_' + str(uuid1()) + '.html'
	map.save(filename)
	file = open(filename, 'r')
	content = file.read()
	file.close()
	os.remove(filename)
	return content

def merge_dicts(a, b):
	return { k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b) }

def query_mentions_from_subreddits(reddit, cities, subreddits):
	mentions = dict()
	for subreddit in subreddits:
		try:
			submissions = query_submissions(reddit, subreddit)
			mentions = merge_dicts(mentions, get_city_mention_counts(cities, submissions))
		except:
			print(f'Something bad happened while querying mentions from r/{subreddit}')

	return mentions

def load_historic_data(directory):
	data = {}
	for file in os.listdir(directory):
		f = os.path.join(directory, file)
		if os.path.isfile(f):
			data[file] = json.load(open(f, 'r'))

	return data

def generate_news_column(reddit):
	subreddit = 'worldnews'
	news = query_news(reddit, subreddit)

	html_news_list = list()

	# sort news by upvotes, most upvotes should be first
	news.sort(key=cmp_to_key(lambda a, b : b.score - a.score))

	for n in news:
		html_news_list.append(
			Html.Li(
				Html.Div(
					content=[
						Html.Div(n.title),
						Html.Div(
							[
								Html.A(
									content=[
										Html.Div(
											[
												Html.Img(
													src='link-mode-light.png',
													alt='hyperlink image',
													Class='link-img'
												),
												'Source'
											],
											Class='link-div'
										)
									],
									href=n.source
								),
								Html.Div(
									[
										Html.Img(src='upvote.png', alt='upvote', Class='upvote-img'),
										f'&nbsp;{int((n.score / 1000) + 0.5)}K'
									],
									Class='score-div'
								)
							],
							Class='element-info-div'
						)
					],
					Class='element-content-div'
				)
			)
		)

	return Html.Div(
		Html.Div(
			[
				Html.Div(
					content=[
						Html.Img(
							src='https://www.redditinc.com/assets/images/site/reddit-logo.png',
							alt='reddit logo',
							Class='reddit-logo-img'
						),
						Html.H2(
							[
								'&nbsp;',
								Html.A(content=f'r/{subreddit}',
									href=f'https://www.reddit.com/r/{subreddit}'
								)
							]
						)
					],
					Class='reddit-logo'
				),
				Html.Ul(
					content=html_news_list,
					Class='news-column-list'
				)
			],
			Class='news-column-div'
		),
		Class='news-column'
	)

def main():
	load_dotenv()
	
	now = datetime.utcnow().strftime(TIME_FORMAT)

	# init praw
	reddit = praw.Reddit(
		client_id=os.getenv('REDDIT_API_ID'),
		client_secret=os.getenv('REDDIT_API_SECRET'),
		username=os.getenv('REDDIT_USERNAME'),
		password=os.getenv('REDDIT_PASSWORD'),
		user_agent='ukraine war hotmap'
	)

	# query mentions of cities
	cities = load_cities()
	mentions = query_mentions_from_subreddits(
		reddit,
		cities,
		[
			'CombatFootage',
			'UkraineWarVideoReport',
			'ukraine',
			'worldnews',
			'UkrainevRussia',
			'UkraineInvasionVideos',
			'UkrainianConflict',
			'Ukraine_UA',
			'UkraineWarReports'
		]
	)

	# dump for historic data and heatmap with time
	json.dump(mentions, open(f'data/historic/{now}', 'w'))

	# print debug info
	print(f'Searched in {submission_count} submissions and found:')
	print(json.dumps(mentions, indent=4, sort_keys=True))

	mapdata = {}
	locations = {}
	data = load_historic_data('data/historic')

	# compile mapdata for folium
	for time in data.keys():
		# get the city locations for each city
		for city in data[time].keys():
			l = 0

			# check if the city location was already queried (we want to minimize nominatim api requests)
			if city in locations:
				l = locations[city]
			else:
				l = query_city_location(city)
			
			locations[city] = l

			# add location to the mapdata if queried successfully
			if l is not None:
				d = [
					round(l[0], 2),
					round(l[1], 2),
					round(math.sqrt(data[time][city] / max(data[time].values())), 2)
				]
				if time in mapdata:
					mapdata[time].append(d)
				else:
					mapdata[time] = [d]

	heatmap_html = generate_heatmap(mapdata)

	file = open('index.html', 'w')
	file.write(
		Html.Html(
			[
				Html.Head(
					[
						Html.Meta(charset='utf-8'),
						Html.Meta(name='description', content='Watch a live heatmap to see where the war in ukraine is most active.'),
						Html.Meta(name='author', content='ruarq'),
						Html.Meta(name='copyright', content='ruarq'),
						Html.Meta(name='language', content='English'),
						Html.Meta(name='keywords', content='ukraine, ukraine invasion, ukraine heatmap, ukraine live heatmap, map, heatmap, ukraine map, ukraine live map, live map, help ukraine, ruarq, github.io, ukraine conflict, conflict, ukraine war, war, russia, ukraine russia, ukraine russia war'),
						Html.Meta(name='revisit-after', content='1 days'),
						Html.Title('Ukraine War Map/Heatmap by ruarq'),
						Html.Link(rel='stylesheet', type='text/css', href='style.css')
					]
				),
				Html.Body(
					[
						Html.Div(
							content=heatmap_html,
							Class='leaflet-map'
						),
						generate_news_column(reddit)
					],
					Class='main-body'
				)
			]
		).dumps()
	)

if __name__ == '__main__':
	main()
