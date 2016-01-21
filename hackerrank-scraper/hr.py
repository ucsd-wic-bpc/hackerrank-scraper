"""
hr.py

A sample script to show how to use scraper.py
"""
from scraper import Competitor, Scraper

competitorDict = {} # Maps competitors username to problems solved
leaderboardScraper = Scraper()
while True:
    for competitor in Competitor.get_competitor_list(leaderboardScraper):
        if competitor.username not in competitorDict:
            competitorDict[competitor.username] = competitor.completedCount
            print("COMPETITOR {} NOW BEING TRACKED".format(competitor.username))
        elif not competitor.completedCount == competitorDict[competitor.username]:
            print("COMPETITOR {} HAS COMPLETED {} ADDITIONAL PROBLEMS. TOTAL={}".format(
                competitor.username, competitor.completedCount - competitorDict[competitor.username],
                competitor.completedCount))
