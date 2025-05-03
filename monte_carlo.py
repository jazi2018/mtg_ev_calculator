import pandas as pd
import random

def get_jset_prices(set: str, data: list[dict]):
    '''
    Compiles pack options for a given jumpstart set, returning a dictionary containing
    the name of the pack and its value
    '''

    abbrev = {'jmp':'jumpstart', 'j22':'jumpstart_2022', 'j25':'foundations_jumpstart'}

    with open(f'decklists/separate_{abbrev[set]}_cards.txt', 'r') as f:
        current_pack = None
        packs = {}
        pack_sum = 0.0
        for line in f:
            if not line[0].isdigit():
                if current_pack:
                    packs[current_pack] = pack_sum
                current_pack = line.strip()
                pack_sum = 0.0
            else:
                ct, nm = line.split(' ', 1)
                nm = nm.strip()
                for card in data:
                    if card['name'] == nm:
                        pack_sum += card['price'] * int(ct)
        packs[current_pack] = pack_sum
    
    return packs

def open_pack(packs:dict):
    return random.choice(list(packs.values()))

def sim_n_packs(packs:dict, n_packs:int = 24, x_sims:int = 1000000) -> pd.DataFrame:
    #storing data as dictionary - will return as a dataframe at the end
    sims = {}
    for i in range(x_sims):
        pack_sum = 0
        for j in range(n_packs):
            pack_sum += open_pack(packs)
        sims[i] = pack_sum
    
    return pd.DataFrame.from_dict(sims, orient='index', columns=['value'])