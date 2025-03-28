import random


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def is_functional_card(self):
        """
            Checks if the card is a functional card.

            Returns:
                bool: True if the card is functional (e.g., '2', '3', '4', 'J', 'Q', 'K', 'A'), False otherwise.
        """
        functional_ranks = {'2', '3', '4', 'J', 'Q', 'K', 'A'}
        return self.rank in functional_ranks

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class CardDeck:
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self):
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        self.shuffle()
        print(', '.join(str(card) for card in self.cards))

    def __str__(self):
        return ', '.join(str(card) for card in self.cards)

    def draw_card(self):
        """
        Draws a card from the deck.

        :return: Card or None: The drawn card if the deck is not empty, otherwise None.
        """

        if self.cards:
            return self.cards.pop()
        else:
            return None

    def cards_left(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def create_deck_from_discard_pile(self, discard_pile):
        """
        Creates deck of cards from given discard_pile
        :param discard_pile: Cards from discard pile
        :return:
        """
        for card in discard_pile:
            self.cards.append(card)
        self.shuffle()
        return self.cards

    def first_card(self):
        return self.cards[-1]


class Player:
    id = 1
    demand = None
    change_of_suit = None
    has_to_draw = False
    has_to_wait = False
    drawn_countJ = 0
    how_many_to_draw = 0
    how_much_to_wait = 0

    def __init__(self, name):
        self.player_id = Player.id
        self.name = name
        self.hand = []
        self.is_waiting = False
        self.waiting = 0
        self.played_card = False
        self.last_card_played = None
        self.has_drawn = False
        Player.id += 1

    def show_all_non_special_cards(self):
        """
        Returns list of all non-special cards in hand
        :return: List of all non-special cards in hand
        """
        return [card for card in self.hand if not card.is_functional_card()]

    def set_how_many_to_draw(self, num):
        """
        Sets how many cards player has to draw
        :param num: Number of cards to draw
        """
        if num == 0:
            Player.how_many_to_draw = 0
        else:
            Player.how_many_to_draw += num

    def count_card_ranks(self, cards):
        rank_count = {}
        for card in cards:
            if card.rank in rank_count:
                rank_count[card.rank] += 1
            else:
                rank_count[card.rank] = 1
        return rank_count

    def order_hand(self):
        self.hand.sort(key=lambda card_to_sort: card_to_sort.rank)

    def show_playable_cards(self, current_card):
        """
        Returns all playable cards based on current card
        :param current_card: Card on to of discard pile
        :return: List of playable cards
        """
        playable_cards = []
        if current_card.rank == '2' and Player.has_to_draw:
            playable_cards = [card for card in self.hand if
                              card.rank == '2' or (card.rank == '3' and card.suit == current_card.suit)]
        elif current_card.rank == '3' and Player.has_to_draw:
            playable_cards = [card for card in self.hand if
                              card.rank == '3' or (card.rank == '2' and card.suit == current_card.suit)]
        elif current_card.rank == '4' and Player.has_to_wait:
            playable_cards = [card for card in self.hand if card.rank == '4']
        elif Player.demand is not None:
            playable_cards = [card for card in self.hand if card.rank == Player.demand]
        elif current_card.rank == 'Q':
            playable_cards = self.hand
        elif current_card.rank == 'K' and (
                current_card.suit == "Spades" or current_card.suit == "Hearts") and Player.has_to_draw:
            playable_cards = [card for card in self.hand if
                              card.rank == 'K' and (card.suit == "Spades" or card.suit == "Hearts")]
        elif current_card.rank == 'A' and Player.change_of_suit is not None:
            playable_cards = [card for card in self.hand if
                              card.rank == 'A' or card.suit == Player.change_of_suit or card.rank == 'Q']
        else:
            playable_cards = [card for card in self.hand if
                              card.suit == current_card.suit or card.rank == current_card.rank or card.rank == 'Q']
        return playable_cards

    def draw(self, deck, quantity=1):
        """
        Appends new card to player's hand
        :param deck: Deck of card from which a card will be drawn
        :param quantity: How many cards will be drawn
        :return: Drawn cards
        """
        self.has_drawn = True
        drawn_cards = []
        for _ in range(quantity):
            card = deck.draw_card()
            if card:
                self.hand.append(card)
            else:
                print("STWORZONO NOWĄ TALIĘ")
                deck = CardDeck()
                card = deck.draw_card()
                self.hand.append(card)
            drawn_cards.append(card)
        return drawn_cards

    def play_card(self, cards):
        """
        Simulates playing a card and sets appropriate parameters if played card was special
        :param cards: Cards to be played
        :return: Card that will be on top
        """
        for i in range(len(cards) - 1):
            if cards[i] in self.hand:
                self.hand.remove(cards[i])
        card = cards[-1]
        self.last_card_played = card
        if card in self.hand:
            if card.rank == 'J':
                to_demand = self.show_all_non_special_cards()
                if to_demand:
                    self.show_all_non_special_cards().sort(key=lambda card_to_sort: card.rank)
                    Player.drawn_countJ = 1
                    Player.demand = to_demand[0].rank
                    print(f"Żądam: {Player.demand}")
                    Player.has_to_draw = True
            elif card.rank == '2' or card.rank == '3' or (
                    card.rank == 'K' and (card.suit == "Hearts" or card.suit == "Spades")):
                Player.has_to_draw = True
                to_add = 5 if card.rank == 'K' else int(card.rank)
                self.set_how_many_to_draw(to_add)
            elif card.rank == 'A':
                Player.change_of_suit = self.hand[-1].suit
                print(f"Zmiana koloru na: {Player.change_of_suit}")
            elif card.rank == '4':
                Player.has_to_wait = True

            self.hand.remove(card)
            self.played_card = True
            return card
        return None

    def logic(self, deck, current_card):
        """
        Main logic of player's move. Establishes which card to play based on which card is first on discard pile.
        :param deck: Deck of cards
        :param current_card: First card on discard pile
        :return: Card to be played using given logic
        """
        self.has_drawn = False
        self.order_hand()
        print(self.show_hand())
        first_card = deck.first_card()
        if self.waiting == 0:
            playable_cards = self.show_playable_cards(current_card)
            rank_count = self.count_card_ranks(playable_cards)
            if ((current_card.rank == '2' or current_card.rank == '3' or
                 (current_card.rank == 'K' and (current_card.suit == "Spades" or current_card.suit == "Hearts")))
                    and Player.has_to_draw):
                if len(playable_cards) != 0:
                    return self.play_card([playable_cards[0]])
                if current_card.rank == '2':
                    if first_card.rank == '2' or (first_card.rank == '3' and first_card.suit == current_card.suit):
                        return self.play_card([self.draw(deck)[0]])
                if current_card.rank == '3':
                    if first_card.rank == '3' or (first_card.rank == '2' and first_card.suit == current_card.suit):
                        return self.play_card([self.draw(deck)[0]])
                if current_card.rank == 'K':
                    if first_card.rank == 'K' and (current_card.suit == "Spades" or current_card.suit == "Hearts"):
                        return self.play_card([self.draw(deck)[0]])
                if len(playable_cards) == 0:
                    Player.has_to_draw = False
                    self.draw(deck, Player.how_many_to_draw)
                    self.played_card = False
                    print(f"Dobrano {Player.how_many_to_draw}")
                    self.set_how_many_to_draw(0)
                    return current_card
            elif current_card.rank == '4' and Player.has_to_wait:
                if len(playable_cards) != 0:
                    return self.play_card([playable_cards[0]])
                else:
                    Player.has_to_wait = False
                    self.played_card = False
                    return current_card
            elif Player.demand is not None:
                Player.drawn_countJ += 1
                if Player.drawn_countJ > Player.id - 1:
                    Player.drawn_countJ = 0
                    Player.demand = None
                    Player.has_to_draw = False
                if len(playable_cards) != 0:
                    return self.play_card([playable_cards[0]])
                else:
                    self.draw(deck)
                    self.played_card = False
                    return current_card
            if len(playable_cards) != 0:
                card_to_play = playable_cards[0]
                if rank_count is not None:
                    most_common = max(rank_count, key=rank_count.get)
                    card_to_play = [c for c in playable_cards if c.rank == most_common]
                if Player.change_of_suit is not None and current_card.rank == 'A':
                    Player.change_of_suit = None
                return self.play_card(card_to_play)
            else:
                card = self.draw(deck)[0]
                if card.rank == current_card.rank or card.suit == current_card.suit:
                    return self.play_card([card])
                else:
                    self.played_card = False
                    return current_card
        else:
            self.waiting -= 1
            self.played_card = False
            return current_card

    def show_hand(self):
        return ", ".join(str(card) for card in self.hand)

    def __str__(self):
        return f"Player id: {self.player_id}, name: {self.name}"


class MainPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        self.played = False
        self.can_play = False
        self.my_turn = False

    def set_can_play(self, can):
        self.can_play = can

    def show_hand(self):
        return "Twoja ręka: " + ", ".join(str(card) for card in self.hand)

    def play_card(self, cards):
        for i in range(len(cards) - 1):
            self.hand.remove(cards[i])
        card = cards[0]
        self.hand.remove(card)
        self.played_card = True
        self.played = True
        return card

    def logic(self, deck, current_card):
        self.has_drawn = False
        self.my_turn = True
        return current_card


class MakaoGame:
    def __init__(self, players, main_player_name):
        self.deck = CardDeck()
        self.players = MakaoGame.initialize_players(players, main_player_name)
        self.discard_pile = []
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]
        self.direction = 1  # 1 oznacza zgodnie z ruchem wskazówek zegara, -1 przeciwnie

    @staticmethod
    def initialize_players(players_data, main_player_name):
        players = [Player(name) for name in players_data]
        players.append(MainPlayer(main_player_name))
        return players

    def prepare_game(self):
        """
        Prepares a game: Gives each player hand of 5 cards and prepares first card on discard pile.
        """

        # Każdy gracz dobiera na początek 5 kart
        for i in range(5):
            for player in self.players:
                player.draw(self.deck)

        # Pierwsza karta na stosie kart odrzuconych
        first_card = self.deck.draw_card()
        while first_card.is_functional_card():
            self.deck.cards.append(first_card)
            self.deck.shuffle()
            first_card = self.deck.draw_card()
        self.discard_pile.append(first_card)
        print(f"Pierwsza karta na stosie odrzuconych: {first_card}")

    def play_turn(self):
        """
        Simulates making a move by a player
        """
        current_card = self.discard_pile[-1]
        print(f"\nTura {self.current_player}. Obecna ręka: {self.current_player.show_hand()}")
        for i in self.current_player.show_playable_cards(current_card):
            print(i, end=" ")
        print()

        print(f"Current card: {current_card}")

        if self.deck.cards_left() <= Player.how_many_to_draw + 1:
            print(self.discard_pile[:-1])
            self.deck.create_deck_from_discard_pile(self.discard_pile[:-1])
            self.discard_pile = [self.discard_pile[-1]]
            print("Utworzono nową talię")
            print(f"Nowa talia: {self.deck}")
            print(f"Karta na stosie odrzuconych: {self.discard_pile[-1]}")
        current_card = self.discard_pile[-1]

        x = self.current_player.logic(self.deck, current_card)
        if x != current_card:
            self.discard_pile.append(x)

        print(f"Dodaję kartę: {x}")
        if self.current_player.played_card:
            print(f"{self.current_player.name} zagrał {x}")
        else:
            print(f"{self.current_player.name} nie mógł zagrać")

        if not self.current_player.hand:
            print(f"{self.current_player.name} wygrał!")
        if not self.deck.cards:
            self.deck = CardDeck()
