from scraper import Scraper

scr = Scraper()
for competitorList in scr.scrape():
    print(competitorList)
