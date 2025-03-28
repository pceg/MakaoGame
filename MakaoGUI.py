import threading
import time
import tkinter.simpledialog as simpledialog
import tkinter as tk
from tkinter import messagebox

from gui import DemandDialog, SuitChangeDialog
from game import Player, MakaoGame, MainPlayer


class MakaoGUI:
    def __init__(self, root, game):
        """
            Initialize the MakaoGUI instance.

            :param root: The root Tkinter window.
            :param game: The MakaoGame instance.
        """

        self.root = root
        self.root.title("Makao Game")
        self.game = game
        self.current_player = self.game.current_player
        self.main_player = self.game.players[-1]

        self.card_images = self.load_card_images()

        window_width = 1000
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 6
        y = (screen_height - window_height) // 6
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame for current card
        self.current_card_frame = tk.Frame(self.root)
        self.current_card_label = tk.Label(self.current_card_frame, text="", font=("Arial", 20))
        self.current_card_label.pack()

        self.players_frame = tk.Frame(self.root)
        self.players_frame.pack(side="top", pady=20)

        self.player_panels = []
        for player in self.game.players[:-1]:
            self.create_player_panel(self.players_frame)

        self.current_card_frame.pack(pady=20)

        # Frame for main player's hand
        self.main_player_frame = tk.Frame(self.root)
        self.main_player_frame.pack(pady=20)

        # Label for displaying player's information
        self.player_info_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.player_info_label.pack(pady=10)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Tworzenie przycisków wewnątrz ramki
        self.draw_button = tk.Button(self.bottom_frame, text="Draw Card", command=self.draw_card)
        self.draw_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 5), pady=10)

        self.end_turn_button = tk.Button(self.bottom_frame, text="End Turn", command=self.end_turn)
        self.end_turn_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 10), pady=10)

        self.show_board()
        messagebox.showinfo("Welcome to the game", "Welcome in the game Makao! Start a game")

        time.sleep(1)
        self.update_display()

    def create_player_panel(self, parent):
        """
            Create a panel for a player.

            :param parent: The parent frame.
        """
        frame = tk.Frame(parent, relief=tk.RIDGE, borderwidth=2)
        frame.pack(side="left", padx=10)
        label = tk.Label(frame, text="", font=("Arial", 12))
        label.pack()
        self.player_panels.append((frame, label))

    def update_player_panels(self):
        """
            Update the player panels with the current game state.
        """
        for idx, player in enumerate(self.game.players[:-1]):
            if idx < len(self.player_panels):
                frame, label = self.player_panels[idx]
                label.config(text=self.player_information(player))
        self.player_info_label.config(text=self.player_information(self.main_player))

    def player_information(self, player):
        player_info = f"Name: {player.name}\n"
        player_info += f"Number of cards: {len(player.hand)}\n"
        if player.played_card:
            player_info += f"Played card: {player.last_card_played}\n"
        if not player.played_card:
            player_info += f"Couldn't play\n"
        if player.has_drawn and self.current_player == player:
            player_info += f"Has drawn card(s)\n"
        if player.is_waiting:
            player_info += f"Blocked\n"
        if Player.demand:
            player_info += f"Demanding: {Player.demand}\n"
        if Player.change_of_suit:
            player_info += f"Changed suit to: {Player.change_of_suit}\n"
        if player == self.main_player and self.main_player.my_turn:
            player_info = "Your turn!\n" + player_info
        return player_info

    def update_display(self):
        """
            Update the display with the current game state.
        """
        self.show_board()
        self.current_player = self.game.current_player
        current_card = self.game.discard_pile[-1]

        card_image = self.get_card_image(current_card)

        if card_image:
            self.current_card_label.config(text=f"Current card: {current_card}", font=("Arial", 12))
            resized_image = card_image.subsample(3)
            self.current_card_label.config(image=resized_image, compound="top", padx=10, pady=10)
            self.current_card_label.image = resized_image
        else:
            self.current_card_label.config(text=f"Current card: {current_card}")

        if isinstance(self.current_player, MainPlayer):
            messagebox.showinfo("Information", "Your turn")
            self.game.play_turn()
            res = self.main_player_logic(current_card)
            if not res:
                self.current_player.can_play = False
                messagebox.showwarning("Info", "There are no playable cards.")
                self.show_board()
            else:
                self.current_player.can_play = True
                self.show_board()
                self.current_player.played_card = True
        else:
            threading.Thread(target=self.wait_for_players_move).start()

    def show_board(self):
        """
        Update the game board display with the current state of the main player's hand.
        """
        for widget in self.main_player_frame.winfo_children():
            widget.destroy()

        main_player = self.game.players[-1]
        current_card = self.game.discard_pile[-1]

        max_cards_per_row = 10  # Maksymalna liczba kart w jednym wierszu
        row = 0
        col = 0

        for idx, card in enumerate(main_player.hand):
            if col >= max_cards_per_row:
                row += 1
                col = 0
            if main_player.my_turn:
                if main_player.can_play:
                    if card in main_player.show_playable_cards(current_card):
                        btn = tk.Button(self.main_player_frame, text=str(card),
                                        command=lambda c=card: self.play_card(c))
                    else:
                        btn = tk.Button(self.main_player_frame, text=str(card), state="disabled")
                    if current_card.rank != '4':
                        self.draw_button.config(state='normal')
                    else:
                        self.draw_button.config(state='disabled')
                else:
                    btn = tk.Button(self.main_player_frame, text=str(card), state="active")
                    if main_player.is_waiting or main_player.has_drawn:
                        self.draw_button.config(state='disabled')
                        self.end_turn_button.config(state='normal')
                    else:
                        self.draw_button.config(state='normal')
                        self.end_turn_button.config(state='disabled')
            else:
                btn = tk.Button(self.main_player_frame,
                                text=str(card), state="active",
                                bg="SystemButtonFace",
                                highlightbackground="SystemButtonFace")
                btn.grid(row=row, column=col, padx=5)

                self.end_turn_button.config(state='disabled')
                self.draw_button.config(state='disabled')

            card_image = self.get_card_image(card)
            if card_image:
                resized_image = card_image.subsample(4)
                btn.config(image=resized_image, compound="top", width=75,
                           height=90)
                btn.image = resized_image
            btn.grid(row=row, column=col, padx=5)

            col += 1

        self.update_player_panels()

    def play_game(self):
        """
        Proceeds to the next turn in the game and updates the display accordingly.
        """
        current_player_index = self.game.players.index(self.game.current_player)
        next_player_index = (current_player_index + 1) % len(self.game.players)
        self.game.current_player = self.game.players[next_player_index]
        self.update_display()

    def wait_for_players_move(self):
        """
            Computer-player's move.
        """
        self.game.play_turn()
        if len(self.game.current_player.hand) == 1:
            messagebox.showinfo("Makao", f":o {self.game.current_player.name} says: MAKAO!")
        if not self.game.current_player.hand:
            messagebox.showinfo("Po Makale", f"{self.game.current_player.name} wins!")
            self.root.quit()
        else:
            self.show_board()
            time.sleep(2)
            self.play_game()

    def main_player_logic(self, current_card):
        """
            Define the main player's logic for playing a card.

            :param current_card: The current card on the discard pile.
            :return: True if a player can play a card, False otherwise.
        """
        mplayer = self.game.current_player
        mplayer.is_waiting = False
        self.main_player.has_drawn = False
        first_card = self.game.deck.first_card()
        if mplayer.waiting == 0:
            mplayer.show_hand()
            playable_cards = mplayer.show_playable_cards(current_card)
            if ((current_card.rank == '2' or current_card.rank == '3' or
                 (current_card.rank == 'K' and (current_card.suit == "Spades" or current_card.suit == "Hearts")))
                    and Player.has_to_draw):
                if len(playable_cards) != 0:
                    messagebox.showinfo("Information", "Możesz się ruszyć")
                    return True
                if current_card.rank == '2':
                    if first_card.rank == '2' or (first_card.rank == '3' and first_card.suit == current_card.suit):
                        messagebox.showinfo("Information", "Dobieram 1")
                        ca = mplayer.draw(self.game.deck)[0]
                        return True
                if current_card.rank == '3':
                    if first_card.rank == '3' or (first_card.rank == '2' and first_card.suit == current_card.suit):
                        messagebox.showinfo("Information", "Dobieram 1")
                        ca = mplayer.draw(self.game.deck)[0]
                        return True
                if current_card.rank == 'K':
                    if first_card.rank == 'K' and (current_card.suit == "Spades" or current_card.suit == "Hearts"):
                        messagebox.showinfo("Information", "Możesz się ruszyć")
                        ca = mplayer.draw(self.game.deck)[0]
                        return True
                if len(playable_cards) == 0:
                    Player.has_to_draw = False
                    mplayer.played_card = False
                    mplayer.draw(self.game.deck, Player.how_many_to_draw)
                    messagebox.showinfo("Information", f"Dobrano {Player.how_many_to_draw}")
                    mplayer.set_how_many_to_draw(0)
                    return False
            elif current_card.rank == '4' and Player.has_to_wait:
                if len(playable_cards) != 0:
                    return True
                else:
                    messagebox.showinfo("Information", "Jesteś zablokowany")
                    Player.has_to_wait = False
                    mplayer.played_card = False
                    mplayer.is_waiting = True
                    return False
            elif Player.demand is not None:
                Player.drawn_countJ += 1
                if Player.drawn_countJ > Player.id - 1:
                    Player.drawn_countJ = 0
                    Player.demand = None
                    Player.has_to_draw = False

                if len(playable_cards) != 0:
                    return True
                else:
                    mplayer.played_card = False
                    return False

            if len(playable_cards) != 0:
                return True
            else:
                card = self.game.deck.first_card()
                if card.rank == current_card.rank or card.suit == current_card.suit:
                    messagebox.showinfo("Information", "Możesz się ruszyć")
                    ca = mplayer.draw(self.game.deck)[0]
                    return True
                else:
                    mplayer.played_card = False
                    return False
        else:
            mplayer.waiting -= 1
            mplayer.played_card = False
            return False

    def play_card(self, card):
        """
        Handles the playing of a card by the main player.
        :param card: The card to be played by the main player.
        """
        main_player = self.game.players[-1]
        current_card = self.game.discard_pile[-1]
        played_card = main_player.play_card([card])
        if played_card:
            if card.rank != 'A' and Player.change_of_suit is not None:
                Player.change_of_suit = None
            self.game.discard_pile.append(played_card)
            main_player.last_card_played = played_card
            messagebox.showinfo("Played", f"Played {played_card}")
            self.show_board()
            self.handle_special_cards(played_card)
            if len(main_player.hand) == 1:
                messagebox.showinfo("Makao", f":o {main_player.name} says: Makao")
            elif not main_player.hand:
                messagebox.showinfo("Po Makale!", f"{main_player.name} wins!")
                self.root.quit()
            else:
                self.play_game()
                self.show_board()
        else:
            messagebox.showwarning("Invalid Move", "You can't play that card.")
        main_player.my_turn = False

    def handle_special_cards(self, card):
        """
        Handles special actions triggered by playing certain cards.
        :param card: The card played by the main player.
        """
        if card.rank == 'J':
            dialog = DemandDialog(self.root)
            self.root.wait_window(dialog)
            if Player.demand:
                Player.drawn_countJ = 0
                Player.has_to_draw = True
        elif card.rank == '2' or card.rank == '3' or (
                card.rank == 'K' and (card.suit == "Hearts" or card.suit == "Spades")):
            Player.has_to_draw = True
            to_add = 5 if card.rank == 'K' else int(card.rank)
            self.game.players[-1].set_how_many_to_draw(to_add)
        elif card.rank == 'A':
            dialog = SuitChangeDialog(self.root)
            self.root.wait_window(dialog)
        elif card.rank == '4':
            Player.has_to_wait = True

    def end_turn(self):
        """
            End the current player's turn (main player)
        """
        if isinstance(self.game.current_player, MainPlayer):
            if (self.game.current_player.played_card or
                    self.game.current_player.is_waiting or
                    self.game.current_player.has_drawn):
                self.play_game()
            else:
                self.draw_card()

    def draw_card(self):
        """
            Draw a card from the deck.
        """
        self.game.current_player.played_card = False
        main_player = self.game.players[-1]
        drawn_cards = main_player.draw(self.game.deck)
        if not drawn_cards:
            messagebox.showinfo("Info", "The deck is empty!")
        self.show_board()
        self.game.play_turn()
        self.play_game()
        main_player.my_turn = False
        main_player.has_drawn = True

    def load_card_images(self):
        """
            Load card images from the filesystem.

            :return: A dictionary mapping card names to Tkinter PhotoImage objects.
        """
        suits = {'Spades': 'p', 'Diamonds': 'd', 'Hearts': 's', 'Clubs': 't'}
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'j', 'q', 'k', 'a']
        card_images = {}
        for suit in suits.values():
            for rank in ranks:
                card_name = f"{suit}{rank}"
                image_path = f"cards/{card_name}.png"
                try:
                    image = tk.PhotoImage(file=image_path)
                    card_images[card_name] = image
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
        return card_images

    def get_card_image(self, card):
        """
            Get the image for a given card.

            :param card: The card object.
            :return: The PhotoImage object for the card.
        """
        suit_map = {'Spades': 'p', 'Diamonds': 'd', 'Hearts': 's', 'Clubs': 't'}
        card_name = f"{suit_map[card.suit]}{card.rank.lower()}"
        return self.card_images.get(card_name)


def show_instructions(root):
    instruction_window = tk.Toplevel(root)
    instruction_window.title("Instructions")

    with open("instructions", "r", encoding="utf-8") as file:
        instructions = file.read()

    instruction_label = tk.Label(instruction_window, text=instructions, padx=10, pady=10)
    instruction_label.pack()

    understand_button = tk.Button(instruction_window, text="Zagrajmy!", command=instruction_window.destroy)
    understand_button.pack(pady=10)

    instruction_window.transient(root)
    instruction_window.grab_set()
    root.wait_window(instruction_window)

def start_game():
    root = tk.Tk()
    show_instructions(root)
    root.destroy()

    player_names = ["Jess", "Nick", "Daniel"]

    num_players = simpledialog.askinteger("Number of Players", "Enter number of players (1-3):", minvalue=1, maxvalue=3)

    main_player_name = ""
    while not main_player_name:
        main_player_name = simpledialog.askstring("Main player name config", "Enter your name: ")
        if not main_player_name:
            messagebox.showwarning("Input Required", "You must enter your name to proceed.")

    game = MakaoGame(player_names[:num_players], main_player_name)
    game.prepare_game()
    root = tk.Tk()
    gui = MakaoGUI(root, game)
    root.mainloop()


if __name__ == "__main__":
    start_game()
