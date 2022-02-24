#imports
import random


#classes
class Card:
    def __init__(self, value, suit):
        pass
        self.value = value
        self.suit = suit

    def show(self):
        print(f"{self.value} of {self.suit}")


class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for s in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            for v in ["Ace", 2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King"]:
                self.cards.append(Card(v, s))

    def draw(self):
        return self.cards.pop()

    def show(self):
        for card in self.cards:
            card.show()

    def shuffle(self):
        for i in range(len(self.cards)-1, 0, -1):
            r = random.randint(0,i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]


class Player:
    def __init__(self, name, wallet):
        self.name = name
        self.hand = []
        self.wallet = wallet
        self.handvalue1 = 0
        self.handvalue2 = 0

    def draw(self, deck):
        self.hand.append(deck.draw())
        print(f"\n{self.name} is dealt a:", end=" ")
        self.hand[-1].show()
        self.valuehand()
        return self

    def showhand(self):
        self.valuehand()
        print(f"\n{self.name}'s hand is:\n")
        for card in self.hand:
            card.show()

        print(f"\nTotal value: {self.handvalue1}")
        if self.handvalue2 > self.handvalue1:
            print(f"Or {self.handvalue2} with Aces high")

    def showwallet(self):
        print(f"\n{self.name} has ${self.wallet}")

    # method to evaluate a self.hand and assign a numerical value.
    # 2 hand values exist to account for ace's being high or low.
    def valuehand(self):
        handvalue1 = 0
        handvalue2 = 0
        aces = 0
        face = ["Jack", "Queen", "King"]
        for card in self.hand:
            if card.value == "Ace":
                handvalue1 += 1
                aces += 1
            elif card.value in face:
                handvalue1 += 10
            else:
                handvalue1 += card.value
        handvalue2 = handvalue1 + aces * 10
        self.handvalue1 = handvalue1
        self.handvalue2 = handvalue2


class Blackjack:
    def __init__(self, player):
        self.player = player
        self.dealer = Player("The Dealer", 1000000)
        # an extra player class allows a split hand to be played separately.
        self.splithand = Player("Split Hand", 0)
        self.deck = Deck()
        self.bet = 0
        # used to indicate a double down bet has been selected
        self.dd = False

    # sets bet vraible to user input bet that must be <= player wallet.
    def betting(self):
        self.spacer("Place your bets!")
        self.dealer.showwallet()
        self.player.showwallet()
        print("\nEnter a value between $10 and $1000.")
        choice = self.get_input("> ", [n for n in range(10,1001)])
        while choice > self.player.wallet:
            print("You cant afford that bet try a smaller amount.")
            choice = self.get_input("> ", [n for n in range(10,1001)])
        self.bet = choice

    # prints message that player is bust and shows hand.
    def bust(self, player):
        self.spacer(f"{player.name}'s hand is Bust!")
        player.showhand

    # checks a players hand for blackjack.
    def checkbj(self, player):
        if player.handvalue2 == 21:
            self.spacer(f"{player.name}'s hand is a natural blackjack!")
            player.showhand()
            return True
        else:
            return False

    # checks new hands for natural blackjack before play begins.
    def checknat(self):
        # check for player natural Blackjack
        playerbj = self.checkbj(self.player)
        # add hole card to dealer hand
        self.dealer.hand.append(self.deck.draw())
        self.dealer.valuehand()
        # check for dealer blackjack
        dealerbj = self.checkbj(self.dealer)

        # compare results of blackjack checks and resolves round if required.
        if playerbj and dealerbj:
            self.spacer("Its a draw, both hands are a blackjack!")
            print("All bets are returned!")
        elif playerbj:
            self.spacer(f"Congratulations {self.player.name} you win this hand!")
            self.pay(1.5)
        elif dealerbj:
            self.spacer(f"Bad luck, {self.dealer.name} wins this hand!")
            self.pay(-1)

        if playerbj or dealerbj:
            self.endround()

    # double down option, double bet, draw a card.
    def ddown(self):
        # indicate double down option has been taken
        self.dd = True
        self.player.draw(self.deck)
        self.player.showhand()

    # clears hands, creates new deck, adds cards to hands.
    def deal(self):
        self.spacer("Cards dealt.")
        # create new deck and shuffle it each round
        self.deck = Deck()
        self.deck.shuffle()
        # clear hands at beginning of each round
        self.player.hand.clear()
        self.splithand.hand.clear()
        self.dealer.hand.clear()
        # clear the doubledown status
        self.dd = False
        # deal 2 cards to player and dealer hands
        self.player.draw(self.deck)
        self.dealer.draw(self.deck)
        self.player.draw(self.deck)
        # print hands to screen
        self.player.showhand()
        self.dealer.showhand()

    # plays dealer hand automatically, hits on 16 or less.
    def dealerplay(self):
        #if player and/or splithand have bust, skip dealer turn
        if self.splithand.hand == []:
            if self.player.handvalue1 > 21:
                return self
        elif self.player.handvalue1 > 21 and self.splithand.handvalue1 > 21:
            return self

        self.spacer(f"{self.dealer.name}'s turn.")
        self.dealer.showhand()

        # dealer must stand if ace high results in hand value of 17 or greater.
        if self.dealer.handvalue2 >= 17:
            print(f"\n{self.dealer.name} stands!")
            self.dealer.showhand()
            return self

        # dealer will hit until bust or 17.
        while self.dealer.handvalue1 < 22:
            if self.dealer.handvalue1 < 17:
                print(f"\n{self.dealer.name} hits!")
                self.dealer.draw(self.deck)
            else:
                print(f"\n{self.dealer.name} stands!")
                self.dealer.showhand()
                return self
        self.bust(self.dealer)

    # end round, ask if player wants continue, checks player has money left.
    def endround(self):
        self.spacer("End of round!")

        # check for player.wallet = 0
        if self.player.wallet < 10:
            self.spacer(f"Your broke {self.player.name}, come again soon !")
            quit()

        # option to continue, quit or continue with same bet.
        print("Do you want to play another round? (y/n)")
        print(f"You can play again with the same (${self.bet}) bet? (r) ")
        choice = self.get_input("> ", ["y","n","r"])
        if choice == "y":
            self.newbetround()
        elif choice == "r":
            self.newround()
        else:
            quit()

    # takes prompt and list of valid choices, will only return a valid choice
    def get_input(self, prompt, choices=None):
        correct = False

        while not correct:
            choice = input(prompt)
            if choice == "quit":
                exit()
            if choices == None:
                return choice
            try:
                choice = int(choice)
                if choice in choices:
                    return choice
                else:
                    print("\nInvalid entry, try again.\n")
                    continue
            except:
                pass

            try:
                choice = choice.lower()
                if choice in choices:
                    return choice
                else:
                    pass
                    print("\nInvalid entry, try again.\n")
            except:
                pass

    # new round with new bet value
    def newbetround(self):
        self.spacer("New round.")
        self.betting()
        self.deal()
        self.checknat()
        self.playerplay()
        self.dealerplay()
        # if split occured, resolve split hand before player hand.
        if self.splithand.hand != []:
            self.resolveround(self.splithand)
        self.resolveround(self.player)
        self.endround()

    # new round with existing bet value.
    def newround(self):
        self.spacer("New round.")
        self.deal()
        self.checknat()
        self.playerplay()
        self.dealerplay()
        # if split occured, resolve split hand before player hand.
        if self.splithand.hand != []:
            self.resolveround(self.splithand)
        self.resolveround(self.player)
        self.endround()

    # method takes +/- value to multiply the existing bet by and add it to
    # player wallet while subtracting from dealer wallet.
    def pay(self, factor):
        value = (self.bet * factor)
        # in event of double down option in play, bet value is doubled
        if self.dd:
            value *= 2
        self.player.wallet += value
        self.dealer.wallet -= value

        if value >= 0:
            print(f"{self.player.name} gains ${value}")
        else:
            print(f"{self.player.name} loses ${value * -1}")
        self.dealer.showwallet()
        self.player.showwallet()

    # begins game and newbetround
    def play(self):
        self.spacer("Lets play Blackjack!")
        print("!type quit to exit game at any time!")
        self.newbetround()

    # allows player to play hand, with options for stand, hit, split, doubledown
    # will go bust if hand value exceeds 21.
    def playerplay(self):
        choices = [1, 2]
        self.spacer(f"{self.player.name}'s turn.")

        # loop allows play until hand goes bust or otherwise resolved.
        while self.player.handvalue1 < 22:
            self.player.showhand()
            print("\nPick an option:\n1) Stand.\n2) Hit.")

            # necessary to only allow split, ddown on initial cards
            if len(self.player.hand) < 3:
                # check for conditions for split
                if self.player.hand[0].value == self.player.hand[1].value:
                    print("3) Split.")
                    choices.append(3)

                list = [9, 10, 11]
                # check for conditions for doubledown
                if self.player.handvalue1 in list:
                    print("4) Double down.")
                    choices.append(4)

            choice = self.get_input("> ", choices)

            if choice == 1:
                return self
            elif choice == 2:
                self.player.draw(self.deck)
            elif choice == 3:
                self.split()
                return self
            else:
                self.ddown()
                return self

        self.bust(self.player)

    # returns highest hand value less than 22.
    def resolvehand(self, player):
        v1, v2 = player.handvalue1, player.handvalue2

        if v2 > v1 and v2 < 22:
            return v2
        else:
            return v1

    # compares player and dealer hand value, determines winner, pays accordingly
    # displays info to player.
    def resolveround(self, player):
        # get best hand value from player and dealer
        p = self.resolvehand(player)
        d = self.resolvehand(self.dealer)

        # if both values less than 22 (not bust), resolve win/lose
        if p < 22 and d < 22:
            self.spacer(f"{player.name} hand value: {p} vs {self.dealer.name} hand value: {d}")
            if p > d:
                self.spacer(f"{player.name} wins!")
                self.pay(1)
            elif p == d:
                self.spacer(f"{player.name} and {self.dealer.name} draw!")
                print("Your bets are returned!")
            elif p < d:
                self.spacer(f"{player.name} loses to {self.dealer.name}!")
                self.pay(-1)
        else:
            #resolve bets for bust hands, ending method if player is bust first
            if p > 21:
                if self.splithand.hand != []:
                    self.bust(player)
                self.pay(-1)
                return self
            elif d > 21:
                if self.splithand.hand != []:
                    self.spacer(f"{player.name} wins!")
                    self.bust(self.dealer)
                self.pay(1)
                return self

    # displays string with rows of $'s above and below.
    def spacer(self, text):
        main = f"\n$$$    {text}    $$$\n"
        outer = "$" * (len(main)-2)
        print(f"\n{outer}\n{main}\n{outer}\n")

    # splits player.hand with splithand.hand and draws card for each then
    # begins splitplay for each.
    def split(self):
        # split player.hand with splithand.hand
        self.splithand.hand.append(self.player.hand.pop())
        # deal both a card
        self.splithand.draw(self.deck)
        self.player.draw(self.deck)
        # begin splitplay for both
        self.splitplay(self.splithand)
        self.splitplay(self.player)

    # allows hand to be played without split or ddown options.
    def splitplay(self, player):
        choices = [1, 2]
        self.spacer(f"{player.name}'s turn.")
        while player.handvalue1 < 22:
            player.showhand()
            print("\nPick an option:\n1) Stand.\n2) Hit.")
            choice = self.get_input("> ", choices)
            if choice == 1:
                return self
            elif choice == 2:
                player.draw(self.deck)
        self.bust(player)


#testing
player = Player("Arnold", 1000)
blackjack = Blackjack(player)
blackjack.play()
