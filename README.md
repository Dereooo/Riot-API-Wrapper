# Riot-API-Wrapper
Naive implementation of a wrapper for fetching data from Riot's Teamfight Tactics API

Motivation: The API keys supplied by Riot for the development stage of products have very low request rate limits (overall, a maximum of 100 requests every 2 minutes, for each server). However, for the product I was aiming at developing, I calculated that I would need up to hundreds of thousands of weekly requests based on the amount of data I needed. With that in mind, I created this nonstop script that fetchs TFT match history data from Riot's API and stores it in my local MongoDB database.

Usage: There are a few variables inside the script that need to be set for adjusting how the fetching happens. As is, when you run the script, the flow of the nonstop script is the following:

1. Creates 3 threads for americas, asia and europe server, which each have their own rate limits.
2. Requests a list of players from the highest rankings (challenger, grandmaster, master and top diamond tiers).
3. For each player, request their unique id and then request their match history.
4. For each match, check if they're in our database already, and if not, fecth its information and store it.

After attempting other formats, I found this was the optimal for my goal, which was to gather a large amount of match information, specifically from high elo players.

You should adapt this script if you have a different goal, but feel free to use my code as you wish, as long as you're complying with Riot's own set of rules.
