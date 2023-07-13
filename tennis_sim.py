# -*- coding: utf-8 -*-
"""
Created on Tue May 30 15:39:12 2023

@author: yaobv
"""

import random
import numpy as np


def play_a_single_game(ps, psB=None):
  """
  Function to check if a given player with 'ps' chances of winning a 
  given point wins a single game. 
  
  Input : 
  ----------------
  ps - probability of server winning a single point 
  psB - probability of winning a big point with default None
  
  Output : 
  ----------------
  a list of list like [1, [40,30]] where
  
  first element --- whether she wins a single game or not
  second element --- score of the current game 
  """
  # set their respective points to zero; here we will
  # represent 0 by 0, 15 by 1, 30 by 2 and 40 by 3 and 40+ by 4.
  # I store this dictionary for finally returning the score of the game
  # note that I denote 40+ score by 4 as well
  score_dict = {0: 0, 1: 15, 2: 30, 3: 40, 4: 40}
  score1 = 0
  score2 = 0
  # set the big point probabilities to original if not provided
  psB = ps if psB is None else psB

  while True:
    # change the original probability to big point probability
    # if it is the game point i.e 40 for the server
    ps = psB if score1 == 3 else ps
    # simulate the bernoulli trial for the given player
    # and check if she wins a point or not
    if random.random() < ps:
      # if she wins a point increment her score by 1
      score1 += 1
    else:
      # otherwise increment the score of her opponent
      score2 += 1
    # print score1,'-', score2
    # winning condition for the given player
    if score1 >= 4 and (score1-score2) >= 2:
      # if the score of first player is 4 and the difference
      # between the score of two players
      return [1, [score_dict[score1], score_dict[score2]]]
    # winning condition for the opponent of the given player
    elif score2 >= 4 and (score2-score1) >= 2:
      return [0, [score_dict[score1], score_dict[score2]]]
   # if there is deuce or advantage score e.g. 6-5,
  # we bring it to a score like 3-2 since this is equivalent
    while True:
      if (score1 + score2) > 6:
        # we set the original probability to big point prob
          ps = psB
          score1 -= 1
          score2 -= 1
      else:
        break


def actual_probability_of_winning_game(ps):
  """
  Function computes the actual probability of a server winning a game 
  if the probability of winning a single point is known.
  
  Input : ps - probability of server winning a single point 
  
  Output : the probability of winning a game   
  
  citation 
  ---------------------------
  https://pdfs.semanticscholar.org/e870/8ca24b8f67476b3284ec22ccb689dc6229be.pdf
  
  Probability of Winning at Tennis I. Theory and Data
  By Paul K. Newton and Joseph B. Keller
  """
  result = ps**4 + 4*(ps**4)*(1-ps) + 10*(ps**4)*(1-ps)**2 + \
      20*(ps**5)*((1-ps)**3)/(1-2*ps*(1-ps))
  return result


def play_a_tiebreaker(ps1, ps2, server=1):
  """
  Function simulates the result of a tie-breaker game and returns if
  player 1 has won the tie-breaker or not. Here I am assuming that a
  tie-breaker consists of 7-points and a player wins a tie-breaker if 
  she wins by a difference of 2 points. Here points are counted as 0,
  1,2,3,4,5,6,7.
  
  Input : 
  --------------------
  ps1 - probability of player 1 winning a single point if she serves
  ps2 - probability of player 2 winning a single point if she serves 
  server - a bool representing who is serving at the start of the tie breaker.
  
  Output :
  --------------------
  Returns 1/0 representing if player 1 wins a given tie breaker. 
  
  """
  # set
  next_set_server = 2 if server == 1 else 1
  # set their respective points to zero;
  tiebreaker_score1 = 0
  tiebreaker_score2 = 0
  while True:
    if server == 1:
      # check if player 1 is serving and
      # next check if she won the game
      if random.random() < ps1:
        # increment her score by 1
        tiebreaker_score1 += 1
        # and change the server to player 2
        server = 2
      else:
        # if player 1 did not win the game then increment player 2 score
        tiebreaker_score2 += 1
        # since player 1 was serving, we allot serve to player 2
        server = 2
    else:
      # if player 2 is serving then check if she won the game and store the
      if random.random() < ps2:
        # if she won the game then increment her score by 1
        tiebreaker_score2 += 1
        # change the server to player 1
        server = 1
      else:
        # if player 2 did not win the game then increment the score of player 2
        tiebreaker_score1 += 1
        # allot serve to player 1
        server = 1
    # print tiebreaker_score1, '-', tiebreaker_score2
    if tiebreaker_score1 >= 7 and (tiebreaker_score1-tiebreaker_score2) >= 2:
        return 1
    elif tiebreaker_score2 >= 7 and (tiebreaker_score2-tiebreaker_score1) >= 2:
        return 0
    # if the tie breaker score become something like 8:7 then we bring it back
    # to 6:5 for simplicity. These two scores are equivalent.
    while True:
        if (tiebreaker_score1+tiebreaker_score2) > 12:
            tiebreaker_score1 -= 1
            tiebreaker_score2 -= 1
        else:
          break


def play_a_single_set(ps1, ps2, ps1B=None, ps2B=None, server=1):
  """
  Function checks if a server wins a given set. 
  
  Input : 
  --------------------
  ps1 - probability of player 1 winning a single point if she serves
  ps2 - probability of player 2 winning a single point if she serves 
  ps1B - probability of player 1 winning a big point with default None
  ps2B - probability of player 2 winning a big point with default None
  server - a bool representing who is serving at the start of the set.
  
  Output : a list of lists consisting like [0, [40, 30], [6, 7], 1]
  --------------------
  first element  : outcome of the set if first player wins or not
  second element : score of the last game played 
  third element  : score of the current set 
  fourth element : who will be serving next 1 for player 1 and 2 for player 2.
  --------------------
  Therefore [0, [40, 30], [6, 7], 1] means that first player lost current set 
  to player 2 with a score of 6-7 while in the last game they played, the score
  was 40:30 which was won by player 2, therefore next turn to serve is of player 1.
  """
  # set big point probabilities if not provided
  ps1B = ps1 if ps1B is None else ps1B
  ps2B = ps2 if ps2B is None else ps2B

  # set the initial set score of each player to zero
  set_score1 = 0
  set_score2 = 0
  # repeat until a result is obtained
  while True:
    if server == 1:
      # check if player 1 is serving and save the outcome of her game
      check_if_won_game = play_a_single_game(ps1, ps1B)
      # print check_if_won_game[1]
      # next check if she won the game
      if check_if_won_game[0] == 1:
        # increment her score by 1
        set_score1 += 1
        # and change the server to player 2
        server = 2
      else:
        # if player 1 did not win the game then increment player 2 score
        set_score2 += 1
        # since player 1 was serving, we allot serve to player 2
        server = 2
    else:
      # if player 2 is serving then check if she won the game and store the
      # result of the game if she is serving
      check_if_won_game = play_a_single_game(ps2, ps2B)
      # print check_if_won_game[1]
      # check if she won the game
      if check_if_won_game[0] == 1:
        # if she won the game then increment her score by 1
        set_score2 += 1
        # change the server to player 1
        server = 1
      else:
        # if player 2 did not win the game then increment the score of player 2
        set_score1 += 1
        # allot serve to player 1
        server = 1
    # print set_score1,'-', set_score2
    # check if a tie break has occurred
    if set_score1 == 6 and set_score2 == 6:
      # if it is a tie break then play a tie break with big point probabilities
      result_tiebreaker = play_a_tiebreaker(ps1B, ps2B, server)
      # change the server after the tie breaker is over
      server = 2 if server == 1 else 1
      # if player 1 has won the tie breaker then increment her score by 1 and
      # return 1
      if result_tiebreaker == 1:
        set_score1 += 1
        # return player 1 won the set together with score of last game played
        # set scores of two players and whose turn is it to serve next
        return [1, check_if_won_game[1], [set_score1, set_score2], server]
      # if player 1 did not win then increment score of player 2 and return 0
      # together with set scores, and the next server
      else:
        set_score2 += 1
        return [0, check_if_won_game[1], [set_score1, set_score2], server]
    # check if the game is already over and player 1 has won it then
    # return 1 together with scores mentioned above.
    if set_score1 >= 6 and (set_score1-set_score2) >= 2:
      return [1, check_if_won_game[1], [set_score1, set_score2], server]
    # if player 2 won it then do similarly
    elif set_score2 >= 6 and (set_score2-set_score1) >= 2:
      return [0, check_if_won_game[1], [set_score1, set_score2], server]
    # if score becomes something like 8:7 then bring it back to 6:5 since the
    # two scores are equivalent
    while True:
      if (set_score1 + set_score2) > 12:
        # since this must have been a tie-breaker situation therefore we turn on
        # the big probabilities namely
        ps1 = ps1B
        ps2 = ps2B
        # decrement the scores of 8:7 to 6:5 which is equivalent
        set_score1 -= 1
        set_score2 -= 1
      else:
        break


def play_a_match(ps1, ps2, ps1B=None, ps2B=None, server=1, no_of_sets=3):
  """
  Function simulates a match and returns if player 1 won the match or not
  
  Input : 
  --------------------
  ps1 - probability of player 1 winning a single point if she serves
  ps2 - probability of player 2 winning a single point if she serves 
  ps1B - probability of player 1 winning a big point with default None
  ps2B - probability of player 2 winning a big point with default None
  server - a bool representing who is serving at the start of the match.
  no_of_sets - total number of sets in the match default value 3.
  
  Output :
  --------------------
  Returns a list of list consisting of the following :
  first element  : 1/0 representing if player 1 wins this match or not. 
  second element : the result of last game where current server is listed first
  next element   : the scores of the sets played between them [score1, score2]
  """
  # set the big probabilities to original prob if not supplied
  ps1B = ps1 if ps1B is None else ps1B
  ps2B = ps2 if ps2B is None else ps2B
  # set the number of sets won by each player to 0
  no_of_sets_won1 = 0
  no_of_sets_won2 = 0
  # container to store the result of each set.
  sets = []
  # container to store the result of last game
  last_game_result = []
  # loop over all number of sets until a player has won the match
  for i in range(no_of_sets):
    # play individual sets and store the result
    set_result = play_a_single_set(ps1, ps2, ps1B, ps2B, server)
    # store the result of last set played
    sets.append(set_result[2])
    # store the result of the last game played
    last_game_result = set_result[1]
    # set who will be serving next
    server = set_result[3]
    # increase the counter of number of sets won by each player
    no_of_sets_won1 += set_result[0]
    # if player 1 wins a set then player 2 win 1-1 = 0 set
    no_of_sets_won2 += 1-set_result[0]
    # exit if one of them reaches to 2 sets win
    if(no_of_sets_won1 == 2 or no_of_sets_won2 == 2):
      break
  match_result = (no_of_sets_won1 > no_of_sets_won2)*1
  return [match_result, last_game_result, sets]


def get_score_of_match(ps1, ps2, ps1B=None, ps2B=None, server=1, no_of_sets=3):
  """
  A wrapper function for play_a_match() which outputs the result of a tennis match in a nice fashion 
  
  Input : similar to play_a_match (refer above for more details )
  
  Output : prints the result on screen for player 1
  """
  # get the match result and store it
  m = play_a_match(ps1, ps2, ps1B, ps2B, server, no_of_sets)
  # extract the individual set scores
  s = m[2]
  if len(s) == no_of_sets - 1:
    print("%d-%d | %d:%d %d:%d " % (m[1][0], m[1][1], s[0][0], s[0][1], s[1][0], s[1][1]))
  else:
    print("%d-%d | %d:%d %d:%d %d:%d" % (m[1][0], m[1][1], s[0][0], s[0][1], s[1][0], s[1][1], s[2][0], s[2][1]))