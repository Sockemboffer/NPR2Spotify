# todo: re-check parsed page for missing tracks to research
    # todo: check if playlist exsists
    # todo: notify when previously not found track is found
# todo: organize queries

def get_spotify_uri(self, artistList):
    # building uri list to use later in playlist fill-up
    jsonData = self.get_json_data()
    query = ""
    for dic in artistList:
        if "Interlude Artist" in dic:
            artists = dic.get("Interlude Artist")
            #print(len(artists))
        if "Interlude Song" in dic:
            track = dic.get("Interlude Song")
            #print(track)
    # todo: call to NPRSpotifySearch
    return self.all_uri_info

# Create several ways to chop up and search for target track
# Initial search raw track and 1st artist name
query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
        parse.quote('track:' + '"' + track + '"' + ' ' + 'artist:"' + artists[0] + '"'))
print(track + " by: " + artists[0])
response = requests.get(
    query,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotipyUserToken)})
response_json = response.json()
#print("=====================================" + json.dumps(response_json, indent=4) + r'\n')

if response_json["tracks"]["total"] == 0:
    # strip [] from track names and research literal & WITH artist search
    trackNoBrackets = track.translate({ord(i): None for i in '[]'})
    #print("TrackNoBrackets: " + trackNoBrackets)
    query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
            parse.quote('track:' + '"' + trackNoBrackets + '"' + ' ' + 'artist:"' + artists[0] + '"'))
    print(trackNoBrackets + " by: " + artists[0])
    response = requests.get(
    query,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotipyUserToken)})
    response_json = response.json()
    #print("NO BRACKETS: " + json.dumps(response_json, indent=4) + '\n')

if response_json["tracks"]["total"] == 0:
    # strip () from track name, search literal track name + artist type
    trackNoBracketsAndBraces = trackNoBrackets.translate({ord(i): None for i in '()'})
    query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
            parse.quote('"' + trackNoBracketsAndBraces + '"' + ' ' + 'artist:"' + artists[0] + '"'))
    print(trackNoBracketsAndBraces + ' ' + 'by: ' + artists[0])
    response = requests.get(
    query,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotipyUserToken)})
    response_json = response.json()
    #print("NO BRACKETS AND NO ARTIST: " + json.dumps(response_json, indent=4) + '\n')

if response_json["tracks"]["total"] == 0:
    # strip () from track name, search literal track name + NO artist
    # When no artist used, double check found track's artist matches npr page artist
    query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(
            parse.quote('"' + trackNoBracketsAndBraces + '"'))
    print(trackNoBracketsAndBraces + ' ' + 'by: None')
    response = requests.get(
    query,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotipyUserToken)})
    response_json = response.json()
    if (response_json["tracks"]["total"] == 0):
        print(trackNoBracketsAndBraces + ' ' + 'by: None')
    else:
        print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: "
        + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> "
        + trackNoBracketsAndBraces + " by: " + artists[0])

if response_json["tracks"]["total"] == 0:
    # strip words from songs like featuring, edit, original, etc.
    stopwords = ['feat.','original','edit','featuring','feature']
    querywords = trackNoBracketsAndBraces.split()
    resultwords  = [word for word in querywords if word.lower() not in stopwords]
    self.result = ' '.join(resultwords)
    query = "https://api.spotify.com/v1/search?q={}&type=track%2Cartist&market=US&limit=5".format(
            parse.quote('"' + self.result + '"' + ' ' + 'artist:"' + artists[0] + '"'))
    print(self.result + ' ' + 'by: ' + artists[0])
    response = requests.get(
    query,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotipyUserToken)})
    response_json = response.json()
    #print("NO BRACKETS AND NO ARTIST: " + json.dumps(response_json, indent=4) + '\n')

if response_json["tracks"]["total"] == 0:
    # strip words from songs like featuring, edit, original, etc. + search WITHOUT type artist
    # When no artist used, double check found track's artist matches npr page artist
    query = "https://api.spotify.com/v1/search?q={}&type=track&market=US&limit=5".format(
            parse.quote('"' + self.result + '"'))
    response = requests.get(
    query,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(spotipyUserToken)})
    response_json = response.json()
    if (response_json["tracks"]["total"] == 0):
        print(self.result + ' ' + 'by: None')
    else:
        print("<!check!> " + response_json["tracks"]["items"][0]["name"] + " by: "
        + response_json["tracks"]["items"][0]["artists"][0]["name"] + " <=?=> "
        + self.result+ " by: " + artists[0])

# Function to print found or missing status (todo: decouple from json file update)
# Added missed track scan date check back into json
# No more search configurations left
if (response_json["tracks"]["total"] == 0) or (response_json["tracks"]["items"][0]["artists"][0]["name"] != artists[0]):
    missedTrack = " ••••••> " + "MISSING: " + track + " by: " + ", ".join(artists) + '\n'
    self.missedTracksList.append(missedTrack)
    print(missedTrack)
    with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
        for entry in jsonData:
            for value in entry:
                if isinstance(value, dict):
                    #print(value)
                    for k, v in value.items():
                        if v == track:
                            # print(k)
                            for k, v in value.items():
                                if k == "Last Checked":
                                    dt = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
                                    v = dt
                                    value[k] = v
                                    #print(k)
        #print(response)
        json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
        json_file.close()
    #print("NoBracketsAndSplit: " + json.dumps(response_json, indent=4) + '\n')
else:
    # found artist and need to put it's uri back into json file
    print("| Found Track: " + str(response_json["tracks"]["items"][0]["name"])  + ", by: "
        + response_json["tracks"]["items"][0]["artists"][0]["name"] + '\n')
    self.all_uri_info.append(response_json["tracks"]["items"][0]["uri"])
    with open('NPRPageParser.json', 'w', encoding='utf-8') as json_file:
        for entry in jsonData:
            for value in entry:
                if isinstance(value, dict):
                    #print(value)
                    for k, v in value.items():
                        if v == track:
                            # print(k)
                            for k, v in value.items():
                                if k == "Spotify URI":
                                    v = response_json["tracks"]["items"][0]["uri"]
                                    value[k] = v
                                    #print(k)
                                if k == "Last Checked":
                                    self.songLastChecked = str(datetime.datetime.now().__format__("%Y-%m-%d %H:%M:%S"))
                                    value[k] = self.songLastChecked
                                    #print(k)
                            
        #print(jsonData)
        json.dump(jsonData, json_file, ensure_ascii=False, indent=4)
        json_file.close()