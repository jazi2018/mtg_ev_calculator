import requests
from bs4 import BeautifulSoup

urls = ['https://mtg.fandom.com/wiki/Jumpstart/Decklists_-_Blue',
        'https://mtg.fandom.com/wiki/Jumpstart/Decklists_-_White',
        'https://mtg.fandom.com/wiki/Jumpstart/Decklists_-_Black',
        'https://mtg.fandom.com/wiki/Jumpstart/Decklists_-_Red',
        'https://mtg.fandom.com/wiki/Jumpstart/Decklists_-_Green',
        'https://mtg.fandom.com/wiki/Jumpstart/Decklists_-_Other']
card_lines = []

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    #find all cards on page
    card_elements = soup.find_all(class_="ext-scryfall-deckentry")

    #get card text
    card_lines += [card.get_text(strip=False) for card in card_elements]

#write to file
with open("jumpstart_cards.txt", "w", encoding="utf-8") as f:
    for line in card_lines:
        f.write(line + "\n")