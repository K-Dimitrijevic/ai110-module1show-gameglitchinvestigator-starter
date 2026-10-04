# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
I noticed numerous bugs but some notable ones were:
  * History in the debug menu not being accurate.
  * Scoring being innaccurate when winning or losing
  * The hints were backwards, which was the most obvious bug.
**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guessed `100`, then typed `12` and clicked "Submit Guess" | Debug menu History showed `[100, 12]` | First click did nothing but when clicking again, it re-submitted the previous guess, so History showed `[100, 100]` | None. The text box and the button were sending their updates separately |
| Lost a game on 5 wrong guesses, then checked the Developer Debug Info | "Out of attempts!" score and debug Score matched | Message said `Score: -25` while the debug menu said `-20`. The score also carried over into the next game | None. The debug panel was drawn before the guess was scored |

| Guessed correctly on the first try | High score for a first-try win (100) | Final score was `70`; some wrong "Too High" guesses also *added* 5 points | None. No error; win formula was `100 - 10 * (attempt + 1)` and the counter started at 1 |

| Secret `50`, guessed `60` | Hint says "📉 Go LOWER!" | Hint said "📈 Go HIGHER!" (and "Too Low" said "Go LOWER!") | No error was detected were swapped in `check_guess` by AI as prompted|

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
    * I used Claude as my AI coding assistant

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
    * I didn't exactly ask it for advice beyond making sure I was properly using my venv correctly. I did have it look for bugs on its own and it correctly verified 5 issues that I didn't notice, all of which were true issues.

- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
    * Claude pointed out that the Hard difficulty (Which I had set to 1-200) was too luck based with only 5 available guesses. I chose to ignore that because the nature of the game is technically entirely luck based and so I was fine with keeping the guesses low since that wasn't really a "bug".

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
    *I read the code that was modified and ran the tests on top of verifying if they were properly fixed by running the game
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
    A "manual" test I did was running a lost game and a game that I won. I noticed that the history wouldn't be documented correctly in the debug logs and would in fact print my last number attempt instead of my current one. I also noticed that the scoring would be off whether I'd win or lose
- Did AI help you design or understand any tests? How?
    The AI created 16 additional tests each of which to verify if a bug has returned by playing out the exact situation I told the AI in appeared in. A primary example being the hints test where it checks if the words are correct.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
    * It'd basically be like saying it's a script that constantly runs from the start whenever people interact with it.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
    * I made a deliberate effort of being very specific and keeping the prompts curt without redundant language so as to avoid confusing the AI
- What is one thing you would do differently next time you work with AI on a coding task?
    * I might try initially prompting it to find and list all the errors it finds to begin before prompting it to start fixing them so as to save on tokens more efficiently
- In one or two sentences, describe how this project changed the way you think about AI generated code.
    * I can see the value in debugging and proficiently creating tests. It saves a significant amount of time whereas otherwise I'd be spending hours to do what it did in the span of minutes.

