import os
import openai
import random
from flask import Flask, request
import re
import json

# https://stackoverflow.com/a/62376955

openai.api_key = os.getenv("OPENAI_API_KEY")

CROSSWORD_DESCRIPTION = """
I'll give you a theme for a crossword. Generate a crossword using the theme.
The format of the crossword will be pairs of lines. The first line will be the word and the second line will be the description of the word.

An example crossword:
Hello
Greeting
World
Universe

Generate a crossword with the theme: {}.
Don't use the following words: {}.
"""

DESCRIPTION_GENERATION = """
Generate crossword descriptions for the following words:
{}
The theme of the crossword is {}.
Your reply must be pairs of lines, where the first line is the word and the second line is the description.
The description must be a single line.
"""

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
        return { "error": "The theme must be nonempty." }, 400

    generate_new_words = not 'noNewWords' in request.args
    words = request.args.get('words', '[]')
    try:
        words = json.loads(words)
        assert type(words) == list
        if len(words) == 0 and not generate_new_words:
            return { "error": "No words have been given and noNewWords is true." }, 400
        for word in words:
            assert type(word["word"]) == str and len(word["word"]) > 0
            for letter in word["word"]:
                assert ord('A') <= ord(letter) <= ord('Z')
            assert not "description" in word or type(word["description"]) == str and len(word["description"]) > 0
    except:
        return { "error": "Incorrect words." }, 400

    descriptions = {}
    words_without_descriptions = set()
    for word in words:
        if not "description" in word:
            words_without_descriptions.add(word["word"])
        else:
            descriptions[word["word"]] = word["description"]

    if len(words_without_descriptions) > 0:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": DESCRIPTION_GENERATION.format(", ".join([word for word in words_without_descriptions]), theme)
                    }
                ],
                temperature=0.6
            )

            words_and_descriptions = response['choices'][0]['message']['content']
            words_and_descriptions = [line.strip() for line in words_and_descriptions.split('\n') if line.strip() != ""]
            for i in range(0, len(words_and_descriptions), 2):
                word = words_and_descriptions[i]
                description = words_and_descriptions[i+1]
                if word in words_without_descriptions:
                    descriptions[word] = description
                    words_without_descriptions.remove(word)
            if len(words_without_descriptions) > 0:
                raise "Incomplete descriptions"
        except:
            return { "error": "Could not generate the crossword." }, 500

    if generate_new_words:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": CROSSWORD_DESCRIPTION.format(theme, [word for word in descriptions])
                    }
                ],
                temperature=0.6
            )
        except:
            return { "error": "Could not generate the crossword." }, 500

        words_and_descriptions = response['choices'][0]['message']['content']
        words_and_descriptions = [line.strip() for line in words_and_descriptions.split('\n') if line.strip() != ""]
        for i in range(0, len(words_and_descriptions), 2):
            if i+1 >= len(words_and_descriptions):
                break
            word = words_and_descriptions[i].upper()
            word = re.sub('\d', '', word)
            word = re.sub('\W', '', word)
            description = words_and_descriptions[i+1]
            if not word in descriptions:
                descriptions[word] = description

    words = [word for word in descriptions]
    crossword = [(words[0], (0, 0, 0), "X")]
    words = set(words[1:])

    # How we choose the remaining words:
    # i) Calculate the currently placed letters in the crossword for each position.
    # Also store the directions of the words the letter belongs to.
    # ii) For each direction X, Y and Z, give them a random score from 0 to 1.
    # iii) For each word in the remaining words, go through each letter of the word.
    # - Find matches of the letter with the currently placed letters.
    # - For each match, consider placing the word with the letters in the match coinciding.
    # Consider each direction and check if placing the word there would cause any clashes.
    # Also make sure that the word only intersects with atmost one word per letter
    # (no 3 words should intersect at the same letter),
    # and has a different direction than all the words it intersects with.
    # - If there are no clashes, give the (word, start, direction)
    # a score of (-number_of_adjacent_letters, score of the word's direction).
    # - Choose one of the (word, start, direction) with the largest score. If no words can be chosen,
    # place a word at the right of the crossword.
    # iv) Repeat the above steps until all words are chosen.
    while len(words) > 0:
        current_letters = {} # Currently placed letters
        for (word, start, direction) in crossword:
            for i, letter in enumerate(word):
                letter_position = word_letter_position(i, start, direction)
                if letter_position in current_letters:
                    directions = current_letters[letter_position][1]
                    if not direction in directions:
                        directions.append(direction)
                else:
                    current_letters[letter_position] = (letter, [direction])

        # We set a random direction score to create a preference order among the directions.
        direction_score = {
            "X": random.random(),
            "Y": random.random(),
            "Z": random.random()
        }
        best = None
        for word in words:
            for letter_index, letter in enumerate(word):
                for current_letter_position, (current_letter, _) in current_letters.items():
                    if letter != current_letter:
                        continue
                    for direction in ["X", "Y", "Z"]:
                        start = word_letter_position(-letter_index, current_letter_position, direction)
                        valid = True
                        for i, letter in enumerate(word):
                            current_letter_at_position = current_letters.get(word_letter_position(i, start, direction))
                            if current_letter_at_position != None:
                                (current_letter, directions) = current_letter_at_position
                                if letter != current_letter or len(directions) > 1 or direction in directions:
                                    valid = False
                                    break
                        if valid:
                            adjacent = 0
                            for adjacent_direction in ["X", "Y", "Z"]:
                                if adjacent_direction == direction:
                                    before_start = word_letter_position(-1, start, direction)
                                    if before_start in current_letters:
                                        adjacent += 1
                                    after_end = word_letter_position(len(word), start, direction)
                                    if after_end in current_letters:
                                        adjacent += 1
                                else:
                                    for i in range(len(word)):
                                        position = word_letter_position(i, start, direction)
                                        for j in [-1, 1]:
                                            adjacent_position = word_letter_position(j, position, adjacent_direction)
                                            if adjacent_position in current_letters:
                                                adjacent += 1
                            score = (-adjacent, direction_score[direction])
                            if best == None or best[0] < score:
                                best = (score, (word, start, direction))
        if best == None:
            rightmost = (0, 0, 0)
            for position in current_letters:
                if position[0] > rightmost[0]:
                    rightmost = position
            start = (rightmost[0] + 2, rightmost[1], rightmost[2])
            crossword.append((words.pop(), start, "X"))
        else:
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