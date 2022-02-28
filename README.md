# Ukraine War Map/Heatmap
This project takes submissions about Ukraine from subreddits like r/CombatFootage, r/UkraineWarVideoReport, r/ukraine, r/worldnews, r/UkraineInvasionVideos and r/UkrainevRussia and translates them into a heatmap where most of the stuff related to the war in Ukraine is happening.
You can see that heatmap [here](https://ruarq.github.io/ukraine-war-heatmap/). It updates every 30 minutes.

## How to run
1. Install dependencies with `pip install dotenv folium geopy praw`
2. Create `.env` file and populate it with:
	```ini
	REDDIT_USERNAME=<your reddit username>
	REDDIT_PASSWORD=<your reddit password>
	REDDIT_API_ID=<your reddit application id>
	REDDIT_API_SECRECT=<your reddit application secret>
	```
3. Create the empty directory `data/historic`
4. Run with `python src/main.py`
