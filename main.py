import os
import openai
import random
from flask import Flask, request
import re

openai.api_key = os.getenv("OPENAI_API_KEY")

CROSSWORD_DESCRIPTION = """
I'll give you a theme for a crossword. Generate a crossword using the theme.
The format of the crossword will be pairs of lines. The first line will be the word and the second line will be the description of the word.

An example crossword:
Hello
Greeting
World
Universe

Generate a crossword with the theme - """

def word_letter_position(index, start, direction):
    if direction == "X":
        letter_position = (start[0] + index, start[1], start[2])
    elif direction == "Y":
        letter_position = (start[0], start[1] - index, start[2])
    else:
        letter_position = (start[0], start[1], start[2] + index)
    return letter_position

app = Flask(__name__)

@app.route("/")
def generate_crossword():
    theme = request.args.get('theme', '')
    if theme == '':
        return "The theme must be nonempty.", 400
    prompt = CROSSWORD_DESCRIPTION + theme

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )
    except:
        return "Could not generate the crossword.", 500

    words_and_descriptions = response['choices'][0]['message']['content']
    words_and_descriptions = [line.strip() for line in words_and_descriptions.split('\n')]
    descriptions = {}
    for i in range(0, len(words_and_descriptions), 2):
        word = words_and_descriptions[i].upper()
        word = re.sub('\d', '', word)
        word = re.sub('\W', '', word)
        description = words_and_descriptions[i+1]
        descriptions[word] = description

    words = [word for word in descriptions]
    crossword = [(words[0], [0, 0, 0], "X")]
    words = set(words[1:])

    # How we choose the remaining words:
    # i) Calculate the currently placed letters in the crossword.
    # ii) For each direction X, Y and Z, give them a random score from 0 to 1.
    # iii) For each word in the remaining words, go through each letter of the word.
    # - Find matches of the letter with the currently placed letters.
    # - For each match, consider placing the word with the letters in the match coinciding.
    # Consider each direction and check if placing the word there would cause any clashes.
    # - If there are no clashes, give the (word, start, direction)
    # a score of (number_of_intersections of the word with the currently placed letters, score of the word's direction).
    # - Choose one of the (word, start, direction) with the largest score. If no words can be chosen, break out the loop.
    # iv) Repeat the above steps.
    while len(words) > 0:
        current_letters = {} # Currently placed letters
        for (word, start, direction) in crossword:
            for i, letter in enumerate(word):
                letter_position = word_letter_position(i, start, direction)
                current_letters[letter_position] = letter

        # We set a random direction score to create a preference order among the directions.
        direction_score = {
            "X": random.random(),
            "Y": random.random(),
            "Z": random.random()
        }
        best = None
        for word in words:
            for letter_index, letter in enumerate(word):
                for current_letter_position, current_letter in current_letters.items():
                    if letter != current_letter:
                        continue
                    for direction in ["X", "Y", "Z"]:
                        start = word_letter_position(-letter_index, current_letter_position, direction)
                        intersections = 0
                        valid = True
                        for i, letter in enumerate(word):
                            current_letter_at_position = current_letters.get(word_letter_position(i, start, direction))
                            if current_letter_at_position != None:
                                if letter == current_letter_at_position:
                                    intersections += 1
                                else:
                                    valid = False
                                    break
                        score = (intersections, direction_score[direction])
                        if valid and (best == None or best[0] < score):
                            best = (score, (word, start, direction))
        if best == None:
            break
        crossword.append(best[1])
        words.remove(best[1][0])

    return {
        "name": theme,
        "words": [{
            "word": word,
            "direction": direction,
            "start": start,
            "description": descriptions[word]
        } for (word, start, direction) in crossword]
    }