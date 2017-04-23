from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, Subsession
from django.db import transaction
import random  

def swap_groups(player1,player2):
    group1 = player1.group
    group2 = player2.group

    new_group1_players = group1.get_players()
    new_group2_players = group2.get_players()

    new_group1_players.remove(player1)
    new_group2_players.remove(player2)

    new_group1_players.append(player2)
    new_group2_players.append(player1)

    group1.set_players(new_group1_players)
    group2.set_players(new_group2_players)

    group1.save()
    group2.save()

class FirstPage(Page):

    def before_next_page(self):

        with transaction.atomic():
            sub = Subsession.objects.select_for_update().filter(pk=self.subsession.id)
            #do what you need to do... "no one working" on the same Subsession will be able to enter this block as long
            #as this block is not over
            self.player.waiting_for_a_group_to_form = True
            original_group_players = self.group.get_players()


            ###We first check whether the original group of the player is ready to enter the round
            all_are_ready_in_natural_group = True
            for player in original_group_players:
                if not player.waiting_for_a_group_to_form:
                    all_are_ready_in_natural_group = False
                    break

            if all_are_ready_in_natural_group:
                # keep the natural group and let it naturally go to the next step
                for player in original_group_players:
                    self.player.waiting_for_a_group_to_form = False
            else:
                other_players_in_the_subsession = self.player.get_others_in_subsession()
                other_ready_players_in_the_subsession =  set(filter(lambda x: x.waiting_for_a_group_to_form  , other_players_in_the_subsession))
                same_type_other_ready_players_in_the_subsession = set(filter(lambda x: x.player_type == self.player.player_type , other_ready_players_in_the_subsession))
                other_type_other_ready_players_in_the_subsession = other_ready_players_in_the_subsession - same_type_other_ready_players_in_the_subsession


                if len(same_type_other_ready_players_in_the_subsession) > 0 and len(other_type_other_ready_players_in_the_subsession) > 1:

                    # own player will always be in the group that will advance in order to trigger advance and to make it easier to determine whose group will be filled

                    other_type_players_who_will_advance_set = set(random.sample(other_type_other_ready_players_in_the_subsession, 2))
                    same_type_player_who_will_advance_set = set(random.sample(same_type_other_ready_players_in_the_subsession,1))
                    same_type_player_who_will_advance_set.add(self.player)
                    all_players_who_will_advance_set = same_type_player_who_will_advance_set | other_type_players_who_will_advance_set
                    own_original_group_set = set(original_group_players) 
                    
                    other_players_in_own_group_to_swap_out = own_original_group_set - all_players_who_will_advance_set
                    players_from_other_groups_to_swap_in = all_players_who_will_advance_set - own_original_group_set

                    assert (len(other_type_players_who_will_advance_set) == len(same_type_player_who_will_advance_set))

                    for x, y in zip(other_players_in_own_group_to_swap_out, players_from_other_groups_to_swap_in):
                        swap_groups(x,y)

                    for p in all_players_who_will_advance_set:
                        p.waiting_for_a_group_to_form = False

                else:
                    pass
                 # not enough players of the right sort, right now



class WP(WaitPage):

    def after_all_players_arrive(self):
        pass
 


class SecondPage(Page):
    def vars_for_template(self):
        return {
        'group_matrix': self.subsession.get_group_matrix()
        }




page_sequence = [
    FirstPage,
    WP,
    SecondPage
]
