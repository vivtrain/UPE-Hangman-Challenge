import math
import time
import json
import requests
import random
from collections import OrderedDict

url = "http://upe.42069.fun/Bhocy"
email = "vivekkumar@g.ucla.edu"
dictionary = "lyricdict.txt"
alphabet = "abcdefghijklmnopqrstuvwxyz"
defaultfreqs = \
  { 'e' : 12.02, 't' : 9.10, 'a' : 8.12, 'o' : 7.68,
    'i' :  7.31, 'n' : 6.95, 's' : 6.28, 'r' : 6.02,
    'h' :  5.92, 'd' : 4.32, 'l' : 3.98, 'u' : 2.88,
    'c' :  2.71, 'm' : 2.61, 'f' : 2.30, 'y' : 2.11,
    'w' :  2.09, 'g' : 2.03, 'p' : 1.82, 'b' : 1.49,
    'v' :  1.11, 'k' : 0.69, 'x' : 0.17, 'q' : 0.11,
    'j' :  0.10, 'z' : 0.07 }
guessedLetters = dict()

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
      for l in alphabet:
        guessedLetters[l] = 0

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
            if ch.isalpha() or ch == '-' or ch == '\'' or ch == '_':
              word += ch
        words[word] = 0
        """
        profile = Letter_Freq_Map(None, None)
        for w in words:
          contains_ = False
          for l in w:
            if l == '_':
              contains_ = True
              break
          if contains_:
            profile.combine(Letter_Freq_Map(dictionary, w))
        """
        # Pick the word with most known leters
        # Make a profile of letter frequencies
        guesser = Letter_Guesser()
        for w in words:
          yetUnknown = False
          for l in w:
            if l == '_':
              yetUnknown = True
            if l != '_' and l.isalpha():
              words[w] = words[w] + 1
          if not yetUnknown:
            words[w] = -1
        print words
        maxknownlets = -1
        maxknownword = ""
        for w in words.keys():
          if words[w] > maxknownlets:
            if not guesser.load(dictionary, w, False):
              continue
            maxknownlets = words[w]
            maxknownword = w

        wordknown = guesser.load(dictionary, maxknownword, True)
        print(">> profile of: " + maxknownword)

        # Guess a letter
        guess = guesser.guess_letter()
        counter = 0
        """
        while guessedLetters[guess] == 1:
          guess = guesser.guess_letter()
          print "try again ", guess
          counter = counter + 1
          if counter >= 100:
            guesser.load(dictionary, "_", False)
            counter = 0
        print ">> guessing: ", guess
        guessedLetters[guess] = 1
        """
        print ">> guessing: ", guess

        # Post a guess
        hm_response = requests.post(url, \
          data={"guess" : guess})
        hm_data = hm_response.json()

        # Don't die the server
        time.sleep(1)
      print "\n"
      print hm_data["status"]
      print hm_data["lyrics"]
      with open("gatheredlyrics.txt", "a") as myfile:
          myfile.write(hm_data["lyrics"] + '\n')
      print "\n\n"

  except KeyboardInterrupt:
    print ""


class Letter_Guesser:
  def __init__(self):
    self.freqs = dict()
    for i in alphabet:
      self.freqs[i] = 0

  def load(self, filename, curword, verbose):
    for i in alphabet:
      self.freqs[i] = 0
    f = open(filename)
    words = list()
    for word in f.read().splitlines():
      if len(word) == len(curword):
        match = True
        for l in range(0, len(word)):
          if curword[l] == '_' or word[l]==curword[l]:
            continue
          match = False
          break
        if match:
          if verbose:
            print word,
          words.append(word)
          for l in word:
            if l.isalpha():
              self.freqs[l] = self.freqs[l] + 1;
    if verbose:
      print ""
    if len(words) == 0:
      print "unknown word: ", curword
      self.freqs = defaultfreqs
      return False
    for l in alphabet:
      for lcmp in alphabet:
        if self.freqs[l] == self.freqs[lcmp]:
          if defaultfreqs[l] > defaultfreqs[lcmp]:
            self.freqs[l] = self.freqs[l] + 0.01
          elif defaultfreqs[l] < defaultfreqs[lcmp]:
            self.freqs[l] = self.freqs[l] - 0.01
    if verbose:
      print self.freqs
    return True

  def guess_letter(self):
    mostcommon = 'a'
    maxfreq = -1
    for l in alphabet:
      if self.freqs[l] > maxfreq and guessedLetters[l] == 0:
        maxfreq = self.freqs[l]
        mostcommon = l
    guessedLetters[mostcommon] = 1
    return mostcommon

  def combine(self, other):
    for l in alphabet:
      self.freqs[l] = self.freqs[l] + other.freqs[l]

"""
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
      cursum = round(cursum, 4)
      sums[letter] = cursum

    index = random.uniform(1, cursum)
    for letter, runningsum in sums.items():
      if index <= runningsum:
        guess = letter
        break
    for letter, freq in self.letter_profile.freq_map.items():
      self.letter_profile.freq_map[letter] = \
        round(freq / float(cursum - self.letter_profile.freq_map[guess])*100, 4)
    self.letter_profile.freq_map[guess] = 0
    return guess
"""

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
