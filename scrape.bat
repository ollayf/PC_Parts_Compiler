call .\venv\Scripts\activate.bat
echo Running NewEgg Scraper
py newegg_scraper.py
timeout 5
echo Running Amazon Scraper
py amazon_scraper.py
timeout 20
pause