# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import pandas as pd
import pickle

from trueskillthroughtime import History, Player, Gaussian

folder = "C:/Users/yaobv/tennis_project/tennis_atp"

df = pd.DataFrame()

for file in os.listdir(f'{folder}'):

    if file.endswith('csv') and '20' in file and 'doubles' not in file:
        df_ = pd.read_csv(f'{folder}/{file}')
        df = pd.concat([df, df_])


df = df[df['winner_name'].apply(lambda x: isinstance(x, str))].copy()
df = df[df['loser_name'].apply(lambda x: isinstance(x, str))].copy()
df = df[~df['winner_name'].str.contains('Unknown')].copy()
df = df[~df['loser_name'].str.contains('Unknown')].copy()
df = df[df['winner_name'] != df['loser_name']].copy()

df.sort_values(by=['tourney_date', 'tourney_id', 'round'],
               ascending=[True, True, True],
               inplace=True)

print('shape before dropping match dupes:', df.shape)


df.drop_duplicates(subset=['winner_name', 'loser_name', 'tourney_id'],
                   inplace=True)

print('shape after dropping match dupes:', df.shape)

df.reset_index(inplace=True, drop=True)

# figuring out how to do it set by set instead of match by match

df.dropna(subset='score', inplace=True)

df['match_length'] = [len(x.split(' ')) for x in df.score]
df = df[df['match_length'] <=3].copy()

list_for_df = []

for x, y, z in zip(df.winner_name, df.loser_name, df.match_length):

    if z == 2:
        list_for_df.append([x, y])
        list_for_df.append([x, y])
    else:
        list_for_df.append([x, y])
        list_for_df.append([y, x])
        list_for_df.append([x, y])

new_df = pd.DataFrame.from_records(
    list_for_df, columns=['winner_name', 'loser_name'])

# creating the trueskill dictionary

columns = zip(df.winner_name, df.loser_name, df.surface)

composition = [[[winner, winner + surface], [loser, loser + surface]]
               for winner, loser, surface in columns]

all_atp_players = set([val for sublist in zip(
    df.winner_name, df.loser_name) for val in sublist])

priors = dict([(p, Player(Gaussian(0., 1.51), 1.5, 0.098))
              for p in all_atp_players])

true_skill_history_priors = History(composition=composition,
                                    priors=priors,
                                    beta=0,
                                    sigma=0.5,
                                    gamma=0.01)

# running the TTT algo 

true_skill_history_priors.convergence(epsilon=0.01, iterations=10)

# creating the dictionary of player names

mens_big_dict = true_skill_history_priors.learning_curves()

mens_small_dict = dict()

for key in mens_big_dict.keys():
    if key not in mens_small_dict:
        mens_small_dict[key] = mens_big_dict[key][-1]

# getting a list of players from the ts dictionary. this can be improved
# trivially tbh

atp_players = list(
    set([val for sublist in zip(df.winner_name, df.loser_name) for val in sublist]))


# saving the files needed using pickle

with open('mens_big_dict.pickle', 'wb') as handle:
    pickle.dump(mens_big_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('mens_small_dict.pickle', 'wb') as handle2:
    pickle.dump(mens_small_dict, handle2, protocol=pickle.HIGHEST_PROTOCOL)
    
with open('mens_names.pickle', 'wb') as file:
    pickle.dump(atp_players, file, protocol=pickle.HIGHEST_PROTOCOL)