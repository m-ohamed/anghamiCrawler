from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv

def crawl():
    global name

    'The name is the name of the file to be saved, and the UID of the user.'
    name = "FileName"
    UID = "UID"

    'This is to get the percentage of artists in similar artists.'
    getArtistsPercentage(UID)

    'The following is what could be crawled, each one should be seperately crawled.'
    'For getRecentlyPlayed() a 0 crawls the recently played, and any other number crawls the most played songs.'
    'For getPlaylists() a 0 crawls the users created playlists, and any other number crawls the followed playlists.'
    #getLikedSongs(UID)
    #getFollowedArtists(UID)
    #getRecentlyPlayed(UID, 0)
    #getRecentlyPlayed(UID, 1)
    #getPlaylists(UID, 0)
    #getPlaylists(UID, 1)



'The following method is used to load the page and press the \'More\' button on the page until the button is gone, and' \
'therefore, no more could be loaded.'
def doWork(url):
    driver.get(url)

    while True:
        try:
            'The time delay is added here since sometimes the dynamic content (javascript content) takes longer to load' \
            'than the page itself.'
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button = driver.find_element_by_link_text("More")
            button.click()
        except Exception:
            break

'The liked songs page is loaded and the list of songs liked is saved and then looped on. Each song is then added' \
'and its name, number of likes, and number of plays are saved.'
def getLikedSongs(UID):
    global name
    global res

    'The name of the columns'
    res = [["Song Name","Artist","Likes","Plays"]]

    'Load the page and click on the \'More\' button'
    doWork("https://play.anghami.com/profile/" + UID + "/24")

    'The following 2 lines are used to get the content of the page and parse it to HTML to be used further on'
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    'Finds all the content that has in its tags: <\'data-ng-bind\': \'::item.itemTitle\'> which correspond to song HREFs' \
    'on Anghami'
    #songHref = soup.find_all('a', {'data-ng-bind': '::item.itemTitle'})
    songHref = soup.find_all('i', {'data-ng-class': '{\'liked icon-liked\':item.liked}'})

    i = 0
    while (i < len(songHref)):
        try:
            'The following line loads the page of each song'
            #driver.get("https://play.anghami.com" + songHref[i].get('data-ng-href'))
            driver.get("https://play.anghami.com/song/" + songHref[i].get('data-id'))


            'Again, a timer here is used because of loading issues, see line 33'
            time.sleep(2)

            html = driver.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')

            'The following 3 lines each extract the tags that contain the specified content, each tag corresponds to Song Name,' \
            'Artist Name, and the final tag has number of Song Likes and Plays'
            songName = soup.find_all('span',{'data-ng-bind-html':'songInfo.title'})
            artistName = soup.find_all('a',{'ng-bind':'songInfo.artist'})
            songLikes = soup.find_all('span', {'class': 'button-label'})

            'The following 17 lines are there to convert from K to thousands and from M to millions since if a user has more' \
            'than 1000 likes for example Anghami saves it as 1K'
            numOfLikes = numOfPlays = 0
            likes = songLikes[0].get_text()[:-7]
            plays = songLikes[1].get_text()[:-6]

            if(likes[-1:] == 'M'):
                numOfLikes = float(likes[:-1])*1000000
            elif(likes[-1:] == 'K'):
                numOfLikes = float(likes[:-1])*1000
            else:
                numOfLikes = float(likes)

            if (plays[-1:] == 'M'):
                numOfPlays = float(plays[:-1]) * 1000000
            elif (plays[-1:] == 'K'):
                numOfPlays = float(plays[:-1]) * 1000
            else:
                numOfPlays = float(plays)

            'The following 3 lines are used to add to the previously created list that will further on be saved as a CSV file,' \
            'the row is extended first to add the data to it and then appeneded in order to be shown as needed when output'
            row = []
            row.extend((songName[0].get_text(),artistName[0].get_text(),numOfLikes,numOfPlays))
            res.append(row)

        except Exception as e:
            'A try statement is added and if an error occurs it is caught here and printed in order to show that an error happened'
            'then a continue statement is used in order to retry the same iteration since it is highly unlikely to get an error' \
            'from this method'
            print("First place: " + str(e))
            continue

        i += 1

    'The following couple of lines are then used to output the result as a CSV file. The name is set in the crawl() method.'
    f = open(name + "'s Liked Songs.csv", 'w', newline='', encoding="utf-8")
    with f:
        writer = csv.writer(f)
        writer.writerows(res)
    f.close()

'The followed artists page is loaded, and all the followed artists are saved. They are then looped on, and for each artist' \
'his/her name, number of followers, number of plays, and the genres are added and saved. Also, after the genres the similar artists' \
'are also added, this was mainly done for testing purposes'
def getFollowedArtists(UID):
    global name
    global res
    res = [["Artist Name","Followers","Plays","Genre 1","Genre 2","Genre 3","Genre 4"]]

    doWork("https://play.anghami.com/profile/" + UID + "/6")
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    i = 0
    'Get the HREFs of all the artists'
    artistHref = soup.find_all('a', {'data-ng-if':'::$ctrl.type !== "artist-list"'})
    errorCount = 0

    while (i < len(artistHref)):
        try:
            driver.get("https://play.anghami.com" + artistHref[i].get('href'))
            time.sleep(3)
            html = driver.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')
            artistName = soup.find_all('div',{'data-ng-bind':'artist.artistName'})
            artistInfo = soup.find_all('li',{'class':'subtitle'})

            similarArtistsRows = []
            if(len(soup.find_all('a',{'href':artistHref[i].get('href')+'/10'})) == 0):
                similarArtistsRows.append("N/A")
            else:
                driver.get("https://play.anghami.com" + artistHref[i].get('href') + "/10")
                time.sleep(3)
                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                simArtistsList = soup.find_all('div',{'class':'title'})
                j = 0
                while(j < len(simArtistsList)):
                    similarArtistsRows.append(simArtistsList[j].get_text())
                    j += 1

            numOfFollowers = numOfPlays = 0
            followers = artistInfo[0].get_text()[:-10]
            plays = (artistInfo[1].get_text()[:-6])[2:]

            if (followers[-1:] == 'M'):
                numOfFollowers = float(followers[:-1]) * 1000000
            elif (followers[-1:] == 'K'):
                numOfFollowers = float(followers[:-1]) * 1000
            elif(artistInfo[0].get_text()[-9:].replace(' ','') == "Follower"):
                numOfFollowers = float(artistInfo[0].get_text()[:-9])
            else:
                numOfFollowers = float(followers)

            if (plays[-1:] == 'M'):
                numOfPlays = float(plays[:-1]) * 1000000
            elif (plays[-1:] == 'K'):
                numOfPlays = float(plays[:-1]) * 1000
            else:
                numOfPlays = float(plays)
            row = []
            row.extend((artistName[0].get_text(), numOfFollowers, numOfPlays))
        except Exception as e:
            'An error count here is added since an error could occur like the song not being available in your country, and to' \
            'make the crawler fully automated it tries the same page for 10 times, if an error keeps happening each time it means ' \
            'something is wrong, and therefore, that page is ignored.'
            errorCount += 1
            if (errorCount >= 10):
                i += 1
                errorCount = 0

            print("First error: ",e)
            continue

        'The following 21 lines are used to get the genre of the artist'
        while True:
            try:
                driver.get("https://www.allmusic.com/search/all/" + artistName[0].get_text())
                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')
                'Since not all artists are found due to many reasons, for example an artist might only be known inside' \
                'the country, if no tags were found then \'N\A\' is added'
                if (len(soup.find_all('div', {'class': 'genres'})) == 0):
                    genres = ["N/A"]
                else:
                    artistGenre = soup.find_all('div', {'class': 'genres'})
                    genres = artistGenre[0].get_text().replace("  ","").replace('\n',"").split(",")

                'Only 4 genres are added, in the case there are more than 4 the rest are ignored, and if there is less than' \
                '4 the rest is filled with \'N\A\''
                j = 0
                while(j < 4):
                    if j >= len(genres):
                        row.append("N/A")
                    else:
                        row.append(genres[j])
                    j += 1
            except Exception as e:
                print("No artists found: " + str(e))
                continue
            break

        res.append(row + similarArtistsRows)
        errorCount = 0
        i += 1

    f = open(name + "'s Followed Artists.csv", 'w', newline='', encoding="utf-8")
    with f:
        writer = csv.writer(f)
        writer.writerows(res)
    f.close()

'It is first checked whether the number (num) passed is a 0 or something else, if it is a 0 the recently played songs is' \
'loaded and crawled, otherwise the most played songs is loaded and crawled. The next step is to get each songs and artists HREFs.' \
'The song HREFs are then looped and all the names, artists, likes, and plays of each song are saved. Finally, the artists HREFs are looped' \
'to remove any duplicates, then the unique set of artists is looped and the similar artists are saved, again, this is done for testing purposes'
def getRecentlyPlayed(UID, num):
    global name
    global res
    res = [["Song Name", "Artist","Likes", "Plays"]]

    if(num == 0):
        doWork("https://play.anghami.com/profile/" + UID + "/9")
    else:
        doWork("https://play.anghami.com/profile/" + UID + "/7")

    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    artistDetails = soup.find_all('a', {'data-ng-bind': '::item.itemSubtitle'})
    songHref = soup.find_all('i', {'data-ng-class': '{\'liked icon-liked\':item.liked}'})

    errorCount = 0
    i = 0
    while (i < len(songHref)):
        row = []
        try:
            #driver.get("https://play.anghami.com" + songHref[i].get('data-ng-href'))
            driver.get("https://play.anghami.com/song/" + songHref[i].get('data-id'))
            html = driver.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')

            songName = soup.find_all('span', {'data-ng-bind-html': 'songInfo.title'})
            artistName = soup.find_all('a', {'ng-bind': 'songInfo.artist'})
            songLikes = soup.find_all('span', {'class': 'button-label'})

            numOfLikes = numOfPlays = 0
            likes = songLikes[0].get_text()[:-7]
            plays = songLikes[1].get_text()[:-6]

            if (likes[-1:] == 'M'):
                numOfLikes = float(likes[:-1]) * 1000000
            elif (likes[-1:] == 'K'):
                numOfLikes = float(likes[:-1]) * 1000
            else:
                numOfLikes = float(likes)

            if (plays[-1:] == 'M'):
                numOfPlays = float(plays[:-1]) * 1000000
            elif (plays[-1:] == 'K'):
                numOfPlays = float(plays[:-1]) * 1000
            else:
                numOfPlays = float(plays)

            row.extend((songName[0].get_text(),artistName[0].get_text(),numOfLikes,numOfPlays))
            res.append(row)


        except Exception as e:
            errorCount += 1
            if (errorCount >= 10):
                i += 1
                errorCount = 0

            print("Error here: " + str(e))
            continue

        errorCount = 0
        i += 1

    res.append(["Artist","Similar Artists"])

    'The following 5 lines are used to create a set of only the unique artists, and therefore, removing any duplicate artists, since the' \
    'user can listen to different songs that belong to the same artist'
    uniqueArtists = set()
    for artist in artistDetails:
        artistHref = artist.get('href')
        if artistHref not in uniqueArtists:
            uniqueArtists.add(artistHref)

    for artist in uniqueArtists:
        row = []
        while True:
            try:
                driver.get("https://play.anghami.com" + artist)
                time.sleep(3)
                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                artistName = soup.find_all('div', {'data-ng-bind': 'artist.artistName'})
                row.append(artistName[0].get_text())

                break

            except Exception as e:
                print("Error at uniqueArtists: " + str(e))
                continue

        if (len(soup.find_all('a', {'href': artist + '/10'})) == 0):
            row.append("N/A")
        else:
            driver.get("https://play.anghami.com" + artist + "/10")
            time.sleep(3)
            html = driver.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')

            simArtistsList = soup.find_all('div', {'class': 'title'})
            j = 0
            while (j < len(simArtistsList)):
                row.append(simArtistsList[j].get_text())
                j += 1

        res.append(row)

    if(num == 0):
        f = open(name + "'s Recently Played Songs.csv", 'w', newline = '', encoding="utf-8")
    else:
        f = open(name + "'s Most Played Songs.csv", 'w', newline='', encoding="utf-8")

    with f:
        writer = csv.writer(f)
        writer.writerows(res)
    f.close()


'It is first checked whether the number (num) passed is a 0 or something else, if it is a 0 the created playlists are crawled' \
'otherwise the followed playlists are crawled. Initially, the HREFs of the playlists are obtained and then looped in each playlist' \
'the list of songs is then obtained and also looped in order to get their name, artist, number of likes, and number of plays.' \
'Then each playlist is output into a different CSV file on its own, with its number in its name, for example, the first playlist' \
'that belongs to a user named John Doe will be named \'JohnDoe\'s Playlist # 1\''
def getPlaylists(UID, num):
    global name
    global res
    res = [[]]
    if(num == 0):
        doWork("https://play.anghami.com/profile/" + UID + "/5")
    else:
        doWork("https://play.anghami.com/profile/" + UID + "/10")

    time.sleep(3)
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    'The following if statement checks whether or not the user has any followed playlists, in the case where someone ' \
    'mistakenly crawls the followed playists page while there is actually no followed playlists, a small message will be' \
    'displayed to tell the user that there are no followed playlists.'
    if (len(soup.find_all('a', {'ng-href': '/profile/' + UID + '/10'})) == 0) and (num == 1):
        print("No followed playlists")
        return

    listOfPlaylists = soup.find_all('a', {'class': 'playlistItem'})

    i = 0
    while (i < len(listOfPlaylists)):
        res = [["Song Name", "Artist", "Likes", "Plays"]]

        try:
            doWork("https://play.anghami.com" + listOfPlaylists[i].get('href'))
            html = driver.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')

            songHref = soup.find_all('a', {'data-ng-bind': '::(item.itemTitle)'})

        except Exception as e:
            print("1st loop " + str(e))
            continue

        j = 0
        errorCount = 0
        while (j < len(songHref)):
            try:
                driver.get("https://play.anghami.com" + songHref[j].get('data-ng-href'))
                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                songName = soup.find_all('span', {'data-ng-bind-html': 'songInfo.title'})
                artistName = soup.find_all('span', {'data-ng-bind': '::songInfo.artist'})
                songLikes = soup.find_all('span', {'class': 'button-label'})

                numOfLikes = numOfPlays = 0
                likes = songLikes[0].get_text()[:-6]
                plays = songLikes[1].get_text()[:-6]

                if (likes[-1:] == 'M'):
                    numOfLikes = float(likes[:-1]) * 1000000
                elif (likes[-1:] == 'K'):
                    numOfLikes = float(likes[:-1]) * 1000
                else:
                    numOfLikes = float(likes)

                if (plays[-1:] == 'M'):
                    numOfPlays = float(plays[:-1]) * 1000000
                elif (plays[-1:] == 'K'):
                    numOfPlays = float(plays[:-1]) * 1000
                else:
                    numOfPlays = float(plays)

                res.append([songName[0].get_text(),artistName[0].get_text(),numOfLikes,numOfPlays])

            except Exception as e:
                errorCount += 1
                print("2nd loop " + str(e))

                if(errorCount >= 10):
                    errorCount = 0
                    j += 1

                continue

            errorCount = 0
            j += 1

        writeError = 0

        while True:
            try:
                if(num == 0):
                    f = open(name + "'s Playlist #" + str(i + 1) + ".csv", 'w', newline='', encoding="utf-8")
                else:
                    f = open(name + "'s Followed Playlist #" + str(i + 1) + ".csv", 'w', newline='', encoding="utf-8")

                with f:
                    writer = csv.writer(f)
                    writer.writerows(res)
                    f.close()

                i += 1

            except Exception:
                writeError += 1
                if(writeError >= 10):
                    print("Error: couldn't write playlist #" + str(i))
                    break
                continue
            break


'The users profile page is first loaded, and is then checked whether or not the user has a Most Played page, if it is ' \
'available it is then loaded and all the artists in it are added to a set without any duplicates. The same is then done' \
'for the Recently Played, Liked Songs, and Followed Artists pages. All the similar artists of those artists are then added' \
'to a seperate list. Finally the number of of unique artists that were found in the similar artists set is counted, and ' \
'the number of unique artists, number of similar artists, and the number of unique artists that appeared in the similar ' \
'artists list are output, alongside a percentage. The percentage output is the number of times a unique artist appeared in' \
'similar artists list divided by the number of unique artists.'
def getArtistsPercentage(UID):
    while True:
        try:
            driver.get("https://play.anghami.com/profile/" + UID)

            html = driver.execute_script("return document.documentElement.outerHTML")
            soup = BeautifulSoup(html, 'html.parser')

            uniqueArtists = set()
            extraUniqueArtists = set()
            similarArtists = set()

            if (len(soup.find_all('a', {'href': '/profile/' + UID + '/7'})) != 0):
                doWork("https://play.anghami.com/profile/" + UID + "/7")

                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                artistDetails = soup.find_all('a', {'data-ng-bind': '::item.itemSubtitle'})

                for artist in artistDetails:
                    artistHref = artist.get('href')
                    if artistHref not in uniqueArtists:
                        uniqueArtists.add(artistHref)

            else:
                print("Error: No Most Played found!")

            if (len(soup.find_all('a', {'href': '/profile/' + UID + '/9'})) != 0):
                doWork("https://play.anghami.com/profile/" + UID + "/9")

                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                artistDetails = soup.find_all('a', {'data-ng-bind': '::item.itemSubtitle'})

                for artist in artistDetails:
                    artistHref = artist.get('href')
                    if artistHref not in uniqueArtists:
                        uniqueArtists.add(artistHref)

            else:
                print("Error: No Recently Played found!")

            if (len(soup.find_all('a', {'href': '/profile/' + UID + '/24'})) != 0):
                doWork("https://play.anghami.com/profile/" + UID + "/24")

                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                artistDetails = soup.find_all('a', {'data-ng-bind': '::item.itemSubtitle'})

                for artist in artistDetails:
                    artistHref = artist.get('href')
                    if artistHref not in uniqueArtists:
                        uniqueArtists.add(artistHref)

            else:
                print("Error: No Liked Songs found!")

            if(len(soup.find_all('a', {'href': '/profile/' + UID + '/6'})) != 0):
                doWork("https://play.anghami.com/profile/" + UID + "/6")

                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                artistDetails = soup.find_all('a', {'data-ng-if': '::$ctrl.type !== "artist-list"'})

                for artist in artistDetails:
                    artistHref = artist.get('href')
                    if artistHref not in uniqueArtists:
                        uniqueArtists.add(artistHref)

            else:
                print("Error: No Followed Artists found!")

            for artist in uniqueArtists:
                driver.get("https://play.anghami.com" + artist)
                time.sleep(3)
                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                'The following if statement is used to check whether the page belongs to more than one artist at the same' \
                'time or not, if it does then each artist is seperately added to a new set which will be dealt with later on'
                if(len(soup.find_all('a', {'data-ng-if': '::$ctrl.type !== "artist-list"'})) != 0):
                    artistDetails = soup.find_all('a', {'data-ng-if': '::$ctrl.type !== "artist-list"'})

                    for member in artistDetails:
                        artistHref = member.get('href')
                        if artistHref not in extraUniqueArtists:
                            extraUniqueArtists.add(artistHref)


                if(len(soup.find_all('a', {'href': '' + artist + '/10'})) != 0):
                    driver.get("https://play.anghami.com" + artist + "/10")

                    time.sleep(3)

                    html = driver.execute_script("return document.documentElement.outerHTML")
                    soup = BeautifulSoup(html, 'html.parser')

                    simArtistsList = soup.find_all('div', {'class': 'artist-item'})

                    for musician in simArtistsList:
                        artistHref = musician.get('href')
                        if artistHref not in similarArtists:
                            similarArtists.add(artistHref)

            'Extra artists from the unique artists set are dealth with here. They are added to the unique artists list (if' \
            'they are not already in it) and dealt with like the other entries in the unique artists set'
            for artist in extraUniqueArtists:
                if artist not in uniqueArtists:
                    uniqueArtists.add(artist)

                driver.get("https://play.anghami.com" + artist)
                time.sleep(3)
                html = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(html, 'html.parser')

                if (len(soup.find_all('a', {'href': artist + '/10'})) != 0):
                    driver.get("https://play.anghami.com" + artist + "/10")

                    time.sleep(3)

                    html = driver.execute_script("return document.documentElement.outerHTML")
                    soup = BeautifulSoup(html, 'html.parser')

                    simArtistsList = soup.find_all('div', {'class': 'artist-item'})

                    for member in simArtistsList:
                        artistHref = member.get('href')
                        if artistHref not in similarArtists:
                            similarArtists.add(artistHref)

            count = 0
            for artist in uniqueArtists:
                if artist in similarArtists:
                    count += 1

            print("Total unique artists: ", len(uniqueArtists))
            print("Total similar artists: ", len(similarArtists))
            print("Total unique artists in similar artists: ", count)
            uniquePercentage = (count / len(uniqueArtists)) * 100
            print("Percentage of count in unique artists will be: ", uniquePercentage, "%")

        except Exception as e:
            print("Error at dispersion: ", e)
            continue


'This was a method used mainly for experimentation which mainly gets the number of unique artists listened to, number of' \
'artists followed, and the number of artists followed that were recently listened to'
def experiment(UID):

    doWork("https://play.anghami.com/profile/" + UID + "/9")
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    artistDetails = soup.find_all('a', {'data-ng-bind': '::item.itemSubtitle'})

    uniqueArtists = set()
    for artist in artistDetails:
        artistHref = artist.get('href')
        if artistHref not in uniqueArtists:
            uniqueArtists.add(artistHref)

    print("Number of Unique Artists in Recently Played: ", len(uniqueArtists))

    doWork("https://play.anghami.com/profile/" + UID + "/6")
    html = driver.execute_script("return document.documentElement.outerHTML")
    soup = BeautifulSoup(html, 'html.parser')

    artistHref = soup.find_all('a', {'data-ng-if': '::$ctrl.type !== "artist-list"'})

    print("Number of Followed Artists: ", len(artistHref))

    count = 0

    for artist in artistHref:
        if (artist.get('href') in uniqueArtists):
            count += 1

    print("Number of artists Followed that was recently listened to: ", count)


'The following 2 lines are used to mute the sound from the driver as sometimes the songs play automatically while crawling.'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--mute-audio")

'The following line is used to start the driver and apply the previously set options.'
driver = webdriver.Chrome(chrome_options=chrome_options)

'Initializing the name and the res (result) variables.'
name = ""
res = ""

'Calling the crawl() method'
crawl()

'Closing the driver once it has finished crawling to avoid issues that may involve memory leakage'
driver.close()
driver.quit()
