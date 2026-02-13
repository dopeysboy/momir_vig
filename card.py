from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('momir'),
    autoescape=select_autoescape()
)

class Face:
    def __init__(self, name, cmc, cc, type_line, power, toughness, text_box):
        self.name = name
        self.cmc = cmc
        self.cc = cc
        self.type_line = type_line
        self.power = power
        self.toughness = toughness
        self.text_box = text_box

    def from_dict(dict):
        return Face(dict['name'], dict['cmc'], dict['cc'], dict['type_line'], dict['power'], dict['toughness'], dict['text_box'])

    def is_creature(self):
        return self.power is not None

class Card:
    def __init__(self, scryfall_id, front:Face, back:Face=None, related_cards:list=None):
        self.scryfall_id = scryfall_id
        self.front = front
        self.back = back
        self.related_cards = related_cards

    def is_mdfc(self):
        return self.back is not None

    def has_related(self):
        return self.related_cards is not None

    def print_card(self):
        template = env.get_template('card.j2')
        return template.render(card=self)

    def print_related(self, all_related_cards):
        related_templates = []
        if self.has_related():
            template = env.get_template('card.j2')
            for related_id in self.related_cards:
                for related_card in all_related_cards:
                    if related_card.scryfall_id == related_id:
                        related_templates.append(template.render(card=related_card))

        return related_templates

    def get_cmc(self):
        return float(self.front.cmc)

    def to_json(self):
        template = env.get_template('card_json.j2')
        return template.render(card=self)

    def get_name(self):
        return self.front.name