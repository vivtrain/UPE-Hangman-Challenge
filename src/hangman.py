import math
import time
import json
import requests
import random
from collections import OrderedDict

url = "http://upe.42069.fun/Bhocy"
email = "vivekkumar@g.ucla.edu"
dictionary = "10k.txt"

def main():
  try: # to catch Ctrl-C and suppress Traceback
    # Start with a clean slate, init game
    reset = requests.post(url + "/reset", data={"email" : email})

    # Keep running
    while True:
      # Get initial state
      hm_response = requests.get(url)
      hm_data = hm_response.json()
      print hm_data
      # Guessing
      while (hm_data["status"] == "ALIVE"):

        # Get the state of the game
        print "\n***********************"
        print(">> Response from " + url)
        print(hm_data)

        # Count the number of letters in the phrase
        statestr = hm_data["state"]
        length = 0
        for i in statestr:
          if i == '_':
            length += 1
        print(">> Number of letters left: " + str(length))

        # Parse into words
        words = dict()
        word = ""
        for ch in statestr:
          if ch == ' ':
            words[word] = 0
            word = ""
          else:
            word += ch
        words[word] = 0

        # Pick the word with most known leters
        for w in words:
          for l in w:
            if l != '_' and l.isalpha():
              words[w] = words[w] + 1
        print words
        maxknownlets = -1
        maxknownword = ""
        for w in words.keys():
          print w, words[w], maxknownlets
          if words[w] > maxknownlets:
            maxknownlets = words[w]
            maxknownword = w

        # Make a profile of letter frequencies
        profile = Letter_Freq_Map(dictionary, maxknownword)
        print(">> profile of: " + maxknownword)

        # Use the profile to generate a guesser
        guesser = Letter_Guesser(profile)

        # Guess a letter
        letter = guesser.guess_letter()
        hm_response = requests.post(url, \
          data={"guess" : letter})
        hm_data = hm_response.json()

        # Don't die the server
        time.sleep(1)
      print "\n"
      print hm_data["status"]
      print hm_data["lyrics"]
      print "\n\n"

  except KeyboardInterrupt:
    print ""


class Letter_Freq_Map:
  def __init__(self, filename, curword):
    self.freq_map = dict()
    for i in "abcdefghijklmnopqrstuvwxyz":
      self.freq_map[i] = 0

    f = open(filename)
    words = list()
    for word in f.read().splitlines():
      if len(word) == len(curword):
        match = True
        for l in range(0, len(word)):
          if curword[l] == '_' or word[l] == curword[l]:
            continue
          match = False
          break
        if match:
          words.append(word)
          for l in word:
            self.freq_map[l] = self.freq_map[l] + 1;
    if len(words) == 0:
      self.freq_map = \
      { 'e' : 12.02, 't' : 9.10, 'a' : 8.12, 'o' : 7.68,
        'i' :  7.31, 'n' : 6.95, 's' : 6.28, 'r' : 6.02,
        'h' :  5.92, 'd' : 4.32, 'l' : 3.98, 'u' : 2.88,
        'c' :  2.71, 'm' : 2.61, 'f' : 2.30, 'y' : 2.11,
        'w' :  2.09, 'g' : 2.03, 'p' : 1.82, 'b' : 1.49,
        'v' :  1.11, 'k' : 0.69, 'x' : 0.17, 'q' : 0.11,
        'j' :  0.10, 'z' : 0.07 }

  def combine(self, other):
    for letter in self.freq_map:
      self.freq_map[letter] = self.freq_map[letter] + other.freq_map[letter]


class Letter_Guesser:
  def __init__(self, freqmap):
    # Seed RNG
    random.seed()
    self.letter_profile = freqmap

  def guess_letter(self):
    cursum = 1
    sums = OrderedDict()
    for letter, freq in self.letter_profile.freq_map.items():
      cursum += freq
      sums[letter] = round(cursum, 4)

    index = random.uniform(1, cursum)
    for letter, runningsum in sums.items():
      if index < runningsum:
        guess = letter
        break

    for letter, freq in self.letter_profile.freq_map.items():
      self.letter_profile.freq_map[letter] = \
        round(freq / float(cursum - self.letter_profile.freq_map[guess])*100, 4)
    self.letter_profile.freq_map[guess] = 0
    print ">> guessing: " + guess
    return guess

if __name__ == "__main__":
  main()


  """
    self.letter_freqs = OrderedDict(
     [('e',12.02), ('t', 9.10), ('a', 8.12), ('o', 7.68),
      ('i', 7.31), ('n', 6.95), ('s', 6.28), ('r', 6.02),
      ('h', 5.92), ('d', 4.32), ('l', 3.98), ('u', 2.88),
      ('c', 2.71), ('m', 2.61), ('f', 2.30), ('y', 2.11),
      ('w', 2.09), ('g', 2.03), ('p', 1.82), ('b', 1.49),
      ('v', 1.11), ('k', 0.69), ('x', 0.17), ('q', 0.11),
      ('j', 0.10), ('z', 0.07)]) """