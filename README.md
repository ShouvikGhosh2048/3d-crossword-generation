# 3d-crossword-generation
A Flask website for generating crosswords for [3D crossword](https://github.com/ShouvikGhosh2048/3d-crossword).

It uses OpenAI's gpt-3.5-turbo for word and description generation.

<img width="960" alt="example" src="https://github.com/ShouvikGhosh2048/3d-crossword-generation/assets/91585022/7edbfa9c-3548-4133-a736-8af74e6e9311">

## Using project
- From the frontend folder, run:
  
  ```
  npm install
  npm run build
  ```
- Set an environment variable `OPENAI_API_KEY` with the OpenAI API key.
- Install flask and flask-cors and run flask with main.py.

## Routes
There are two routes - "/" and "/api".

"/" is the route for the website.

"/api" is the route for the API.
You can `GET` the route with the following query parameters:
- `theme`: The theme of the crossword.
- `words`: User provided words in JSON. The JSON will be an array of objects. The object fields are:
  - `word` (required): The word. It must be a non-empty string and consist of only letters.
  - `description` (optional): The description of the word. If not provided, the description will be generated. Must be non-empty if provided.
- `noNewWords`: If present in the URL, no new words are generated. (This parameter doesn't require any value.)

The route returns a JSON object with a crossword (or an error if the server was unable to generate a crossword).

## Idea
The project idea came from [Saham](https://www.linkedin.com/in/saham-sil-943112277/).
