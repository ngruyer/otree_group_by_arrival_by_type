from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django import forms

author = 'Nicolas Gruyer - Economics Games. https://economics-games.com'

doc = """
Test Game: Players entering the game should be grouped by 4 after their arrival, as soon as possible. But each group of 4 must contain exactly 2 type_1 and 2 type_2 players.
Be careful, do not manipulate groups containing players who have already entered the round: This might create problems.
"""


class Constants(BaseConstants):
    name_in_url = 'group_test'
    players_per_group = 4
    num_rounds = 1


class Subsession(BaseSubsession):
    def before_session_starts(self):
        for p in self.get_players():
            p.player_type = (p.id_in_group  - 1) % 2 + 1


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    waiting_for_a_group_to_form = models.BooleanField()
    player_type = models.IntegerField()
