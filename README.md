# NPR2Spotify
Too much great music between segments that I never have time to dig for on their website. One of my first programming projects. Built a scrapper program to parse every Morning and Weekend Edition article for the interlude music data. I then creating public playlists on Spotify for others to enjoy. Go easy on me.

## Problem
Back-of-the-envelope estimation: 7 song avg. per day, 2555 songs per year,  63,875 songs across 25 years. ~15 minutes to gather, create playlist, search and verify ~7 day's songs (actually hearing what NPR played vs what Spotify found.) 365 days * 15 minutes, around 90 hours for one year and roughly 2000 hours or 95 days to catalog their songs into Spotify playlists. Eep!

## Solution
At the cost of accuracy in identifying songs, use python libraries to hopfully reduce the human effort required.

*NPRPageParser.py* - Handles finding valid archive links to cache into json files. Read's cached links from those json files to parse each day's article for various info including the interlude data to also store into json files.

*NPRSpotifySearch.py* - When fed interlude data, processes Spotify search responses and do some simple comparisons against what was found on NPR.

*NPRPlaylistCreator.py* - Create a playlist for each day's article interlude songs that were found to be matches and provide some details about any missing songs into the playlist description.

## Shortfalls
There may be a lot of false positives and false negatives. In most cases it seems pretty spot-on but I've only compared about a months songs for some confidence in moving forward.

## Time to complete
I've bee
