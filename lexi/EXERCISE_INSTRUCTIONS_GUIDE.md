# Exercise Instructions Guide

This guide explains how users should provide input for each type of exercise in the Lexi learning platform.

## Exercise Types and Input Methods

### 1. **Spelling Exercises** 📝

**What the user sees:**
- Incomplete words with missing letters (e.g., "d_g", "c_t", "r_n")
- Pattern hints (e.g., "CVC pattern")

**How to answer:**

**Single Word:**
- Look at the incomplete word: 'd_g'
- Figure out the missing letter
- Type the complete word: `dog`

**Multiple Words:**
- Look at all incomplete words: 'd_g, c_t, r_n'
- Fill in the missing letter for EACH word
- Type ALL complete words separated by commas: `dog, cat, run`

**Example:**
```
Exercise: Complete these words: c_t, d_g, p_n
User types: cat, dog, pen
```

---

### 2. **Sight Words Exercises** 👀

#### A. Flash Cards
**What the user sees:**
- A list of sight words to practice (e.g., "the, and, is, to, you")

**How to answer:**
- Read each word carefully
- Type ONE word at a time
- System will confirm if correct before moving to next

**Example:**
```
Words to practice: the, and, is
User types: the
System: ✅ Perfect!
User types: and
System: ✅ Perfect!
```

#### B. Sentence Completion
**What the user sees:**
- Sentences with blanks: "I ___ going to school"
- Word choices: "am, is, are"

**How to answer:**
- Read the sentence with the blank
- Choose the correct sight word
- Type the COMPLETE sentence with your word filled in

**Example:**
```
Sentence: I ___ going to school.
Options: am, is, are
User types: I am going to school.
```

---

### 3. **Writing Exercises** ✍️

**What the user sees:**
- A word bank with multiple words (e.g., "cat, sat, mat, the, on")

**How to answer:**
- Use ALL the words provided
- Create ONE complete sentence
- Make sure it makes sense
- Start with a capital letter and end with punctuation

**Example:**
```
Word bank: cat, sat, mat, the, on
User types: The cat sat on the mat.
```

**Tips:**
- You can use the words in any order
- Add small words like "a", "the" if needed
- Be creative!

---

### 4. **Phonics Exercises** 🔤

#### A. Sound Out
**What the user sees:**
- Words to sound out (e.g., "cat, dog, run")

**How to answer:**
- Look at each word
- Sound out each letter (c-a-t = cat)
- Type the word you hear
- Type one word at a time

**Example:**
```
Practice words: cat, dog
User types: cat
System: ✅ Perfect!
User types: dog
System: ✅ Perfect!
```

#### B. Word Building (Single Word)
**What the user sees:**
- Letters provided: "c, a, t"
- Instruction to build a word

**How to answer:**
- Look at the letters provided
- Build a word using those letters
- Type the word

**Example:**
```
Letters: c, a, t
User types: cat
```

#### C. Word Building (Multiple Words)
**What the user sees:**
- Multiple sets of letters
- Example: "Letters for word 1: c, a, t | Letters for word 2: d, o, g"

**How to answer:**
- Build a word from each set of letters
- Type ALL the words separated by spaces

**Example:**
```
Build 2 words from: [c,a,t] and [d,o,g]
User types: cat dog
```

---

### 5. **Reading Comprehension Exercises** 📚

**What the user sees:**
- A passage to read
- Questions about the passage

**How to answer:**
- Read the passage carefully
- Read the question
- Answer in your own words
- Type your answer (can be a phrase or sentence)

**Example:**
```
Passage: "The cat sat on the mat. The cat was happy."
Question: What is the main idea?
User types: The story is about a cat sitting on a mat.
```

**Tips:**
- Look for details in the text
- There's no single "correct" way to phrase your answer
- Answer based on what you understood

---

## General Tips for All Exercises

1. **Read instructions carefully** - Each exercise type has specific requirements
2. **Take your time** - There's no rush
3. **Ask for help** - Type "how do I answer this?" if confused
4. **Check your spelling** - Especially for writing exercises
5. **Use punctuation** - Capital letters and periods for sentences
6. **One step at a time** - For multi-part exercises, complete one part at a time

---

## Getting Help During Exercises

**If you're stuck, you can ask:**
- "How do I answer this?"
- "What should I do?"
- "Can you explain?"
- "Show me an example"

**The system will provide:**
- Clear step-by-step instructions
- Examples of correct answers
- Hints and tips
- Encouragement and support

---

## System Responses

After you submit your answer, the system will:
- ✅ Confirm if correct with encouragement
- 📝 Provide feedback if incorrect
- 💡 Offer tips and suggestions
- 🌟 Celebrate your progress
- 🎯 Guide you to the next step

---

## Example Conversation Flow

```
System: Here are 5 words for you to practice:
1. cat
2. dog  
3. run
4. sit
5. big

📝 Challenge: Try using ALL 5 words in a sentence!

User: how do I answer this?

System: ✍️ How to answer this writing exercise:
1. Use ALL these words: cat, dog, run, sit, big
2. Create ONE complete sentence
3. Make sure it makes sense

Example: If words are 'cat, sat, mat', you could write: "The cat sat on the mat."

✍️ Now type your sentence!

User: The big cat and dog run and sit.

System: 🌟 Fantastic sentence! You used all 5 words!

Your sentence: "The big cat and dog run and sit."

Great job putting them together!
```

---

## Important Notes

1. **Active Exercise Context**: When you have an active exercise, your input will be evaluated against that exercise
2. **New Requests**: To get new words or start a new exercise, say "give me different words" or "new words"
3. **Completion**: After completing an exercise, ask for new words to continue practicing
4. **Flexibility**: The system understands various phrasings - don't worry about exact wording

---

## Technical Implementation

The system uses the `_handle_help_request()` method in `ai_tutor.py` to provide context-aware instructions based on:
- Active exercise type (skill_area)
- Exercise subtype (exercise_type)
- Current exercise data (words, sentences, questions, etc.)

When a user asks "how do I answer this?", the system:
1. Checks if there's an active exercise
2. Identifies the exercise type
3. Provides specific instructions with examples
4. Offers relevant tips and suggestions
