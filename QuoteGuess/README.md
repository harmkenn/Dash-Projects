# 💭 Quote Guess Game

A multi-team trivia game where players identify who spoke famous Book of Mormon quotes. Features progressive hints with decreasing point values.

## Game Overview

**Quote Guess** is a team-based quiz game that challenges players to identify the speaker of classic Book of Mormon quotes. The game includes 100 carefully selected quotes from across the Book of Mormon and related scriptures.

### Key Features

- **100 Curated Quotes**: Spanning all major Book of Mormon figures and prophets
- **Progressive Hints**: Each quote has 3 hints that progressively reveal information about the speaker
- **Dynamic Scoring**: 
  - Base score: 300 points
  - Each hint revealed: -100 points
  - Correct answer with no hints: 300 points
  - Correct answer with all hints: 0 points
- **Multi-Team Support**: Play with 2-4 teams competing simultaneously
- **Team Rotation**: Turns automatically rotate between teams after each question
- **Game Customization**: Choose number of teams (2-4) and number of questions (5-100)

## How to Play

### Setup
1. Select the number of teams (2-4)
2. Select the number of questions (5-100)
3. Click "🔁 Start New Game"

### Gameplay
1. A quote is displayed on the screen
2. The current team tries to identify the speaker
3. Before guessing, teams can reveal up to 3 hints to help identify the speaker
4. Each hint reduces the available points by 100
5. Type the speaker's name and submit your answer
6. Points are awarded for correct answers (based on hints used)
7. Turns rotate to the next team
8. Continue until all questions are answered
9. The team with the most points wins!

### Scoring Breakdown

| Scenario | Points |
|----------|--------|
| Correct with 0 hints | 300 |
| Correct with 1 hint | 200 |
| Correct with 2 hints | 100 |
| Correct with 3 hints | 0 |
| Incorrect | 0 |

## Files

- **quote_guess_game.py**: Main game application with UI and game logic
- **quotes_data.py**: Database of 100 Book of Mormon quotes with speakers, references, and hints
- **README.md**: This file

## Data Structure

Each quote entry contains:
```python
{
    "quote": "The actual scripture quote",
    "speaker": "Person who said/was associated with the quote",
    "book": "Book of scripture",
    "chapter": "Chapter:verse reference",
    "hints": [
        "Hint 1 - General info about speaker",
        "Hint 2 - More specific background",
        "Hint 3 - Very specific identifying information"
    ]
}
```

## Technical Details

- Built with **Streamlit** for responsive web interface
- Uses **Session State** for game persistence
- Color-coded teams with team tracking
- Real-time score updates

## Example Quotes

Some of the featured quotes include:
- "This is my work and my glory—to bring to pass the immortality and eternal life of man." - Heavenly Father
- "Choose you this day whom ye will serve." - Joshua
- "I am the light and the life of the world." - Jesus Christ
- "Behold, I am Jesus Christ the Son of God." - Jesus Christ
- "By small and simple things are great things brought to pass." - Alma

## Running the Game

From the main launcher:
1. Select "💭 Quote Guess" from the sidebar
2. Configure your game settings
3. Click "🔁 Start New Game"
4. Enjoy!

## Tips for Playing

- Read the hint gradually to get a sense of who it might be
- Different speakers have distinct traits and roles in the Book of Mormon
- Familiar names may appear as speakers, authors, or people quoted
- Remember that some quotes are from visitors to the Americas (like Jesus Christ, angels, etc.)

## Future Enhancements

Possible additions:
- Difficulty levels (easy, medium, hard)
- Timed rounds
- Multiple choice options
- Player name tracking
- Game statistics/history
- Custom quote sets by book or time period
