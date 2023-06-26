import { useState } from "react";
import { FaTrash } from "react-icons/fa";

function App() {
  const [theme, setTheme] = useState("");
  const [words, setWords] = useState(
    [] as {
      word: string;
      description: string;
    }[]
  );
  const [error, setError] = useState("");
  const [generateNewWords, setGenerateNewWords] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [crossword, setCrossword] = useState(
    null as null | {
      name: string;
      url: string;
    }
  );

  let disableGenerate = false;
  if (theme.length === 0) {
    disableGenerate = true;
  }
  if (!generateNewWords && words.length === 0) {
    disableGenerate = true;
  }
  words.forEach((word) => {
    if (word.word.length === 0) {
      disableGenerate = true;
    }
  });
  if (fetching) {
    disableGenerate = true;
  }

  const alphabeticalWords = words.map((word) => {
    for (let i = 0; i < word.word.length; i++) {
      if (
        !(
          ("a".charCodeAt(0) <= word.word.charCodeAt(i) &&
            word.word.charCodeAt(i) <= "z".charCodeAt(0)) ||
          ("A".charCodeAt(0) <= word.word.charCodeAt(i) &&
            word.word.charCodeAt(i) <= "Z".charCodeAt(0))
        )
      ) {
        return false;
      }
    }
    return true;
  });
  if (alphabeticalWords.findIndex((isAlphabetical) => !isAlphabetical) !== -1) {
    disableGenerate = true;
  }

  return (
    <div className="max-w-xl m-auto p-5 space-y-7">
      <h1 className="text-center font-bold text-xl">3D Crossword Generator</h1>
      {error.length > 0 && (
        <p className="text-center text-red-700 bg-red-100 p-1">{error}</p>
      )}
      <input
        placeholder="Theme (required)"
        className="border px-1 w-full"
        disabled={fetching}
        value={theme}
        onChange={(e) => {
          if (crossword !== null) {
            URL.revokeObjectURL(crossword.url);
          }
          setCrossword(null);
          setTheme(e.target.value);
        }}
      />
      {words.map((word, index) => (
        <div key={index} className="space-y-3">
          {!alphabeticalWords[index] && (
            <p className="text-red-700">
              The word should only contain alphabets.
            </p>
          )}
          <div className="flex justify-between">
            <input
              placeholder="Word (required)"
              className="border px-1"
              disabled={fetching}
              value={word.word}
              onChange={(e) => {
                if (crossword !== null) {
                  URL.revokeObjectURL(crossword.url);
                }
                setCrossword(null);
                setWords([
                  ...words.slice(0, index),
                  {
                    word: e.target.value,
                    description: word.description,
                  },
                  ...words.slice(index + 1),
                ]);
              }}
            />
            <button
              onClick={() => {
                if (crossword !== null) {
                  URL.revokeObjectURL(crossword.url);
                }
                setCrossword(null);
                setWords([...words.slice(0, index), ...words.slice(index + 1)]);
              }}
              disabled={fetching}
            >
              <FaTrash />
            </button>
          </div>
          <textarea
            placeholder="Description (optional)"
            className="border px-1 w-full"
            disabled={fetching}
            value={word.description}
            onChange={(e) => {
              if (crossword !== null) {
                URL.revokeObjectURL(crossword.url);
              }
              setCrossword(null);
              setWords([
                ...words.slice(0, index),
                {
                  word: word.word,
                  description: e.target.value,
                },
                ...words.slice(index + 1),
              ]);
            }}
          />
        </div>
      ))}
      <div className="flex justify-between">
        <span className="flex gap-1">
          <input
            type="checkbox"
            id="generateNewWords"
            disabled={fetching}
            checked={generateNewWords}
            onChange={(e) => {
              if (crossword !== null) {
                URL.revokeObjectURL(crossword.url);
              }
              setCrossword(null);
              setGenerateNewWords(e.target.checked);
            }}
          />
          <label htmlFor="generateNewWords">Generate new words</label>
        </span>
        <button
          disabled={fetching}
          onClick={() => {
            if (crossword !== null) {
              URL.revokeObjectURL(crossword.url);
            }
            setCrossword(null);
            setWords([
              ...words,
              {
                word: "",
                description: "",
              },
            ]);
          }}
        >
          + Add word
        </button>
      </div>
      <div className="flex justify-center">
        <button
          className={
            "bg-sky-600 text-white px-3 py-2 rounded" +
            (disableGenerate ? " opacity-50" : "")
          }
          disabled={disableGenerate}
          onClick={() => {
            const apiWords = words.map((word) => {
              if (word.description.length > 0) {
                return word;
              } else {
                return {
                  word: word.word,
                };
              }
            });
            const apiWordsString = encodeURIComponent(JSON.stringify(apiWords));
            const apiTheme = encodeURIComponent(theme);
            const url = `/api?theme=${apiTheme}&words=${apiWordsString}${
              generateNewWords ? "" : "&noNewWords"
            }`;
            if (crossword !== null) {
              URL.revokeObjectURL(crossword.url);
            }
            setCrossword(null);
            setFetching(true);
            setError("");
            fetch(url)
              .then(async (response) => {
                const json = await response.json();
                const file = new File([JSON.stringify(json)], `${theme}.json`, {
                  type: "application/json",
                });
                const newFileURL = URL.createObjectURL(file);
                setCrossword({
                  name: `${theme}.json`,
                  url: newFileURL,
                });
                setFetching(false);
              })
              .catch(() => {
                setError("Couldn't create the crossword.");
                setFetching(false);
              });
          }}
        >
          Generate
        </button>
      </div>
      {crossword !== null && (
        <div className="flex justify-center">
          <a
            href={crossword.url}
            className="bg-sky-600 text-white px-3 py-2 rounded"
            download={crossword.name}
          >
            Download crossword
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
