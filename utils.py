# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 10:04:03 2023

@author: yaobv
"""

import pandas as pd
import numpy as np
import re
import os


class MatchElo:

    def __init__(self, df: pd.DataFrame, base_k: int = 42):
        self.df = df
        self.names = set(
            pd.concat([self.df['winner_name'], self.df['loser_name']]))
        self.winners = self.df.winner_name
        self.losers = self.df.loser_name
        self.elo_dict = {name: 1500 for name in self.names}
        self.base_k = base_k
        self.processed = False
        self.winner_elo = []
        self.loser_elo = []
        self.winner_probs = []

    def update_elo(self, winner=None, loser=None):

        prematch_winner_elo = self.elo_dict[winner]
        prematch_loser_elo = self.elo_dict[loser]

        exp_a = 1 / \
            (1 + 10 ** ((prematch_loser_elo - prematch_winner_elo)/400))
        exp_b = 1 - exp_a

        winner_delta = self.base_k * (1 - exp_a)
        loser_delta = self.base_k * (0 - exp_b)

        self.elo_dict[winner] = prematch_winner_elo + winner_delta
        self.elo_dict[loser] = prematch_loser_elo + loser_delta

        return exp_a, prematch_winner_elo, prematch_loser_elo

    def process_elo(self):

        if self.processed:
            return "elo already processed"

        else:
            for w, l in zip(self.winners, self.losers):
                win_prob_, pm_w, pm_l = self.update_elo(winner=w, loser=l)

                self.winner_elo.append(pm_w)
                self.loser_elo.append(pm_l)
                self.winner_probs.append(win_prob_)

            self.processed = True
            print("elo ratings processed successfully")
            return self
        

class SetsElo:

    def __init__(self, df: pd.DataFrame, base_k: int = 33):
        self.df = df
        self.names = self.names = set(
            pd.concat([self.df['winner_name'], self.df['loser_name']]))
        self.winners = df.winner_name
        self.losers = df.loser_name
        self.total_sets = df.total_sets
        self.elo_dict = {name: 1500 for name in self.names}
        self.base_k = base_k
        self.winner_probs = []
        self.processed = False

    def get_match_start_elo(self, winner=None, loser=None):

        prematch_winner_elo = self.elo_dict[winner]
        prematch_loser_elo = self.elo_dict[loser]

        exp_a = 1 / \
            (1 + 10 ** ((prematch_loser_elo - prematch_winner_elo)/400))
        exp_b = 1 - exp_a

        return exp_a

    def update_elo(self, winner=None, loser=None, winner_won=True):
        prematch_winner_elo = self.elo_dict[winner]
        prematch_loser_elo = self.elo_dict[loser]

        exp_a = 1 / \
            (1 + 10 ** ((prematch_loser_elo - prematch_winner_elo)/400))
        exp_b = 1 - exp_a

        if winner_won:
            winner_delta = self.base_k * (1 - exp_a)
            loser_delta = self.base_k * ((0) - exp_b)

            self.elo_dict[winner] = prematch_winner_elo + winner_delta
            self.elo_dict[loser] = prematch_loser_elo + loser_delta

        else:
            winner_delta = self.base_k * (0 - exp_a)
            loser_delta = self.base_k * ((1) - exp_b)

            self.elo_dict[winner] = prematch_winner_elo + winner_delta
            self.elo_dict[loser] = prematch_loser_elo + loser_delta

    def process_elo(self):

        if self.processed:
            return "elo already processed"

        else:
            for w, l, s in zip(self.winners, self.losers, self.total_sets):

                prematch_win_prob = self.get_match_start_elo(winner=w, loser=l)
                self.winner_probs.append(prematch_win_prob)

                if s == 2:
                    for i in range(2):
                        self.update_elo(winner=w, loser=l)

                elif s == 3:
                    self.update_elo(winner=w, loser=l)
                    self.update_elo(winner=w, loser=l, winner_won=False)
                    self.update_elo(winner=w, loser=l)

                elif s == 4:
                    self.update_elo(winner=w, loser=l)
                    self.update_elo(winner=w, loser=l)
                    self.update_elo(winner=w, loser=l, winner_won=False)
                    self.update_elo(winner=w, loser=l)

                else:
                    self.update_elo(winner=w, loser=l)
                    self.update_elo(winner=w, loser=l, winner_won=False)
                    self.update_elo(winner=w, loser=l)
                    self.update_elo(winner=w, loser=l, winner_won=False)
                    self.update_elo(winner=w, loser=l)

        return self

def elo_predict(elo_a=1500, elo_b=1500):
    
    "returns the win probability of elo_a given elo_a and elo_b"
    
    prob_a = 1 / (1 + 10 ** ((elo_b - elo_a)/400))

    return prob_a


def fiveodds(p3):
  
  "converts the probability of winning 3 sets into the probability of winning 5"
  
  p1 = np.roots([-2, 3, 0, -1*p3])[1]
  p5 = (p1**3)*(4 - 3*p1 + (6*(1-p1)*(1-p1)))
  
  return p5

def last_with_nan(series):
    "a function to return the last value in a groupby even if its nan"
    val = series.iloc[-1]
    return val if val else np.nan

def process_match_stats(df : pd.DataFrame, window : int = 20):
    """
    Converts player match stats into rolling match statistics

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe containing match results
    window : int, optional
        The size of the rolling window.

    Returns
    -------
    stats_df : pd.DataFrame
        Each player's rolling statistics at the date of the match

    """
    
    winner_df = df[['winner_name', 'tourney_date', 'tourney_id', 'round', 'total_sets',
               'w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon',
               'w_SvGms', 'w_bpSaved', 'w_bpFaced', 'w_2ndsvOpps', 'w_1stReturnOpps',
               'w_1stReturnPts', 'w_2ndReturnOpps', 'w_2ndReturnPts', 'w_bpOpps', 'w_bpWon']].copy()

    loser_df = df[['loser_name', 'tourney_date', 'tourney_id', 'round', 'total_sets',
              'l_ace', 'l_df', 'l_svpt', 'l_1stIn', 'l_1stWon', 'l_2ndWon',
              'l_SvGms', 'l_bpSaved', 'l_bpFaced', 'l_2ndsvOpps', 'l_1stReturnOpps',
              'l_1stReturnPts', 'l_2ndReturnOpps', 'l_2ndReturnPts', 'l_bpOpps', 'l_bpWon']].copy()

    # renaming the columns so they're identical
    winner_df.columns = [x.split('_')[1] if '_' in x else 'round' for x in winner_df.columns]
    loser_df.columns = [x.split('_')[1] if '_' in x else 'round' for x in loser_df.columns]
    
    # stacking the winner and loser columns and then sorting by the index
    stats_df = pd.concat([winner_df, loser_df], axis=0)
    stats_df.sort_index(inplace=True)

    # calculating matches played
    stats_df['matches_played'] = stats_df.groupby('name').cumcount() + 1
    

    # lambda func so its easy to adjust the window
    rolling_func = lambda x: x.shift().rolling(window, min_periods=5).sum()

    # calculating rolling statistics for each player
    stats_df['rolling_svpts'] = stats_df.groupby('name')['svpt'].transform(rolling_func)
    stats_df['rolling_1stIn'] = stats_df.groupby('name')['1stIn'].transform(rolling_func)
    stats_df['rolling_1stIn_perc'] = stats_df['rolling_1stIn'].div(stats_df['rolling_svpts'])

    stats_df['rolling_1stWon'] = stats_df.groupby('name')['1stWon'].transform(rolling_func)
    stats_df['rolling_1stWon_perc'] = stats_df['rolling_1stWon'].div(stats_df['rolling_1stIn'])

    stats_df['rolling_2ndsvOpps'] = stats_df.groupby('name')['2ndsvOpps'].transform(rolling_func)
    stats_df['rolling_2ndWon'] = stats_df.groupby('name')['2ndWon'].transform(rolling_func)
    stats_df['rolling_2ndWon_perc'] = stats_df['rolling_2ndWon'].div(stats_df['rolling_2ndsvOpps'])

    stats_df['rolling_aces'] = stats_df.groupby('name')['ace'].transform(rolling_func)
    stats_df['rolling_aces_perc'] = stats_df['rolling_aces'].div(stats_df['rolling_svpts'])

    stats_df['rolling_dfs'] = stats_df.groupby('name')['df'].transform(rolling_func)
    stats_df['rolling_dfs_perc'] = stats_df['rolling_dfs'].div(stats_df['rolling_svpts'])

    stats_df['rolling_1stRetOpps'] = stats_df.groupby('name')['1stReturnOpps'].transform(rolling_func)
    stats_df['rolling_1stRetPts'] = stats_df.groupby('name')['1stReturnPts'].transform(rolling_func)
    stats_df['rolling_1stRet_perc'] = stats_df['rolling_1stRetPts'].div(stats_df['rolling_1stRetOpps'])

    stats_df['rolling_2ndRetOpps'] = stats_df.groupby('name')['2ndReturnOpps'].transform(rolling_func)
    stats_df['rolling_2ndRetPts'] = stats_df.groupby('name')['2ndReturnPts'].transform(rolling_func)
    stats_df['rolling_2ndRet_perc'] = stats_df['rolling_2ndRetPts'].div(stats_df['rolling_2ndRetOpps'])
    
    return stats_df


def get_player_points(df : pd.DataFrame = None):
    """
    Converts the raw set scores into cumulative match points.
    Note this function only needs df.score and should therefore
    be modified.

    """

    winner_scores = []
    loser_scores = []

    pattern = re.compile(r'\d+-\d+')

    for score in df.score:

        winner = 0
        loser = 0

        sets_ = re.findall(pattern, score)
        set_scores = [x.split('-') for x in sets_]

        for ss in set_scores:
            winner += int(ss[0])
            loser += int(ss[1])

        winner_scores.append(winner)
        loser_scores.append(loser)

    return pd.Series(winner_scores), pd.Series(loser_scores)

def load_atp_data(folder_path='./tennis_atp'):
    """
    

    Returns
    -------
    df : a pandas dataframe containing lightly processed and de-duped ATP
         match data from 2000-01-01 until present

    """

    folder = folder_path

    df = pd.DataFrame()

    for file in os.listdir(f'{folder}'):

        if file.endswith('csv') and '20' in file and 'doubles' not in file:
            df_ = pd.read_csv(f'{folder}/{file}')
            df = pd.concat([df, df_])
            
    round_dict = {
        'RR': 0,
        'ER': 0,
        'BR': 0,
        'Q1': 1,
        'R128': 1,
        'Q2': 2,
        'R64': 2,
        'Q3': 3,
        'R32': 3,
        'R16': 4,
        'QF': 5,
        'Q4': 5,
        'SF': 6,
        'F': 7
    }

    df = df[df['winner_name'].apply(lambda x: isinstance(x, str))].copy()
    df = df[df['loser_name'].apply(lambda x: isinstance(x, str))].copy()
    df = df[~df['winner_name'].str.contains('Unknown')].copy()
    df = df[~df['loser_name'].str.contains('Unknown')].copy()
    df = df[df['winner_name'] != df['loser_name']].copy()

    df.dropna(subset='score', inplace=True)
    df['retired'] = [1 if 'RET' in x else 0 for x in df.score]
    df['walkover'] = [1 if 'W/O' in x else 0 for x in df.score]

    # reformatting names to compare with betting data later
    df['winner_initial'] = [x.split()[-1] + ' ' + x.split()[0][0] + '.' for x in df.winner_name]
    df['loser_initial'] = [x.split()[-1] + ' ' + x.split()[0][0] + '.' for x in df.loser_name]

    df['total_sets'] = [len(x.split()) if isinstance(x, str) else np.nan for x in df.score]

    # extracting the points for each set using a custom function 
    x, y = get_player_points(df=df)
    df['winner_points'] = x
    df['loser_points'] = y

    df['round'] = df['round'].map(round_dict)
    df['tourney_date'] = [str(x)[:4] + '-' + str(x)[4:6] + '-' + str(x)[6:8] for x in df.tourney_date]
    df['tourney_date'] = pd.to_datetime(df['tourney_date'])
    df['month'] = df.tourney_date.dt.month

    df.sort_values(by=['tourney_date', 'tourney_id', 'round'],
                   ascending=[True, True, True],
                   inplace=True)

    # calculating match statistics to later compute rolling statistics
    df['w_2ndsvOpps'] = df['w_svpt'].sub(df['w_1stIn'])
    df['l_2ndsvOpps'] = df['l_svpt'].sub(df['l_1stIn'])

    df['w_1stReturnOpps'] = df['l_1stIn']
    df['w_2ndReturnOpps'] = df['l_svpt'].sub(df['l_1stIn'])

    df['w_1stReturnPts'] = df['l_1stIn'] - df['l_1stWon']
    df['w_2ndReturnPts'] = df['l_2ndsvOpps'] - (df['l_2ndWon'] + df['l_df'])

    df['l_1stReturnOpps'] = df['w_1stIn']
    df['l_2ndReturnOpps'] = df['w_svpt'].sub(df['w_1stIn'])

    df['l_1stReturnPts'] = df['w_1stIn'] - df['w_1stWon']
    df['l_2ndReturnPts'] = df['w_2ndsvOpps'] - (df['w_2ndWon'] + df['w_df'])

    df['w_bpOpps'] = df['l_bpFaced']
    df['w_bpWon'] = df['l_bpFaced'] - df['l_bpSaved']

    df['l_bpOpps'] = df['w_bpFaced']
    df['l_bpWon'] = df['w_bpFaced'] - df['w_bpSaved']

    print('shape before dropping match dupes:', df.shape)


    df.drop_duplicates(subset=['winner_name', 'loser_name', 'tourney_id'],
                       inplace=True)

    print('shape after dropping match dupes:', df.shape)

    df.reset_index(inplace=True, drop=True)
    
    return df


def load_wta_data(folder_path="./tennis_wta"):
    """

    Returns
    -------
    df : a pandas dataframe containing lightly processed and de-duped
         WTA match data from 2000-01-01 until the present
    
    """

    folder = folder_path

    df = pd.DataFrame()

    for file in os.listdir(f'{folder}'):

        if file.endswith('csv') and '20' in file and 'doubles' not in file and '1920' not in file:

            try:
                df_ = pd.read_csv(f'{folder}/{file}', low_memory=False)
                df = pd.concat([df, df_])

            except:
                df_ = pd.read_csv(f'{folder}\{file}',
                                  encoding='latin-1', low_memory=False)
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

    return df
