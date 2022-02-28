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

submission_count = 0

def load_cities():
	cities = open(f'data/cities').read().split('\n')
	
	#remove empty city names
	cities = [city for city in cities if len(city) > 1]

	return cities

def query_submissions(reddit, sub):
	print(f"Querying hot submissions from 'r/{sub}'")
	r = reddit.subreddit(sub).hot(limit=150)
	return r

def get_city_mention_counts(cities, submissions):
	mentions = dict()

	# search in every submission
	for submission in submissions:
		global submission_count
		submission_count += 1

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
	nominatim = Nominatim(user_agent='ukraine-war-heatmap')

	location = nominatim.geocode(
		{
			'city': city
		},
		language='en',
		country_codes='ua'
	)

	s = f"Querying location for '{city}'"
	if location.raw:
		print(f'[OKAY] {s}')
		return (float(location.raw['lat']), float(location.raw['lon']))
	else:
		print(f'[FAIL] {s}')
		return None

def create_heatmap(mapdata):
	map = fl.Map(
		tiles='Stamen Terrain',
		location=[49.3956617, 30.9809839], zoom_start=6
	)

	# timestamps, sort ascending
	index = list(mapdata.keys())
	index.sort()

	map.add_child(
		HeatMapWithTime(
			name='Timeline',
			data=list(mapdata.values()),
			index=index,
			radius=0.5,
			scale_radius=True
		)
	)

	# map.add_child(
	# 	HeatMap(
	# 		name='Now',
	# 		blur=25,
	# 		radius=40,
	# 		data=list(mapdata.values())[-1]
	# 	)
	# )

	map.save('index.html')

def merge_dicts(a, b):
	return { k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b) }

def query_mentions_from_subreddits(reddit, cities, subreddits):
	mentions = dict()
	for subreddit in subreddits:
		submissions = query_submissions(reddit, subreddit)
		mentions = merge_dicts(mentions, get_city_mention_counts(cities, submissions))
	return mentions

def load_historic_data(directory):
	data = {}
	for file in os.listdir(directory):
		f = os.path.join(directory, file)
		if os.path.isfile(f):
			data[file] = json.load(open(f, 'r'))

	return data

def main():
	load_dotenv()

	# init praw
	reddit = praw.Reddit(
		client_id=os.getenv('REDDIT_API_ID'),
		client_secret=os.getenv('REDDIT_API_SECRET'),
		username=os.getenv('REDDIT_USERNAME'),
		password=os.getenv('REDDIT_PASSWORD'),
		user_agent='ukraine war hotmap'
	)

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
	now = datetime.utcnow().strftime('%d.%m.%y %H:%M')
	json.dump(mentions, open(f'data/historic/{now} UTC', 'w'))

	# print debug info
	print(f'Searched in {submission_count} submissions and found:')
	print(json.dumps(mentions, indent=4, sort_keys=True))

	mapdata = {}

	# for city in mentions.keys():
	# 	l = get_city_location(city)
	# 	if l is not None:
	# 		locations.append(l)
	# 		weights.append(mentions[city])

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
				d = [l[0], l[1], math.sqrt(data[time][city] / max(data[time].values()))]
				if time in mapdata:
					mapdata[time].append(d)
				else:
					mapdata[time] = [d]

	create_heatmap(mapdata)

if __name__ == '__main__':
	main()
