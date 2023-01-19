# %%
import os
import random
from collections import Counter
from enum import Enum, auto
suits = ("Hearts","Diamonds","Clubs","Spades")
ranks = ("Two","Three","Four","Five","Six","Seven","Eight","Nine","Ten","Jack","Queen","King","Ace")
values = {'Two':2, 'Three':3,'Four':4,'Five':5,'Six':6,'Seven':7,'Eight':8,
        'Nine':9,'Ten':10,'Jack': 11,'Queen':12,'King':13,'Ace': 14}

# %%
class Card:
#Add card details to card class
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank] 
        pass

    def __str__(self) -> str:
        return f'{self.rank} of {self.suit}'

# %%
class HandCondition(Enum):
    High_Card = 0
    One_Pair = 1
    Two_Pair = 2
    Three_Of_A_Kind = 3
    Straight = 4
    Flush = 5
    Full_House = 6
    Four_Of_A_Kind = 7
    Straight_Flush = 8
    Royal_Flush = 9

# %%
def value_to_rank(cardint):
    #From a Card's value in integer, return Card's value in string
    for key,value in values.items():
        if cardint == value:
            return key
    #this REALLY shouldn't happen
    return False

def show_cards(communitycards):
    #returns the community cards
    printresult = ''
    for card in communitycards:
        printresult = str(card) + '|' + printresult
    return printresult

def hasFlush(clsHand):
    #Returns boolean on whether Flush exists or not, and highest value of only flush cards
    suits_dict = Counter([card.suit for card in clsHand.cards])
    suitname,count = suits_dict.most_common(1)[0]
    assert count != 0
    if count >= 5:
        FlushList = sorted([card.value for card in clsHand.cards if card.suit == suitname])
        return True, FlushList[-1]
    else:
        return False, 0
        
def hasStraight(clsHand):
    #Returns a boolean on whether straight exists or not
    acelowstraight = sorted((card.value == 1 if card.value == 14 else card.value) for card in clsHand.cards)
    acehighstraight = sorted(card.value for card in clsHand.cards)
    i = 0
    cardsinarow = 0

    while i < len(acelowstraight) -1:
        if acelowstraight[i] == 1:
            #Check for ace low straight(highest card must be 5)
            if (acelowstraight[i+1] == 2 and acelowstraight[i+2] == 3 and acelowstraight[i+3] == 4 and
                acelowstraight[i+4] == 5):
                return True,5
            else:
                noOfCardsInARow = 0
                i += 1
        if acehighstraight[i+1] - acehighstraight[i] == 1:
            cardsinarow +=1
            if cardsinarow ==4:
                return True,acelowstraight[i+1]
            else:
                i += 1
        else:
            noOfCardsInARow = 0
            i += 1
    #no straight
    return False,0

def has2P(clsHand):
    #Returns whether 1 Pair, 3 Of a Kind, 4 Of a Kind, 2 Pair or Full House, alongside highcard value.
    #If kicker enabled, returns kicker values.
    highvalue = 0
    counteddict = Counter([card.value for card in clsHand.cards])
    two_most_common, count = zip(*counteddict.most_common(2))

    #To account for pre-flop calculation of hand strength
    if len(count) == 1:
        templist = list(count)
        templist.append(1)
        count = tuple(templist)

    assert count != 0
    
    #NOT IN WIN ORDER(High Card,1pair,3OK,4OK,impossible,2pair,FH)
    count_to_message = {
    (1, 1): 0,
    (2, 1): 1,
    (3, 1): 3,
    (4, 1): 7,
    (5, 1): "impossible",
    (2, 2): 2,
    (3, 2): 6,
    }
    #debug steps
    #print(two_most_common)

    #Check if kicker called this function, and return the kicker(if any).
    if kicker.has_been_called:
        if count == (3,2):
            return two_most_common[1]
        elif count == (2,2):
            return min(two_most_common)

    #return value of win condition:special cases of 2 pair and full house
    if count == (2,2):
        highvalue = max(two_most_common)
        #clsHand.highcard = max(two_most_common)
    elif count == (3,2):
        highvalue = two_most_common[0]
        #clsHand.highcard = two_most_common[0]
    # elif count != (2,2) and count != (3,2):
    #     highvalue = two_most_common[0]
    else:
        highvalue = two_most_common[0]
    
    msg = count_to_message[count]

    assert msg >= 0 and msg <= 8 and msg != 4 and msg!= 5

    #For lowest win condition, High Card
    if msg == 0:
        highvalue = max(counteddict)

    return msg,highvalue

def hasSTFlush(hasStraight,hasFlush,clsHand,highStraight):
    #Returns boolean on whether Straight Flush exists.
    if hasStraight and hasFlush:
        #Check that the Flush provided HAS a straight by checking suit
        cardlist = sorted([card.value for card in clsHand.cards])
        highnum = cardlist.index(highStraight)
        lownum = highnum -4 ;assert lownum >=0
        suitset = set([clsHand.cards[i].suit for i in range(lownum,highnum)])
        assert suitset > 0
        return len(suitset) == 1
            

def hasRFlush(highcard,hasSTFlush = False):
    #Return boolean on whether Royal Flush exists.
    if hasSTFlush == True and highcard == 14:
        #print('ran')
        return True
    else:
        #print('fail')
        return False

def kicker(PlayerHand,CPUHand,strwincondition):
    #function to deal with kickers + pair issues.
    #If it is a Flush, throw a draw. Because the hands require the 5 cards to be used.
    #If it is a Straight, throw a draw. Because if the highest card is the same,
    #then everything else in the hand must be the same.(Straight Flush exists too)
    #If it is a 1 Pair, find the next highest value and compare.
    #If it is a 2 Pair, find the next highest pair and compare, then next highest value.
    #If it is 3OK/4OK, find the next highest value and compare.
    #If it is a Full House, find the highest pair value and compare.
    #Return kicker value, and who won as int.0 for player, 1 for cpu,2 for draw
    #if value is 0, that means it is a draw.
    
    WinConditionName = HandCondition(strwincondition).name
    playersorted = [card.value for card in PlayerHand.cards].sort(reverse=True)
    CPUsorted = [card.value for card in CPUHand.cards].sort(reverse=True)
    kicker.has_been_called = True

    #Returns whoever has the highest kicker of the 5 cards
    def NextHighest():
        for i in range(4):
            if playersorted[i] > CPUsorted[i]:
                return playersorted[i], 0
            elif playersorted[i] < CPUsorted[i]:
                return CPUsorted[i], 1
        #If nothing, return a Draw.
        return playersorted[0], 2
        
    
    def Kind():
        #compare the 2nd highest pair value, if draw check high cards.
        playerkicker = has2P(PlayerHand)
        cpukicker = has2P(CPUHand)
        if playerkicker > cpukicker:
            return playerkicker, 0
        elif playerkicker < cpukicker:
            return cpukicker, 1
        elif playerkicker == cpukicker:
            return NextHighest()
    
    if (WinConditionName == "Flush" or WinConditionName == "Three_Pair" or 
    WinConditionName == "Four_Of_A_Kind" or WinConditionName == ""):
        return NextHighest()
    elif WinConditionName == "Two_Pair" or WinConditionName == "Full_House":
        return Kind()
    elif WinConditionName == "Three_Pair" or WinConditionName == "Four_Of_A_Kind":
        return NextHighest()


# %%
class Deck:
    def __init__(self) -> None:
        self.allcards = []
        for suit in suits:
            for rank in ranks:
                #Create Card Obj
                created_card = Card(suit,rank)
                self.allcards.append(created_card)

    def __str__(self):
        cdoutput = ' '
        for card in self.allcards:
            temp = str(card)
            cdoutput = cdoutput + temp + "\n"
        return cdoutput

    def shuffle(self):
        random.shuffle(self.allcards) 

    def deal_onecard(self):
        return self.allcards.pop()

# %%
class Hand:
    def __init__(self):
        self.won = False
        self.cards = []
        self.highcard = 0
        self.aces = 0
        self.winpriority = 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self


    def add_card(self,card:Card):
        #Add card
        self.cards.append(card)
        if len(self.cards) > 1:
            self.highcard,self.winpriority = self.check_score()

    #Texas HOLDEM version

    def __str__(self):
        listvalue = ''
        #check the cards that hand has
        listvalue = str(self.cards[0]) + ' ' + str(self.cards[1])
        highcardstr = value_to_rank(self.highcard)
        #check the highest value of your hand
        return f'{listvalue}\nHand Value: {highcardstr}-High {HandCondition(self.winpriority).name.replace("_", " ")}'
        
    def check_score(self):
        #Return the highest value card, as well as the associated Hand Condition
        #Checking Order:
        #RF,SF,4K,FH,FL,ST,3K,2P,P,HC
        straightresult,highstraight = hasStraight(self)
        flushresult,highflush = hasFlush(self)
        straightflushresult = hasSTFlush(straightresult,flushresult,self,highstraight)
        royalflushresult = hasRFlush(highstraight,straightflushresult)
        pairresult,highpair = has2P(self)
        #return highcard, then winpriority
        if royalflushresult:
            return 14,9
        elif straightflushresult:
            return highstraight,8
        elif pairresult == 7:
            return highpair,7
        elif pairresult == 6:
            return highpair,6        
        elif flushresult:
            return highflush,5
        elif straightresult:
            return highstraight,4
        elif pairresult == 3:
            return highpair,3
        elif pairresult == 2:
            return highpair,2
        elif pairresult == 1:
            return highpair,1
        elif pairresult == 0:
            return highpair,0

# %%
class Chips:
    def __init__(self) -> None:
        self.chips = 10000
        self.bet = 0
        pass

    def __str__(self) -> str:
        return f'Balance is ${self.chips}'

    def blind(self):
        self.bet += 20
        print('Blind is bought')
        
    def bet_raise(self):
        #Input for Bet amount
        while True:
            temp = str(input('How many chips do you want to input? Input All for ALL IN\n'))
            if temp == "All" :temp = self.chips - self.bet
            try:
                self.bet += int(temp)
            except TypeError and ValueError:
                print('This is not a valid input!')
            else:
                print(f'Amount accepted: Current Bet Amount: {self.bet}')
                break
    
    def dealings(self):
        #Input for Call/Check,Betting/Raising or Folding.
        while True:
            decision = str(input('\nWhat is your next move? Input C to call/check,B to Raise your bet, or F to Fold\n'))
            if decision == 'C':
                return 'call'
            elif decision == 'B':
                return 'bet'
            elif decision == 'F':
                return "fold"
            else:
                print('Not a valid input!',end='\n')

    def won(self):
        #Print out win message, return bet
        print(f'You won the bet! Gained ${self.bet}')
        self.chips += self.bet
        self.bet = 0

    def lost(self):
        #Print out lose message, lose bet
        print(f'You lost the bet. Lost ${self.bet}')
        self.chips -= self.bet
        self.bet = 0

# %%
#Winning
def main():
    the_chips = Chips()
    gameon = True
    #win conditions in order
    winconditions = {"Royal_Flush":False,"Straight_Flush":False,"Full_House":False,"Four_Of_A_Kind":False,"Flush":False,"Straight":False,
    "Three_Of_A_Kind":False,"Two_Pair":False}
    #Initialise Deck, Hands
    while gameon:
        print('New round started...')
        kicker.has_been_called = False
        flop = True
        Playing = True
        the_deck = Deck()
        the_deck.shuffle()
        player_hand = Hand()
        cpu_hand = Hand()
        #First Draw, Blind, Show Player Hand
        the_chips.blind()
        player_hand.add_card(the_deck.deal_onecard())
        cpu_hand.add_card(the_deck.deal_onecard())
        player_hand.add_card(the_deck.deal_onecard())
        cpu_hand.add_card(the_deck.deal_onecard())
        
        print(f'Your Hand: {player_hand}')
        community_list = []
        answer = the_chips.dealings()
        if answer == 'call':
            pass
        elif answer == 'bet':
            the_chips.bet_raise()
        elif answer == 'fold':
            cpu_hand.won = True
            the_chips.lost()
            Playing = False
            flop = False


        #flop dealed
        if flop:
            communitycard1 = the_deck.deal_onecard()
            communitycard2 = the_deck.deal_onecard()
            communitycard3 = the_deck.deal_onecard()
            community_list.extend([communitycard1,communitycard2,communitycard3])
            
            player_hand.add_card(communitycard1); player_hand.add_card(communitycard2); player_hand.add_card(communitycard3)
            cpu_hand.add_card(communitycard1); cpu_hand.add_card(communitycard2); cpu_hand.add_card(communitycard3)
            print(f'Community Cards: {show_cards(community_list)}',end='\n')
            print(f'Your Hand: {player_hand}')

            answer = the_chips.dealings()
            if answer == 'call':
                pass
            elif answer == 'bet':
                the_chips.bet_raise()
            elif answer == 'fold':
                pass
                cpu_hand.won = True
                Playing = False

        #Bet/Raise, Call/Check, Fold(2nd round onwards)
        while Playing:
            a_new_card = the_deck.deal_onecard()
            community_list.append(a_new_card)
            player_hand.add_card(a_new_card)
            cpu_hand.add_card(a_new_card)
            print(f'Community Cards: {show_cards(community_list)}',end='\n')
            print(f'Your Hand: {player_hand}')
            answer = the_chips.dealings()
            if answer == 'call':
                pass
            elif answer == 'bet':
                the_chips.bet_raise()
                pass
            elif answer == 'fold':
                pass
                cpu_hand.won = True
                Playing = False
            #Check that 5 community cards have been drawn to start the showdown
            if len(community_list) == 5:
                Playing = False
        #Showdown
        if not cpu_hand.won:
            print('Showdown!')
            #COmpare win conditions(check highest value)
            if player_hand.winpriority > cpu_hand.winpriority:
                player_hand.won = True
                print('Player wins')
            elif cpu_hand.winpriority > player_hand.winpriority:
                cpu_hand.won = True
                print('CPU wins')
            #Check for highest value win condition if both win conditions are both True
            elif player_hand.winpriority == cpu_hand.winpriority:
                if player_hand.highcard > cpu_hand.highcard:
                    player_hand.won = True
                    print(f'Player wins: {player_hand.highcard}-High {HandCondition(player_hand.winpriority).name.replace("_", " ")}')
                elif player_hand.highcard < cpu_hand.highcard:
                    cpu_hand.won = True
                    print(f'CPU wins: {cpu_hand.highcard}-High {HandCondition(cpu_hand.winpriority).name.replace("_", " ")}')

                #check for kicker, won value == 0 player wins,1 cpu wins, 2 draw
                elif player_hand.highcard == cpu_hand.highcard:
                    finalkicker,won = kicker(player_hand,cpu_hand,player_hand.winpriority)
                    if won == 0:
                        player_hand.won = True
                        print(f'Player wins: {player_hand.highcard}-High {HandCondition(player_hand.winpriority).name.replace("_", " ")} + {value_to_rank(finalkicker)} Kicker')
                    elif won == 1:
                        cpu_hand.won = True
                        print(f'CPU wins: {cpu_hand.highcard}-High {HandCondition(cpu_hand.winpriority).name.replace("_", " ")} + {value_to_rank(finalkicker)} Kicker')
                    elif won == 2:
                        print(f'Draw: {cpu_hand.highcard}-High {HandCondition(cpu_hand.winpriority).name.replace("_", " ")} + {value_to_rank(finalkicker)} Kicker')
                        player_hand.won = True
                        cpu_hand.won = True

                            
        #Check who won
        if player_hand.won and cpu_hand.won:
            print(f'CPU Hand: {cpu_hand}')
            print(f'Community Cards: {show_cards(community_list)}',end='\n')
            print(f'Your Hand: {player_hand}')
            the_chips.bet = 0
        elif player_hand.won:
            print(f'CPU Hand: {cpu_hand}')
            print(f'Community Cards: {show_cards(community_list)}',end='\n')
            print(f'Your Hand: {player_hand}')
            the_chips.won()
        elif cpu_hand.won:
            print(f'CPU Hand: {cpu_hand}')
            print(f'Community Cards: {show_cards(community_list)}',end='\n')
            print(f'Your Hand: {player_hand}')
            the_chips.lost()
            pass

        #check to play again
        while True:
            playagain = input("Play again? Yes/No\n")
            if playagain == 'Yes' or playagain == 'Y':
                os.system("cls")
                break
            elif playagain == 'No' or playagain == 'N':
                gameon = False
                print('Goodbye')
                break
            else:
                print('Not a valid input')
                pass


# %%
#debug
# def test_this():
#     kicker.has_been_called = False
#     new_deck = Deck()
#     new_deck.shuffle()
#     onecard = Card("Hearts","Ten")
#     twocard = Card("Hearts","Ace")
#     threecard = Card("Hearts","Six") #com
#     fourcard = Card("Hearts","Ten") #com
#     fivecard = Card("Hearts","Five") #com
#     sixcard = Card("Hearts","Three")
#     sevencard = Card("Hearts","Ace")
    
#     mylist = [onecard,twocard,threecard,fourcard,fivecard]
#     #onecard = new_deck.deal_onecard()
#     #twocard = new_deck.deal_onecard()
#     muhhand = Hand()
#     muhhand.add_card(onecard)
#     muhhand.add_card(twocard)
#     muhhand.add_card(threecard)
#     muhhand.add_card(fourcard)
#     muhhand.add_card(fivecard)
#     opforhand = Hand()
#     #print(str(muhhand))
#     #print(f'\n{muhhand.highcard}')
#     print(show_cards(mylist))
#     print(str(muhhand))
# test_this()

# %%
main()

# %%



