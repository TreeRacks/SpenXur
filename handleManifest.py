import requests, zipfile, os, pickle, json, sqlite3

def get_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'

    #get the manifest location from the json
    r = requests.get(manifest_url)
    manifest = r.json()
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

    #Download the file, write it to 'MANZIP'
    r = requests.get(mani_url)
    with open("MANZIP", "wb") as zip:
        zip.write(r.content)
    print("Download Complete!")

    #Extract the file contents, and rename the extracted file
    # to 'Manifest.content'
    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'manifest.content')
    print('Unzipped!')

hashes = {
    # 'DestinyActivityDefinition': 'activityHash',
    # 'DestinyActivityTypeDefinition': 'activityTypeHash',
    # 'DestinyClassDefinition': 'classHash',
    # 'DestinyGenderDefinition': 'genderHash',
    # 'DestinyInventoryBucketDefinition': 'bucketHash',
    'DestinyInventoryItemDefinition': 'hash',
    # 'DestinySandboxPerkDefinition': 'hash',
    # 'DestinyProgressionDefinition': 'progressionHash',
    # 'DestinyRaceDefinition': 'raceHash',
    # 'DestinyTalentGridDefinition': 'gridHash',
    # 'DestinyUnlockFlagDefinition': 'flagHash',
    # 'DestinyHistoricalStatsDefinition': 'statId',
    # 'DestinyDirectorBookDefinition': 'bookHash',
    # 'DestinyStatDefinition': 'statHash',
    # 'DestinySandboxPerkDefinition': 'perkHash',
    # 'DestinyDestinationDefinition': 'destinationHash',
    # 'DestinyPlaceDefinition': 'placeHash',
    # 'DestinyActivityBundleDefinition': 'bundleHash',
    # 'DestinyStatGroupDefinition': 'statGroupHash',
    # 'DestinySpecialEventDefinition': 'eventHash',
    # 'DestinyFactionDefinition': 'factionHash',
    # 'DestinyVendorCategoryDefinition': 'categoryHash',
    # 'DestinyEnemyRaceDefinition': 'raceHash',
    # 'DestinyScriptedSkullDefinition': 'skullHash',
    # 'DestinyGrimoireCardDefinition': 'cardId'
}

hashes_trunc = {
    'DestinyInventoryItemDefinition': 'itemHash',
    'DestinyTalentGridDefinition': 'gridHash',
    'DestinyHistoricalStatsDefinition': 'statId',
    'DestinyStatDefinition': 'statHash',
    'DestinySandboxPerkDefinition': 'perkHash',
    'DestinyStatGroupDefinition': 'statGroupHash'
}

def build_dict(hash_dict):
    #connect to the manifest
    con = sqlite3.connect('manifest.content')
    print('Connected')
    #create a cursor object
    cur = con.cursor()

    all_data = {}
    count = 0
    # print ((hash_dict.values()))
    # with open('./hash_dict.json', 'w') as file:
    #         file.write(json.dumps(hash_dict.values(), indent = 4))
    #for every table name in the dictionary
    for table_name in hash_dict.keys():
        #get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print('Generating '+table_name+' dictionary....')

        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()
        #print all the items

        #create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]
        
        
        if count == 0 and os.path.isfile(r".\items.json") == False:
            with open('./items.json', 'w') as file:
                file.write(json.dumps(item_jsons, indent = 4))
        
        elif count == 1:
            with open('./sockets.json', 'w') as file:
                file.write(json.dumps(item_jsons, indent = 4))

        #create a dictionary with the hashes as keys
        #and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        
        for item in item_jsons:
            
            item_dict[item[hash]] = item
            
        count+=1
        print(count)

        #have a counter that runs for each loop iteration
        
        #add that dictionary to our all_data using the name of the table
        #as a key.
        all_data[table_name] = item_dict
        

    print('Dictionary Generated!')


    # get_manifest()
    # all_data = build_dict(hashes)
    # if os.path.isfile(r".\manifest.content") == False:
    #     with open('manifest.pickle', 'wb') as data:
    #         pickle.dump(all_data, data)
    #         print("'manifest.pickle' created!\nDONE!")
    # else:
    #     print('Pickle Exists')

    # with open('manifest.pickle', 'rb') as data:
    #     all_data = pickle.load(data)
    #check if pickle exists, if not create one.
    # hash = 1363886209
    # ghorn = all_data['DestinyInventoryItemDefinition'][hash]
    # print('Name: '+ghorn['displayProperties']['name'])
    # print('Type: '+ghorn['itemTypeDisplayName'])
    # print('Flavor Text: '+ghorn['flavorText'])
    # print('Perk 1: '+all_data['DestinySandboxPerkDefinition'][3486450016][ghorn['perks'][0]['perkHash']]['displayProperties']['name'])
    return all_data


