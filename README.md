# 3d-crossword-generation
A Flask API for generating crosswords for [3D crossword](https://github.com/ShouvikGhosh2048/3d-crossword).

It uses OpenAI's gpt-3.5-turbo for word and description generation, and a greedy search for word placement.

To use this project, you'll need to set an environment variable `OPENAI_API_KEY` with the OpenAI API key and then run main.py with Flask.

## API
There is only one route - "/".
You can `GET` the route with the following query parameters:
- `theme`: The theme of the crossword.
- `words`: User provided words in JSON. The JSON will be an array of objects. The object fields are:
  - `word`(required): The word. It must be a non-empty string and consist of only uppercase letters.
  - `description`(optional): The description of the word. If not provided, the description will be generated. Must be non-empty if provided.
- `noNewWords`: If present in the URL, no new words are generated. (This parameter doesn't require any value.)

## Idea
The project idea came from [Saham](https://www.linkedin.com/in/saham-sil-943112277/).
