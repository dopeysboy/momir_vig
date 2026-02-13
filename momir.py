import json
import os
import requests
import random
from card import *

SCRYFALL_BASE_API_URL = "https://api.scryfall.com"
SCRYFALL_HEADERS = {
    "Accept": "*/*",
    "User-Agent": "momir-vig/0.2"
}


def json_to_card_list(json_string):
    ret_list = []

    for card in json_string:
        front = Face.from_dict(card['front'])

        if card['back'] is not None:
            back = Face.from_dict(card['back'])
        else:
            back = None
        
        ret_list.append(Card(card['scryfall_id'], front, back, card['related_cards']))
    return ret_list

def write_api_data(file_path):
    target_url = f'{SCRYFALL_BASE_API_URL}/bulk-data'

    bulk_data = requests.get(target_url, headers=SCRYFALL_HEADERS)

    for item in bulk_data.json()['data']:
        if item['type'] == 'oracle_cards':
            target_url = item['download_uri']
            break

    resp = requests.get(target_url, headers=SCRYFALL_HEADERS)

    with open(file_path, 'w', encoding='utf8') as file:
        json.dump(resp.json(), file)

def get_oracle_dump_data():
    oracle_file_dump_file_path = os.path.join(os.path.dirname(__file__), 'downloaded_files', 'oracle_cards.json')

    write_api_data(oracle_file_dump_file_path)

    with open(oracle_file_dump_file_path, 'r', encoding='utf8') as file:
        return json.load(file)

def load_all_cards():
    json_data = get_oracle_dump_data()

    all_creature_cards=[] 

    for card in json_data:
        if card['name'] == 'B.F.M. (Big Furry Monster)':
            continue

        if 'Creature' in card['type_line'] and 'Token' not in card['type_line']:
            if '//' not in card['type_line']:
                name = card['name']
                cmc = card['cmc']
                cc = card['mana_cost']
                type_line = card['type_line']
                power = card['power']
                toughness = card['toughness']
                text_box = card['oracle_text']

                front_face = Face(name, cmc, cc, type_line, power, toughness, text_box)
                back_face = None
            else:
                if 'Creature' in card['card_faces'][0]['type_line']:
                    f_name = card['card_faces'][0]['name']
                    f_cmc = card['cmc']
                    f_cc = card['card_faces'][0]['mana_cost']
                    f_type_line = card['card_faces'][0]['type_line']
                    f_power = card['card_faces'][0]['power']
                    f_toughness = card['card_faces'][0]['toughness']
                    f_text_box = card['card_faces'][0]['oracle_text']
                    
                    b_name = card['card_faces'][1]['name']
                    b_cmc = card['cmc']
                    b_cc = card['card_faces'][1]['mana_cost']
                    b_type_line = card['card_faces'][1]['type_line']
                    b_text_box = card['card_faces'][1]['oracle_text']

                    if 'Creature' in card['card_faces'][1]['type_line']:
                        b_power = card['card_faces'][1]['power']
                        b_toughness = card['card_faces'][1]['toughness']
                    else:
                        b_power = None
                        b_toughness = None

                    front_face = Face(f_name, f_cmc, f_cc, f_type_line, f_power, f_toughness, f_text_box)
                    back_face = Face(b_name, b_cmc, b_cc, b_type_line, b_power, b_toughness, b_text_box)
      
            if 'all_parts' in card.keys():
                related_cards = []

                for related in card['all_parts']:
                    if related['id'] != card['id']:
                        related_cards.append(related['id'])
            else:
                related_cards = None

            all_creature_cards.append(Card(card['id'], front_face, back_face, related_cards))
    return all_creature_cards

def get_related_ids(all_creature_cards):
    ret_list = []
    
    for card in all_creature_cards:
        if card.has_related():
            ret_list += card.related_cards

    return ret_list

def populate_related_data(id_list):
    all_cards = get_oracle_dump_data()
    ret_dict = {}
    
    for id in id_list:
        if id not in ret_dict.keys():
            for card in all_cards:
                if card['id'] == id:
                    if '//' not in card['type_line']:
                        name = card['name']
                        cmc = card['cmc']
                        cc = card['mana_cost']
                        type_line = card['type_line']
                        text_box = card['oracle_text']
                        if 'Creature' in card['type_line']:
                            power = card['power']
                            toughness = card['toughness']
                        else:
                            power = None
                            toughness = None

                        front_face = Face(name, cmc, cc, type_line, power, toughness, text_box)
                        back_face = None
                    else:
                        f_name = card['card_faces'][0]['name']
                        f_cmc = card['cmc']
                        f_cc = card['card_faces'][0]['mana_cost']
                        f_type_line = card['card_faces'][0]['type_line']
                        f_text_box = card['card_faces'][0]['oracle_text']
                        
                        if 'Creature' in card['card_faces'][0]['type_line']:
                            f_power = card['card_faces'][0]['power']
                            f_toughness = card['card_faces'][0]['toughness']
                        else:
                            f_power = None
                            f_toughness = None

                        b_name = card['card_faces'][1]['name']
                        b_cmc = card['cmc']
                        b_cc = card['card_faces'][1]['mana_cost']
                        b_type_line = card['card_faces'][1]['type_line']
                        b_text_box = card['card_faces'][1]['oracle_text']

                        if 'Creature' in card['card_faces'][1]['type_line']:
                            b_power = card['card_faces'][1]['power']
                            b_toughness = card['card_faces'][1]['toughness']
                        else:
                            b_power = None
                            b_toughness = None

                        front_face = Face(f_name, f_cmc, f_cc, f_type_line, f_power, f_toughness, f_text_box)
                        back_face = Face(b_name, b_cmc, b_cc, b_type_line, b_power, b_toughness, b_text_box)

                    ret_dict[id] = Card(card['id'], front_face, back_face)

    return ret_dict

def print_list(input_list):
    for item in input_list:
        print(item)

def refresh_data(all_creature_cards_filepath, related_cards_filepath):
    all_creature_cards = load_all_cards()
    all_related_ids = get_related_ids(all_creature_cards)

    related_cards = populate_related_data(all_related_ids)

    with open(all_creature_cards_filepath, 'w', encoding='utf-16') as file:
        file.write('[\n')
        for i in range(len(all_creature_cards)):
            file.write(f'{all_creature_cards[i].to_json()}')
            if i != len(all_creature_cards) - 1:
                file.write(f',\n')
        file.write('\n]')
    
    with open(related_cards_filepath, 'w', encoding='utf-16') as file:
        file.write('[\n')
        i = 0
        for key in related_cards.keys():
            file.write(f'{related_cards[key].to_json()}')
            if i != len(related_cards.keys()) - 1:
                file.write(f',\n')
                i += 1
        file.write('\n]')

    return all_creature_cards, related_cards

def load_card_data(do_refresh_data):
    script_filepath = os.path.dirname(__file__)
    all_creature_cards_filepath = os.path.join(script_filepath, 'downloaded_files', 'all_creature_cards.json')
    related_cards_filepath = os.path.join(script_filepath, 'downloaded_files', 'related_cards.json')

    if do_refresh_data:
        refresh_obj = refresh_data(all_creature_cards_filepath, related_cards_filepath)

        all_creature_cards = refresh_obj[0]
        related_cards = refresh_obj[1]

    else:
        with open(all_creature_cards_filepath, 'r', encoding='utf-16') as file:
            all_creature_cards_json = json.load(file)

        with open(related_cards_filepath, 'r', encoding='utf-16') as file:
            related_cards_json = json.load(file)

        all_creature_cards = json_to_card_list(all_creature_cards_json)
        related_cards = json_to_card_list(related_cards_json)

    return all_creature_cards, related_cards


def print_momir(input_num, do_refresh):
    card_obj = load_card_data(do_refresh)

    all_creature_cards = card_obj[0]
    related_cards = card_obj[1]

    valid_creatures = []

    for creature in all_creature_cards:
        if creature.get_cmc() == input_num:
            valid_creatures.append(creature)

    list_choice_num = random.randint(0, len(valid_creatures) - 1)

    chosen_creature = valid_creatures[list_choice_num]
    print(chosen_creature.print_card())
    print_list(chosen_creature.print_related(related_cards))


def main():
    print_momir(3, False)


if __name__ == "__main__":
    main()
