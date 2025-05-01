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

def extract_prices(data) -> list:
    pass
    # prices = []
    # while True:
        

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