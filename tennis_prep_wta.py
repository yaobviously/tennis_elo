# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:20:08 2023

@author: yaobv
"""

import os
import pandas as pd
import pickle

from trueskillthroughtime import History, Player, Gaussian

folder = "C:/Users/yaobv/tennis_project/tennis_wta"

df = pd.DataFrame()

for file in os.listdir(f'{folder}'):

    if file.endswith('csv') and '20' in file and 'doubles' not in file and '1920' not in file:

        try:
            df_ = pd.read_csv(f'{folder}/{file}')
            df = pd.concat([df, df_])

        except:
            df_ = pd.read_csv(f'{folder}\{file}', encoding='latin-1')
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

df.dropna(subset=['surface', 'winner_name', 'loser_name'],
          inplace=True)

df.drop_duplicates(subset=['winner_name', 'loser_name', 'tourney_id'],
                   inplace=True)

print('shape after dropping match dupes:', df.shape)

df.reset_index(inplace=True, drop=True)

# creating the trueskill dict for the wta players

columns = zip(df.winner_name, df.loser_name, df.surface)

composition = [[[winner, winner + surface], [loser, loser + surface]]
               for winner, loser, surface in columns]

all_wta_players = set([val for sublist in zip(
    df.winner_name, df.loser_name) for val in sublist])

priors = dict([(p, Player(Gaussian(0., 1.51), 1.5, 0.098))
              for p in all_wta_players])

true_skill_history_priors = History(composition=composition,
                                    priors=priors,
                                    beta=0,
                                    sigma=0.5,
                                    gamma=0.01)

# running the TTT dict

true_skill_history_priors.convergence(epsilon=0.01, iterations=10)

womens_big_dict = true_skill_history_priors.learning_curves()

womens_small_dict = dict()

for key in womens_big_dict.keys():
    if key not in womens_small_dict:
        womens_small_dict[key] = womens_big_dict[key][-1]


with open('women_names.pickle', 'wb') as names:
    pickle.dump(all_wta_players, names, protocol=pickle.HIGHEST_PROTOCOL)


with open('womens_big_dict.pickle', 'wb') as file:
    pickle.dump(womens_big_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    
    
with open('womens_small_dict.pickle', 'wb') as file_b:
    pickle.dump(womens_small_dict, file_b, protocol=pickle.HIGHEST_PROTOCOL)