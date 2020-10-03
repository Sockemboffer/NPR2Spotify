# NPR2Spotify
Too much great music between segments that I never have time to dig for on their website. One of my first programming projects. Go easy on me.

## Problem
Back-of-the-envelope estimation: 7 song avg. per day, 2555 songs per year,  63,875 songs across 25 years. ~15 minutes to gather, create playlist, search and verify ~7 songs (actually hearing what NPR played vs what Spotify found.) 365 days * 15 minutes, around 90 hours for one year or roughly 2000 hours or roughly 95 days to catalog their songs into Spotify playlists. Eep!

## Solution
At the cost of accuracy in identifying songs, use python libraries to hopfully reduce the human effort required.

- *NPRPageParser.py* - Handles getting valid links, parsing HTML, and outputing to json files.

- *NPRSpotifySearch.py* - When fed interlude data, processes Spotify search responses and do some simple comparisons against what was found on NPR.

- *NPRPlaylistCreator.py* - Create a playlist for each day's songs and provide details about missing songs in to the playlist description.

## Shortfalls
There may be a lot of false positives and false negatives. In most cases it seems pretty spot-on but I've only compared about a months songs for some confidence in moving forward.

## Interesting learnings
- Just about anything I needed someone already had a library for
- HTML parsing is kinda ugly looking with xpath but works great!
- UTF-8 encoding
- Reading and writing to json
- Zfilling numbers
- Splitting strings
- List splitting
- How handy lambdas seem to be
- Robot.txt standard
- OAuth verifications
- Sorting lists
- Base64 jpg encoding
- OS directory navigation
- Git'ing
- VS Code

## Time to complete
I've bee
