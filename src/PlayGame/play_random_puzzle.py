import random
import re
import sys
import time
import ascii_wheel
from smart_player import computer_turn_smart, computer_turn_smart_conservative, computer_turn_smart_aggressive
from optimized_player import computer_turn_optimized, computer_turn_optimized_aggressive, computer_turn_optimized_conservative, get_human_suggestion
from solve_timing_ai import (
    computer_turn_solve_timing_conservative, 
    computer_turn_solve_timing_aggressive, 
    computer_turn_solve_timing_balanced
)

def computer_turn(showing, winnings, previous_guesses, turn):
  # Guess in the order of the alphabet
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  dollar = 0
  for character in alphabet:
    if character in previous_guesses:
      continue
    if is_vowel(character):
      if winnings[(turn % 3)] < 250:
        continue
      else:
        print("Computer bought:", character)
        winnings[(turn % 3)] = winnings[(turn % 3)] - 250
        break
    # Want to choose a consonant ... so spins wheel
    dollar = spin_wheel()
    if dollar == 0:
      print("Computer lost a turn")
      character = "_"
      break
    elif dollar == -1:
      print("Computer went backrupt")
      winnings[(turn % 3)] = 0
      character = "_"
      break
    else:
      print("Computer guessed:", character)
      break
  return character, dollar

def computer_turn_morse(showing, winnings, previous_guesses, turn):
  # Guess in the order that Samuel Morse identified for his code
  alphabet = "ETAINOSHRDLUCMFWYGPBVKQJXZ"
  dollar = 0
  for character in alphabet:
    if character in previous_guesses:
      continue
    if is_vowel(character):
      if winnings[(turn % 3)] < 250:
        continue
      else:
        print("Computer bought:", character)
        winnings[(turn % 3)] = winnings[(turn % 3)] - 250
        break
    # Want to choose a consonant ... so spins wheel
    dollar = spin_wheel()
    if dollar == 0:
      print("Computer lost a turn")
      character = "_"
      break
    elif dollar == -1:
      print("Computer went backrupt")
      winnings[(turn % 3)] = 0
      character = "_"
      break
    else:
      print("Computer guessed:", character)
      break
  return character, dollar

def computer_turn_oxford(showing, winnings, previous_guesses, turn):
  # From dictionary ... that's game optimized word not occurance of words
  # Concise Oxford Dictionary (9th edition, 1995) 
  # https://www3.nd.edu/~busiforc/handouts/cryptography/letterfrequencies.html

  alphabet = "EARIOTNSLCUDPMHGBFYWKVXZJQ"
  dollar = 0
  for character in alphabet:
    if character in previous_guesses:
      continue
    if is_vowel(character):
      if winnings[(turn % 3)] < 250:
        continue
      else:
        print("Computer bought:", character)
        winnings[(turn % 3)] = winnings[(turn % 3)] - 250
        break
    # Want to choose a consonant ... so spins wheel
    dollar = spin_wheel()
    if dollar == 0:
      print("Computer lost a turn")
      character = "_"
      break
    elif dollar == -1:
      print("Computer went backrupt")
      winnings[(turn % 3)] = 0
      character = "_"
      break
    else:
      print("Computer guessed:", character)
      break
  return character, dollar

def computer_turn_trigrams_bigrams(showing, winnings, previous_guesses, turn):

  allow_vowels = False
  if winnings[(turn % 3)] >= 250:
    allow_vowels = True

  candidate_trigrams = [] 
  showing_words = showing.split(' ')
  for word in showing_words:
    index = 0
    while index < (len(word) - 2):
      trigram = word[index:index+3]
      #print(trigram)
      if trigram[2] == "_" and "_" != trigram[0] and "_" != trigram[1]:
        candidate_trigrams.append(trigram)
      index = index + 1

  candidate_bigrams = [] 
  for word in showing_words:
    index = 0
    while index < (len(word) - 1):
      bigram = word[index:index+2]
      #print(bigram)
      if "_" != bigram[0] and bigram[1] == "_":
        candidate_bigrams.append(bigram)
      index = index + 1

  #print(candidate_trigrams)
  #print(candidate_bigrams)

  dollar = 0
  guess = "_"

  # Frewquencies from: http://mathcenter.oxford.emory.edu/site/math125/englishLetterFreqs/#:~:text=Most%20common%20bigrams%20(in%20order,%2C%20sa%2C%20em%2C%20ro.

  #Most common trigrams (in order)
  trigrams = ["THE", "AND", "THA", "ENT", "ING", "ION", "TIO", "FOR", "NDE", "HAS", "NCE", "EDT", "TIS", "OFT", "STH", "MEN"]
  for trigram in trigrams:
    to_match = trigram[0:2] + "_"
    #print("TOMatch", to_match)
    if to_match in candidate_trigrams:
      candidate = trigram[2]
      #print("CANDIDATE", candidate)
      if is_vowel(candidate) and allow_vowels == False:
        #print("can't vowel")
        continue
      elif candidate in previous_guesses:
        #print("already guessed")
        continue
      else:
        guess = candidate
        #print("Actual CANDIDATE", candidate)
        break
  if guess != "_":
    if is_vowel(guess):
      print("Computer bought:", guess)
      winnings[(turn % 3)] = winnings[(turn % 3)] - 250
      return guess, dollar # Should be a vowel and 0 since we've already subtraced
    else:
      dollar = spin_wheel()
      if dollar == 0:
        print("Computer lost a turn")
        guess = "_"
      elif dollar == -1:
        print("Computer went backrupt")
        winnings[(turn % 3)] = 0
        guess = "_"
      else:
        print("Computer guessed:", guess)
      return guess, dollar

  #print("No trigrams ... backing off to bigrams")

  #Most common bigrams (in order)
  #frequent bigrams from a file ... http://practicalcryptography.com/media/cryptanalysis/files/english_bigrams_1.txt Only want first 128
  #bigrams = ["TH", "HE", "IN", "EN", "NT", "RE", "ER", "AN", "TI", "ES", "ON", "AT", "SE", "ND", "OR", "AR", "AL", "TE", "CO", "DE", "TO", "RA", "ET", "ED", "IT", "SA", "EM", "RO"]
  bigrams = []
  with open("bigrams.txt") as g:
    for line in g:
      line = line.rstrip('\n')
      bigram = line.split(' ')[0].upper()
      bigrams.append(bigram)
      if len(bigrams) == 128:
        break # Arbitrary threshold to use
  #print(bigrams)
  for bigram in bigrams:
    to_match = bigram[0] + "_"
    #print(to_match)
    if to_match in candidate_bigrams:
      candidate = bigram[1]
      #print("CANDIDATE", candidate)
      if is_vowel(candidate) and allow_vowels == False:
        #print("can't vowel")
        continue
      elif candidate in previous_guesses:
        #print("already guessed")
        continue
      else:
        guess = candidate
        #print("Actual CANDIDATE", candidate)
        break
  if guess != "_":
    if is_vowel(guess):
      print("Computer bought:", guess)
      winnings[(turn % 3)] = winnings[(turn % 3)] - 250
      return guess, dollar # Should be a vowel and 0 since we've already subtraced
    else:
      dollar = spin_wheel()
      if dollar == 0:
        print("Computer lost a turn")
        guess = "_"
      elif dollar == -1:
        print("Computer went backrupt")
        winnings[(turn % 3)] = 0
        guess = "_"
      else:
        print("Computer guessed:", guess)
      return guess, dollar

  #print("No bigrams ... backing off to unigrams")

  # Unigrams are from the oxford strategy above
  alphabet = "EARIOTNSLCUDPMHGBFYWKVXZJQ"


  for character in alphabet:
    if character in previous_guesses:
      continue
    if is_vowel(character):
      if winnings[(turn % 3)] < 250:
        continue
      else:
        print("Computer bought:", character)
        winnings[(turn % 3)] = winnings[(turn % 3)] - 250
        break
    # Want to choose a consonant ... so spins wheel
    dollar = spin_wheel()
    if dollar == 0:
      print("Computer lost a turn")
      character = "_"
      break
    elif dollar == -1:
      print("Computer went backrupt")
      winnings[(turn % 3)] = 0
      character = "_"
      break
    else:
      print("Computer guessed:", character)
      break
  return character, dollar

def get_random_puzzle():
  random_int = random.randint(0,900) # Roughly size of num puzzles in valid
  number = 0
  with open("../../data/puzzles/valid.csv") as f:
    for line in f:
      line = line.rstrip('\n')
      puzzle, clue, date, game_type = line.split(',')
      if number == random_int:
        #print(line)
        clue = clue.replace("&amp;", "&") # HTML Code
        puzzle = puzzle.replace("&amp;", "&") # HTML Code
        return(puzzle, clue, date, game_type)
      number = number + 1

def human_turn(showing, winnings, previous_guesses, turn, puzzle):

  # Offer AI suggestion
  print("\n" + "="*50)
  print("🤖 Would you like an AI suggestion? (y/n)")
  suggestion_choice = input().lower().strip()
  if suggestion_choice == 'y' or suggestion_choice == 'yes':
    try:
      suggestion = get_human_suggestion(showing, winnings, previous_guesses, turn)
      print(suggestion)
    except Exception as e:
      print(f"Sorry, couldn't generate suggestion: {e}")
  print("="*50)

  # Make sure human chooses a valid action
  deciding = False
  while not deciding:
    decision = input("1: Spin, 2: Buy Vowel, 3: Solve, 4: Get AI Suggestion ....  ")
    if decision == "1" or decision == "2" or decision == "3":
      deciding = True
      if decision == "2" and winnings[(turn % 3)] < 250: # Minimum cost of a vowel
        print("Sorry .... you don't have enough money. Select 1 or 3")
        deciding = False
    elif decision == "4":
      # Show AI suggestion again
      try:
        suggestion = get_human_suggestion(showing, winnings, previous_guesses, turn)
        print(suggestion)
      except Exception as e:
        print(f"Sorry, couldn't generate suggestion: {e}")
    else:
      print("Please choose 1, 2, 3, or 4")

  # Player decisions
  if decision == "3":
    deciding = True
    solve = input("Your guess to solve: ...... ").upper() # TODO: clean
    if solve == puzzle:
      print("YOU WIN!")
      winnings[turn % 3] += 1000  # Add $1000 bonus for solving
      print("Player", turn % 3, "won!")
      print("Final winnings with $1000 solve bonus:", winnings)
      is_solved = True
      exit()
      #break #TODO: not just exit here
    else:
      print("Wrong ... next player")
      #turn = turn + 1
      #print("The clue is:", clue)
      #print_board(showing)
      #continue
      guess = "_"
      dollar = 0
  elif decision == "2":
    winnings[(turn % 3)] = winnings[(turn % 3)] - 250
    is_one_vowel = False
    while is_one_vowel != True:
      vowel = input("Guess a vowel: ").upper()
      if len(vowel) != 1:
        print("Guess only one letter")
      else:
        is_one_vowel = is_vowel(vowel)

      if not is_one_vowel:
        print("Not a vowel")
    guess = vowel
    dollar = 0
  elif decision == "1":
    # Spin wheel
    dollar = spin_wheel()
    guess = ""
    if dollar == 0:
      print("Sorry! Lose a turn. Next player")
      #turn = turn + 1
      #continue
      guess = "_"
    elif dollar == -1:
      print("Oh No! Bankrupt!")
      winnings[(turn % 3)] = 0
      #turn = turn + 1
      #continue
      guess = "_"
    is_one_consonant = False
    if guess == "_":
      is_one_consonant = True # Hacky way
    while is_one_consonant != True:
      guess = input("Name a consonant .... ").upper()
      if len(guess) != 1: 
        print("Guess only one letter")
      else:
        is_one_consonant = is_consonant(guess)

      if not is_one_consonant:
        print("Not a consonant")
  return guess, dollar

def is_consonant(guess):
  consonants = "BCDFGHJKLMNPQRSTVWXYZ"
  if guess in consonants:
    return True
  else:
    return False

def is_vowel(guess):
  vowels = "AEIOU"
  if guess in vowels:
    return True
  else:
    return False

def print_board(showing):
  words = showing.split(" ")
  to_print = ""
  for word in words:
    for character in word:
      to_print = to_print + character + " "
    to_print = to_print + "\n"
  print(to_print)

def spin_wheel():
  wheel_values = [0,-1,500,550,600,650,700,750,800,850,900,-1,500,550,600,650,700,750,800,850,900,500,550,600]
  # Note that the wheel changes over time ... free play now an 850. Different rounds, etc.
  print("Wheel is spinning ....")
  print("It landed on ....")
  time.sleep(2) # Drama!
  ascii_wheel.draw_ascii_wheel(wheel_values, radius=18, label_style="long")
  dollar = random.choice(wheel_values)
  print("....", dollar, "dollars")
  return dollar


def play_random_game(type_of_players):

  # Play the game
  puzzle, clue, date, game_type = get_random_puzzle()
  print("Welcome to Wheel of Fortune")
  print("You are playing a game of type:", game_type)
  print("The clue is:", clue)

  # Mask out word
  showing = puzzle
  showing = re.sub(r"[A-Z]","_",showing)
  print_board(showing)

  # Play the game
  guess = ""
  previous_guesses = []
  turn = 0

  winnings = [0,0,0]
  dollar = 0
  is_solved = False

  while showing != puzzle:
    time.sleep(2) # Let humans see what is going on
    # Ends wierd if last letter is guessed and not solved.# TODO
    print("It is player", turn % 3, "'s turn")

    # Type of player
    type_of_player = type_of_players[turn % 3]
    print("This player is:", type_of_player)

    if type_of_player == "human":
      guess, dollar = human_turn(showing, winnings, previous_guesses, turn, puzzle)
    elif type_of_player == "morse":
      guess, dollar = computer_turn_morse(showing, winnings, previous_guesses, turn)
    elif type_of_player == "oxford":
      guess, dollar = computer_turn_oxford(showing, winnings, previous_guesses, turn)
    # Main AI types
    elif type_of_player == "smart":
      guess, dollar = computer_turn_optimized(showing, winnings, previous_guesses, turn)
    elif type_of_player == "conservative":
      guess, dollar = computer_turn_optimized_conservative(showing, winnings, previous_guesses, turn)
    elif type_of_player == "aggressive":
      guess, dollar = computer_turn_optimized_aggressive(showing, winnings, previous_guesses, turn)
    
    # Advanced solve timing variants (integrated into main three)
    elif type_of_player == "solve_timing":
      guess, dollar = computer_turn_solve_timing_balanced(showing, winnings, previous_guesses, turn, puzzle, game_type)
    elif type_of_player == "solve_conservative":
      guess, dollar = computer_turn_solve_timing_conservative(showing, winnings, previous_guesses, turn, puzzle, game_type)
    elif type_of_player == "solve_aggressive":
      guess, dollar = computer_turn_solve_timing_aggressive(showing, winnings, previous_guesses, turn, puzzle, game_type)
    
    # Legacy support for old player types
    elif type_of_player in ["trigram", "basic", "computer"]:
      guess, dollar = computer_turn(showing, winnings, previous_guesses, turn)
    elif type_of_player in ["optimized", "opt_balanced"]:
      guess, dollar = computer_turn_optimized(showing, winnings, previous_guesses, turn)
    elif type_of_player == "opt_aggressive":
      guess, dollar = computer_turn_optimized_aggressive(showing, winnings, previous_guesses, turn)
    elif type_of_player == "opt_conservative":
      guess, dollar = computer_turn_optimized_conservative(showing, winnings, previous_guesses, turn)
    else:
      # Default case for unrecognized player types - use basic computer turn
      print(f"Warning: Unknown player type '{type_of_player}', using default computer turn")
      guess, dollar = computer_turn(showing, winnings, previous_guesses, turn)

    ## Human playing
    #if turn % 3 == 0:
    #  guess, dollar = human_turn(showing, winnings, previous_guesses, turn, puzzle)
    #
    ## Computer playing
    #elif turn % 3 == 1:
    #  guess, dollar = computer_turn_oxford(showing, winnings, previous_guesses, turn)
    #elif turn % 3 == 2:
    #  guess, dollar = computer_turn_morse(showing, winnings, previous_guesses, turn)


    # Check if this is a solve attempt
    if guess.startswith('SOLVE:'):
      solve_guess = guess[6:]  # Remove 'SOLVE:' prefix
      print(f"Player {turn % 3} attempts to solve: '{solve_guess}'")
      if solve_guess == puzzle:
        winnings[turn % 3] += 1000  # Add $1000 bonus for solving
        print(f"CORRECT! Player {turn % 3} solved the puzzle!")
        print("Final winnings:", winnings)
        return turn % 3  # Return winner
      else:
        print("Wrong solution ... next player")
        turn = turn + 1
    # Double check that guess has not already been said (I've seen it on TV before)
    elif guess in previous_guesses and guess != "_":
      print("Sorry, that's already been guessed .... next player")
      turn = turn + 1
    else:
      # Update board
      previous_guesses.append(guess)
      correct_places = []
      for pos,char in enumerate(puzzle):
        if(char == guess):
            correct_places.append(pos)
      #print(correct_places)
      if guess == "_": # Hacky way to say the comp got it wrong or bankrupt, etc.
        turn = turn + 1
      elif len(correct_places) < 1:
        print("Sorry, not in the puzzle ... next player")
        turn = turn + 1
      else:
        # Add winnings for correct letter guesses
        winnings[(turn % 3)] = winnings[(turn % 3)] + (dollar * len(correct_places))
        for correct_letter in correct_places:
          showing = showing[:correct_letter] + guess + showing[correct_letter + 1:]
    
    # Only print status if we're not solving
    if not guess.startswith('SOLVE:'):
      print("Winnings:", winnings)
      print("Previous guesses:", previous_guesses)
      print("The clue is:", clue)
      print_board(showing)

  while not is_solved:
    print("Player", turn % 3, "has a chance to solve")
    type_of_player = type_of_players[turn % 3] # wouldn't have hit this above
    # If human, let them guess, otheerwise let computer guess
    if type_of_player == "human":
      solve = input("Your guess to solve: ...... ").upper() # TODO: clean
    else:
      solve = showing
  
    if solve == puzzle:
      winnings[turn % 3] += 1000  # Add $1000 bonus for solving
      print("Player", turn % 3, "won!")
      print("Final winnings with $1000 solve bonus:", winnings)
      is_solved = True
    else:
      print("Wrong ... next player")
      turn = turn + 1
      print("The clue is:", clue)
      print_board(showing)

def show_player_types():
    """Display available player types and their descriptions."""
    print("\n=== Available Player Types ===")
    print("Main AI Types:")
    print("  smart          - Advanced AI with strategic analysis (balanced)")
    print("  conservative   - Conservative AI with risk-averse play")
    print("  aggressive     - Aggressive AI with high risk-taking")
    print("\nAdvanced Solve Timing AI:")
    print("  solve_timing   - AI that strategically times solve attempts (balanced)")
    print("  solve_conservative - Solve timing AI with conservative solving")
    print("  solve_aggressive - Solve timing AI with aggressive solving")
    print("\nSpecial Types:")
    print("  human          - Human player")
    print("\nLegacy Types (still supported):")
    print("  computer, basic, trigram, optimized, opt_aggressive, opt_conservative")
    print("\nExample usage:")
    print("  python play_random_puzzle.py smart conservative aggressive")
    print("  python play_random_puzzle.py solve_timing smart conservative")
    print("  python play_random_puzzle.py aggressive solve_aggressive smart\n")

if __name__ == '__main__':
  type_of_players = sys.argv[1:]
  print(type_of_players)
  if len(type_of_players) != 3:
    print("There should be 3 players ... creating a default game with modern AI players")
    show_player_types()
    type_of_players = ["smart", "conservative", "aggressive"] # Main three AI types
    time.sleep(3)
  #type_of_players = ["morse", "morse", "oxford"] # TODO: Set with command line

  play_random_game(type_of_players)



# TODO: Somehow when the comp buys E it messes things up ... (first letter for many strategies)
