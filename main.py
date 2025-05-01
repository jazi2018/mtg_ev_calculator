import numpy as np
import requests

'''
Common themes are each represented four times in different variations among the
121 packs, rare themes twice, and mythic themes are represented only once.
Mythic cards are 1 in 121 packs - rare cards are 2 in 121 packs
'''

headers = {
    'user-agent' : 'SetValueEstimator/1.0',
    'accept' : '*/*'
}

def extract_data(data: list, keys:list = ['name', 'rarity']) -> list:
    '''
    Extracts relevant data from json formatted scryfall query
    
    :param data list: A list of dictionaries returned from a scryfall query
    :param keys list: Any number of desired keys to be extracted from query - price exclusive.
    If no keys are passed, default values are used.
    :returns: A list of dictionaries containing name, price (usd), and rarity for each card by default
    '''
    new_data = []

    try:
        for card in data:
            temp = {}
            temp['price'] = data['prices']['usd']
            for key in keys:
                temp[key] = data[key]
            
            new_data.append(temp)

    except KeyError as e:
        print(f'An invalid key was selected: {e}')
        return new_data
    
    return new_data


def get_data_from_set(set: str) -> list:
    data = []
    query = f'https://api.scryfall.com/cards/search?q=set:{set}+-type:land'
    while True:
        try:
            #query scryfall for set
            r = requests.get(query, headers=headers)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'An error has occured during scryfall query: {e}')
            return data
        
        #convert query to json
        page = r.json()
        #extract data from this page's list of cards
        data.extend(extract_data(page['data']))

        if page['has_more']:
            #set query for next page, repeat loop
            query = page['next_page']
        else:
            #no more pages, query done - return data
            return data

def main():
    request_delay = 0.075
    
    r = requests.get('https://api.scryfall.com/cards/search?q=set:jmp+-type:land', headers=headers)
    
    try:
        r.raise_for_status()
    except Exception as e:
        print(f'an exception has occured: {e}')

    data = r.json()
    prices = []
    


if __name__ == '__main__':
    main()