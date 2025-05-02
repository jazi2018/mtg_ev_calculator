from statistics import stdev
#import pandas as pd
import requests

'''
Common themes are each represented four times in different variations among the
121 packs, rare themes twice, and mythic themes are represented only once.
Mythic cards are 1 in 121 packs - rare cards are 2 in 121 packs
'''

'''
Card rarity approximations:
Individual mythic cards printed in Jumpstart are going to be in one out of every 121 packs.
Individual rare cards might be printed in two packs, but some might not be. Also, one out
of three Jumpstart packs will include two cards printed at rare.
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
            price = card['prices']['usd']
            temp['price'] = float(price) if price is not None else 0
            for key in keys:
                temp[key] = card[key]
            
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

# analysis functions #
def max_card(data:list) -> dict:
    max = data[0]
    for card in data:
        if card['price'] > max['price']:
            max = card  
    
    return max

def mean(data:list) -> float:
    sum = 0
    for card in data:
        sum += card['price']
    
    return sum / len(data)

def standard_dev(data:list) -> float:
    prices = []
    for card in data:
        prices.append(card['price'])
    
    return stdev(prices)

def main():
    data = get_data_from_set('j25')
    print(f'Mean: ${mean(data):.2f}')
    print(f'Stdev: ${standard_dev(data):.2f}')
    print(f'Best card: {max_card(data)}')


if __name__ == '__main__':
    main()