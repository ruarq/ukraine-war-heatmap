# Ukraine War Map/Heatmap
This project takes submissions about Ukraine from subreddits like r/CombatFootage, r/UkraineWarVideoReport, r/ukraine, r/worldnews, r/UkraineInvasionVideos and r/UkrainevRussia and translates them into a heatmap where most of the stuff related to the war in Ukraine is happening.
You can see that heatmap [here](https://ruarq.github.io/ukraine-war-heatmap/). It updates every 30 minutes.

## Support Ukraine
- Read [this](https://www.reddit.com/r/ukraine/comments/s6g5un/want_to_support_ukraine_heres_a_list_of_charities/)
	reddit post from [r/ukraine](https://www.reddit.com/r/ukraine) for a big list of charities to donate to
- Do not spread misinformation and do report misinformation
- If you have the infrastructure or just for fun, you can help the
	[IT ARMY of Ukraine](https://t.me/itarmyofukraine2022) to fight against russia (at your own risk)
- Checkout [all the other projects](https://github.com/topics/ukraine/) on github related to ukraine and the invasion

## How to run
1. Install dependencies with `pip install dotenv geopy praw`

	**NOTE:** You will also have to install my [folium fork](https://github.com/python-visualization/folium).

2. Create `.env` file and populate it with:
	```ini
	REDDIT_USERNAME=<your reddit username>
	REDDIT_PASSWORD=<your reddit password>
	REDDIT_API_ID=<your reddit application id>
	REDDIT_API_SECRECT=<your reddit application secret>
	```
3. Create the empty directory `data/historic`
4. Run with `python src/main.py`
