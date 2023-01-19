# Texas-Hold'Em
This is a simple game of Texas Hold'em Poker made in Python.

# Game Flow

The game starts off first by issuing the User and CPU 2 cards before asking the User to call, bet or fold. 

Next, 3 community cards are drawn, and the User is asked to make a decision. If the User calls or bets, another card is drawn.

This repeats until 5 community cards have been drawn, or the User has folded.

After that, the Showdown occurs, where CPU cards are revealed to the player, as well as the CPU's hand's strengh. Once done, the game decides the winner and prompts the User whether they want to play again.

# Features implemented

Automatically determine the strength of the User's Hand, and displays it for the user.

Kickers implemented to determine the best hand if both Hands have the same win condition

(e.g Both CPU and User have a Ten-High Three Of a Kind, but CPU wins over User as CPU has a King Kicker over the Player's Queen Kicker)
