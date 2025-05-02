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
def max_card(data:list, key:str = 'price') -> dict:
    max = data[0]
    for card in data:
        if card[key] > max[key]:
            max = card  
    
    return max

def mean(data:list, key:str = 'price') -> float:
    sum = 0
    for card in data:
        sum += card[key]
    
    return sum / len(data)

def standard_dev(data:list, key:str = 'price') -> float:
    prices = []
    for card in data:
        prices.append(card[key])
    
    return stdev(prices)

def calculate_odds(data:list) -> list[dict]:
    '''
    Appends to each dict entry in a list the odds of such entry being present in
    a jumpstart pack.

    Considering there are 121 possible packs - each card has an x / 121 chance of appearing
    in any given pack, where x is the number of times it occurs in each decklist.

    :param data list: A list of dictionaries containing at minimum the names of cards
    :returns list[dict]: A modified list of dictionaries containing a new key 'probability' with the odds of obtaining the card in question
    '''
    #convert files to dict
    counts = {}
    with open('jumpstart_cards.txt', 'r') as f:
        for line in f:
            ct, nm = line.strip().split(' ', 1)
            counts[nm] = int(ct)
    
    #iterate thru data - calc probability and append at each entry
    for card in data:
        num = counts.get(card['name'], 0)
        card['probability'] = num / 121
    
    return data

def calculate_weighted_value(data:list) -> list[dict]:
    '''
    Appends to each dict entry in a list the weighted value of each card.

    Simply multiplies card probability by price to weight the expected value.
    '''

    for card in data:
        card['weighted'] = card['price'] * card['probability']
    
    return data

def main():
    data = get_data_from_set('jmp')
    print(f'Mean: ${mean(data):.2f}')
    print(f'Stdev: ${standard_dev(data):.2f}')
    print(f'Best card: {max_card(data)}')
    data = calculate_odds(data)
    print(f'Probability of this card: {max_card(data)['name']} = %{(max_card(data)['probability'])*100:.2f}')
    data = calculate_weighted_value(data)
    print(f'Mean expected value: ${mean(data, 'weighted'):.2f}')
    print(f'Stdev expected value: ${standard_dev(data, 'weighted'):.2f}')
    print(f'Expected value of best card: {max_card(data)['name']} = ${max_card(data)['weighted']:.2f}')


if __name__ == '__main__':
    main()