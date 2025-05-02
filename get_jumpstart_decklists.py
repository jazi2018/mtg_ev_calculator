import requests
from bs4 import BeautifulSoup
from collections import Counter

sets = ['Jumpstart', 'Jumpstart_2022', 'Foundations_Jumpstart']
colors = ['White', 'Blue', 'Black', 'Red', 'Green', 'Other']
counts = Counter()

for set in sets:
    for color in colors:
        response = requests.get(f'https://mtg.fandom.com/wiki/{set}/Decklists_-_{color}')
        soup = BeautifulSoup(response.text, 'html.parser')

        #find all cards on page
        card_elements = soup.find_all(class_="ext-scryfall-deckentry")

        #get card text
        #card_lines += [card.get_text(strip=False) for card in card_elements]
        for card in card_elements:
            text = card.get_text()
            try:
                ct, nm = text.split(' ', 1)
                counts[nm] += int(ct)
            except ValueError:
                print(f'line is messed up! : {text}\nskipping!')
                continue

    #write to file
    with open(f"{str.lower(set)}_cards.txt", "w", encoding="utf-8") as f:
        for name, count in counts.most_common():
            f.write(f'{count} {name}\n')
    
    counts.clear()