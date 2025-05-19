from statistics import stdev
#import pandas as pd
import requests
import monte_carlo
#import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
    query = f'https://api.scryfall.com/cards/search?q=set:{set}'
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

def calculate_odds(data:list, card_file: str | None = None) -> list[dict]:
    '''
    Appends to each dict entry in a list the odds of such entry being present in
    a **jumpstart** pack.

    Considering there are 121 possible packs - each card has an x / 121 chance of appearing
    in any given pack, where x is the number of times it occurs in each decklist.

    :param data list: A list of dictionaries containing at minimum the names of cards
    :param data card_file: A file containing a card distribution in any given set (specifically for jumpstarts). Each line should be
    formatted as "x card name", where x = the number of times the card occurs in the set.
    If card_file is None, probability will be evaluated using normal mtg booster pack metrics.
    :returns list[dict]: A modified list of dictionaries containing a new key 'probability' with the odds of obtaining the card in question
    '''
    #convert files to dict
    if card_file:
        counts = {}
        try:
            with open(card_file, 'r') as f:
                for line in f:
                    ct, nm = line.strip().split(' ', 1)
                    counts[nm] = int(ct)
        except OSError as e:
            print(f'{card_file} is an invalid filename: {e}')

        #iterate thru data - calc probability and append at each entry
        for card in data:
            num = counts.get(card['name'], 0)
            card['probability'] = num / 121
    
    else:
        #look into odds for certain card rarities in a booster pack - calc that
        pass
    
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
    sets = ['jmp', 'j22', 'j25']
    dfs = {}
    for set in sets:
        data = get_data_from_set(set)
        packs = monte_carlo.get_jset_prices(set, data, 2.0)
        df = monte_carlo.sim_n_packs(packs)
        #pack_df = pd.DataFrame(list(packs.items()), columns = ['deck', 'value'])
        print(f'{set}:')
        #print(pack_df.describe())
        print(df.describe())
        dfs[set] = df

    colors = ['red', 'blue', 'green']
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))  # 2 rows, 3 columns

    # Add a main title for the entire figure
    fig.suptitle('Value Distribution of 2 Jumpstart Boosters Over 1000000 Simulations', fontsize=16, fontweight='bold', y=0.98)

    for i, (j_set, color) in enumerate(zip(sets, colors)):
        # Create histogram
        sns.histplot(dfs[j_set], x='value', kde=True, color=color, ax=axes[0, i])
        axes[0, i].set_title(f'Value distribution of {j_set}')
        axes[0, i].set_xlabel('Value (USD)')
        axes[0, i].set_ylabel('Frequency')
        
        # Calculate mean for the histogram
        mean_value = dfs[j_set]['value'].mean()
        
        # Add a vertical line at the mean
        axes[0, i].axvline(x=mean_value, color='black', linestyle='--', linewidth=1.5)

        # Create boxplot
        sns.boxplot(dfs[j_set], x='value', color=color, ax=axes[1, i])
        axes[1, i].set_xlabel('Value (USD)')
        
        # Calculate quartiles and median
        q1 = dfs[j_set]['value'].quantile(0.25)
        median = dfs[j_set]['value'].median()
        q3 = dfs[j_set]['value'].quantile(0.75)
        iqr = q3 - q1
        
        # Create a statistics text box in the top left corner of the boxplot
        stats_text = (f"Statistics:\n"
                    f"Q1: {q1:.2f}\n"
                    f"Median: {median:.2f}\n"
                    f"Q3: {q3:.2f}\n"
                    f"IQR: {iqr:.2f}\n"
                    f"Mean: {mean_value:.2f}")  # Added mean to the stats box too
        
        # Position it at the top left corner of the plot
        axes[1, i].text(0.70, 0.95, stats_text, transform=axes[1, i].transAxes, 
                    verticalalignment='top', horizontalalignment='left',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Adjust layout to make room for the main title
    plt.tight_layout()
    plt.show()


    # print(f'Mean: ${mean(data):.2f}')
    # print(f'Stdev: ${standard_dev(data):.2f}')
    # print(f'Best card: {max_card(data)}')
    # data = calculate_odds(data)
    # print(f'Probability of this card: {max_card(data)['name']} = %{(max_card(data)['probability'])*100:.2f}')
    # data = calculate_weighted_value(data)
    # print(f'Mean expected value: ${mean(data, 'weighted'):.2f}')
    # print(f'Stdev expected value: ${standard_dev(data, 'weighted'):.2f}')
    # print(f'Expected value of best card: {max_card(data)['name']} = ${max_card(data)['weighted']:.2f}')
    # packs = get_jset_prices('jmp', data)
    # for key, val in packs.items():
    #     print(f'{key} : {val}')


if __name__ == '__main__':
    main()