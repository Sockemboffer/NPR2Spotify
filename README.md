![npr2spotifylogo](https://github.com/Sockemboffer/NPR2Spotify/blob/master/Edition%20Logos/npr2spotify_twitter_header.png)
# NPR2Spotify
Generally, this program parses NPR Morning Edition, Weekend Edition, and All Things Considered and creates a Spotify [Playlist](https://open.spotify.com/user/1tnm7cyegqffdjtsz6mt1ozcl?si=oQepJ6nKTVmZ6rYdRaEDTQ/) for that day's interlude music. It's not perfect at matching for various reasons like human error and my ad-hoc matching logic. Assumes you have a free spotify developer account, uses OAuth2, and spotify user permissions to create/modify playlists.

Morning and Weekend Edition playlists all public: [NPR MoWeEd](https://open.spotify.com/user/1tnm7cyegqffdjtsz6mt1ozcl?si=c8f7240012154a88)

All Things Considered playlists for 1996 now public: [NPR ATC](https://open.spotify.com/user/31eljfpkmh4v6xux7mu36s32cmzu?si=760639e4c5344320)

Follow on Twitter: [@NPR2Spotify](https://twitter.com/MoWeEd2Spotify)

**/showname Article Data/** - Each day's output for each year

**/showname Article Link Cache/** - Output that feeds day links into Main.py below.

**NPRPageParser.py** - Takes in an NPR show link and saves out to json files various info about that day including any track information.

**NPRPlaylistCreator.py** - Various methods to create, update description, add tracks.

**NPRSpotifySearch.py** - My system for trying to get a decent amount of search results to then parse and find a good track match.

**Main.py** - Entry point (that's gross looking.)

----------------------------------------------------------------------------------------------------
- [ ] Create a dependiencies manifest.
- [ ] Make more pythonic all around.
- [ ] Automate to run daily.
- [x] On going, All Things Considered Archive
----------------------------------------------------------------------------------------------------

## Problem
Would take a long time (*like, 95ish days non-stop for one person*) to go verify and create playlists for NPR's Morning and Weekend Edition interludes. While this little project took near 2 years to complete, I was able to learn some more about programming and Python.

One of my first programming projects. I'm new to GitHub and Python.

Suggestions welcomed. Go easy on me and Enjoy!

## Donate to NPR today!
Support your local [NPR station](https://www.npr.org/donations/support) today.

[Morning Edition](https://www.npr.org/programs/morning-edition/)

[Weekend Edition Saturday](https://www.npr.org/programs/weekend-edition-saturday/)

[Weekend Edition Sunday](https://www.npr.org/programs/weekend-edition-sunday/)
[All Things Considered](https://www.npr.org/programs/all-things-considered/)
## Thanks
My pal at [MBGameDev](https://github.com/mbgamedev/) for holding my hand a couple-few times.

**AND**

[TheComeUpCode](https://github.com/TheComeUpCode/) for giving me my first steps into Web APIs! [Check out her helpful videos.](https://www.youtube.com/channel/UC-bFgwL_kFKLZA60AiB-CCQ/)

🌎👩🏽‍🤝‍👩🏿👨🏻‍🤝‍👨🏼👫🏻🧑🏻‍🤝‍🧑🏾👭🏼👫🏽👭👬🏿👬🏼🧑🏻‍🤝‍🧑🏿🧑‍🤝‍🧑👩🏾‍🤝‍👩🏼🧑🏿‍🤝‍🧑🏿👫👩🏻‍🤝‍👩🏿👬🧑🏽‍🤝‍🧑🏾👫🏿📻
