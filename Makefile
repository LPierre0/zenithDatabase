all:
	source env/bin/activate && python3.12 src/scraper/item_scraper.py && python3.12 src/scraper/stats_scraper.py && src/scraper/build_scraper.py
	