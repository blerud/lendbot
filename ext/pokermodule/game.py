from collections import namedtuple
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List

import discord
import random

from ext.pokermodule.player import Player
from ext.pokermodule.rules import best_possible_hand, Card, Deck
from ext.pokermodule.pot import PotManager

EmbedTitle = namedtuple("EmbedTitle", ["title"])
EmbedDescription = namedtuple("EmbedDescription", ["description"])
EmbedField = namedtuple("EmbedField", ["name", "value", "inline"])
EmbedFooter = namedtuple("EmbedFooter", ["text"])

Option = namedtuple("Option", ["description", "default"])

GAME_OPTIONS: Dict[str, Option] = {
    "blind":  Option("The current price of the small blind", 100),
    "buy-in": Option("The amount of money all players start out with", 10000),
    "raise-delay": Option("The number of minutes before blinds double",  0),
    "starting-blind": Option("The starting price of the small blind", 100),
    "auto-deal": Option("Automatically deal cards after a round", 1),
    "tournament": Option("Tournament mode (no buy-ins during the game)", 0)
}

# An enumeration that says what stage of the game we've reached
class GameState(Enum):
    # Game hasn't started yet
    NO_GAME = 1
    # A game has started, and we're waiting for players to join
    WAITING = 2
    # Everyone's joined, we're waiting for the hands to be dealt
    NO_HANDS = 3
    # We've dealt hands to everyone, they're making their bets
    HANDS_DEALT = 4
    # We've just dealt the flop
    FLOP_DEALT = 5
    # We just dealt the turn
    TURN_DEALT = 6
    # We just dealt the river
    RIVER_DEALT = 7

# A class that keeps track of all the information having to do with a game
class Game:
    def __init__(self) -> None:
        self.new_game()
        # Set the game options to the defaults
        self.options = {key: value.default
                        for key, value in GAME_OPTIONS.items()}

    def new_game(self) -> None:
        self.state = GameState.NO_GAME
        # The players participating in the game
        self.players: List[Player] = []
        # The players participating in the current hand
        self.in_hand: List[Player] = []
        # The index of the current dealer
        self.dealer_index = 0
        # The index of the first person to bet in the post-flop rounds
        self.first_bettor = 0
        # The deck that we're dealing from
        self.cur_deck: Deck = None
        # The five cards shared by all players
        self.shared_cards: List[Card] = []
        # Used to keep track of the current value of the pot, and who's in it
        self.pot = PotManager()
        # The index of the player in in_hand whose turn it is
        self.turn_index = -1
        # The last time that the blinds were automatically raised
        self.last_raise: datetime = None

    # Adds a new player to the game, returning if they weren't already playing
    def add_player(self, user: discord.User) -> bool:
        if self.is_player(user):
            return False
        player = Player(user)
        player.balance = self.options["buy-in"]
        self.players.append(player)
        return True

    # Returns whether a user is playing in the game
    def is_player(self, user: discord.User) -> bool:
        for player in self.players:
            if player.user == user:
                return True
        return False

    # Removes a player from being able to bet, if they folded or went all in
    def leave_hand(self, to_remove: Player) -> None:
        for i, player in enumerate(self.in_hand):
            if player == to_remove:
                index = i
                break
        else:
            # The player who we're removing isn't in the hand, so just
            # return
            return

        self.in_hand.pop(index)

        # Adjust the index of the first person to bet and the index of the
        # current player, depending on the index of the player who just folded
        if index < self.first_bettor:
            self.first_bettor -= 1
        if self.first_bettor >= len(self.in_hand):
            self.first_bettor = 0
        if self.turn_index >= len(self.in_hand):
            self.turn_index = 0

    # Returns some messages to update the players on the state of the game
    def status_between_rounds(self) -> List[object]:
        messages = []
        if not self.options["auto-deal"]:
            messages.append(EmbedFooter("Message .p deal to deal."))
        # Print chip count
        for player in self.players:
            name = player.user.name
            if player == self.dealer:
                name = f"__{name}__"
            if player == self.current_player:
                name = f"**{name}**"
            messages.append(EmbedField(name, f"${player.balance}", True))
        return messages

    # Moves on to the next dealer
    def next_dealer(self) -> None:
        self.dealer_index = (self.dealer_index + 1) % len(self.players)

    # Returns the current dealer
    @property
    def dealer(self) -> Player:
        return self.players[self.dealer_index]

    @property
    def cur_bet(self) -> int:
        return self.pot.cur_bet

    # Returns the player who is next to move
    @property
    def current_player(self) -> Player:
        return self.in_hand[self.turn_index]

    # Starts a new game, returning the messages to tell the channel
    def start(self) -> List[str]:
        self.state = GameState.NO_HANDS
        self.dealer_index = random.randint(0, len(self.players) - 1)
        # Reset the blind to be the starting blind value
        self.options["blind"] = self.options["starting-blind"]
        if self.options["auto-deal"]:
            return [EmbedTitle("The game has begun!")]
        else:
            return [EmbedTitle("The game has begun!")] + self.status_between_rounds()

    # Starts a new round of Hold'em, dealing two cards to each player, and
    # return the messages to tell the channel
    def deal_hands(self) -> List[str]:
        # Shuffles a new deck of cards
        self.cur_deck = Deck()

        # Start out the shared cards as being empty
        self.shared_cards = []

        # Deals hands to each player, setting their initial bets to zero and
        # adding them as being in on the hand
        self.in_hand = []
        for player in self.players:
            player.cards = (self.cur_deck.draw(), self.cur_deck.draw())
            player.cur_bet = 0
            player.placed_bet = False
            self.in_hand.append(player)

        self.state = GameState.HANDS_DEALT
        messages = [EmbedTitle("The hands have been dealt!")]

        # Reset the pot for the new hand
        self.pot.new_hand(self.players)

        if self.options["blind"] > 0:
            messages += self.pay_blinds()

        self.turn_index -= 1
        return messages + self.next_turn()

    # Makes the blinds players pay up with their initial bets
    def pay_blinds(self) -> List[object]:
        messages: List[object] = []

        # See if we need to raise the blinds or not
        raise_delay = self.options["raise-delay"]
        if raise_delay == 0:
            # If the raise delay is set to zero, consider it as being turned
            # off, and do nothing for blinds raises
            self.last_raise = None
        elif self.last_raise is None:
            # Start the timer, if it hasn't been started yet
            self.last_raise = datetime.now()
        elif datetime.now() - self.last_raise > timedelta(minutes=raise_delay):
            messages.append(EmbedField("**Blinds are being doubled this round!**", u"\u200B", False))
            self.options["blind"] *= 2
            self.last_raise = datetime.now()

        blind = self.options["blind"]

        # Figure out the players that need to pay the blinds
        if len(self.players) > 2:
            small_player = self.players[(self.dealer_index + 1) % len(self.in_hand)]
            big_player = self.players[(self.dealer_index + 2) % len(self.in_hand)]
            # The first player to bet pre-flop is the player to the left of the big blind
            self.turn_index = (self.dealer_index + 3) % len(self.in_hand)
            # The first player to bet post-flop is the first player to the left of the dealer
            self.first_bettor = (self.dealer_index + 1) % len(self.players)
        else:
            # In heads-up games, who plays the blinds is different, with the
            # dealer playing the small blind and the other player paying the big
            small_player = self.players[self.dealer_index]
            big_player = self.players[self.dealer_index - 1]
            # Dealer goes first pre-flop, the other player goes first afterwards
            self.turn_index = self.dealer_index
            self.first_bettor = self.dealer_index - 1

        if self.pot.pay_blind(small_player, blind):
            self.leave_hand(small_player)

        if self.pot.pay_blind(big_player, blind * 2):
            self.leave_hand(big_player)

        return messages

    # Returns messages telling the current player their options
    def cur_options(self) -> List[object]:
        messages = [self.current_player.user.mention,
                    EmbedTitle(f"It is {self.current_player.user.name}'s turn."),
                    EmbedDescription(f"Pot: ${self.pot.value} | Current bet: ${self.pot.cur_bet}")]

        # Print chip count
        for player in self.players:
            name = player.user.name
            if player == self.dealer:
                name = f"_{name}_"
            if player == self.current_player:
                name = f"**{name}**"
            if player.cur_bet > 0:
                name += f": ${player.cur_bet}"
            if player not in self.pot.pots[0].players:
                name = f"~~{name}~~"

            value = f"${player.balance}"
            if player.balance == 0:
                value += " (All-in!)"
            messages.append(EmbedField(name, value, True))

        if self.current_player.cur_bet == self.cur_bet:
            messages.append(EmbedFooter("Message .p check, .p raise or .p fold."))
        elif self.current_player.max_bet > self.cur_bet:
            messages.append(EmbedFooter("Message .p call, .p raise or .p fold."))
        else:
            messages.append(EmbedFooter("Message .p allin or .p fold."))
        return messages

    # Advances to the next round of betting (or to the showdown), returning a
    # list messages to tell the players
    def next_round(self) -> List[object]:
        messages: List[object] = []
        name = ""
        if self.state == GameState.HANDS_DEALT:
            name = "Dealing the flop:"
            self.shared_cards.append(self.cur_deck.draw())
            self.shared_cards.append(self.cur_deck.draw())
            self.shared_cards.append(self.cur_deck.draw())
            self.state = GameState.FLOP_DEALT
        elif self.state == GameState.FLOP_DEALT:
            name = "Dealing the turn:"
            self.shared_cards.append(self.cur_deck.draw())
            self.state = GameState.TURN_DEALT
        elif self.state == GameState.TURN_DEALT:
            name = "Dealing the river:"
            self.shared_cards.append(self.cur_deck.draw())
            self.state = GameState.RIVER_DEALT
        elif self.state == GameState.RIVER_DEALT:
            return self.showdown()
        value = "  ".join(str(card) for card in self.shared_cards)

        messages.append(EmbedField(name, value, False))
        self.pot.next_round()
        self.turn_index = self.first_bettor
        return messages + self.cur_options()

    # Finish a player's turn, advancing to either the next player who needs to
    # bet, the next round of betting, or to the showdown
    def next_turn(self) -> List[str]:
        if self.pot.round_over():
            if self.pot.betting_over():
                return self.showdown()
            else:
                return self.next_round()
        else:
            self.turn_index = (self.turn_index + 1) % len(self.in_hand)
            return self.cur_options()

    def showdown(self) -> List[str]:
        while len(self.shared_cards) < 5:
            self.shared_cards.append(self.cur_deck.draw())

        messages = [EmbedField("Betting has concluded. Dealing and revealing the remaining cards:",
            "  ".join(str(card) for card in self.shared_cards), False)]

        winners = self.pot.get_winners(self.shared_cards)

        for winner, winnings in sorted(winners.items(), key=lambda item: item[1]):
            winner.balance += winnings

        for player in self.pot.in_pot():
            hand_name = str(best_possible_hand(self.shared_cards, player.cards))

            if player in winners:
                name = f"**{player.user.name}:** ${player.balance} (+${winners[player]})"
                value = f"{player.cards[0]}  {player.cards[1]}  **({hand_name})**"
            elif player.balance == 0:
                name = f"~~{player.user.name}~~: ${player.balance}"
            else:
                name = f"{player.user.name}: ${player.balance}"

            messages.append(EmbedField(name, value, True))

        # Remove players that went all in and lost
        i = 0
        while i < len(self.players):
            player = self.players[i]
            if player.balance > 0:
                i += 1
            else:
                self.players.pop(i)
                if len(self.players) == 1:
                    # There's only one player, so they win
                    messages.append(EmbedField(f":tada:{self.players[0].user.name} wins the game!", "Congratulations!", False))
                    self.state = GameState.NO_GAME
                    return messages
                if i <= self.dealer_index:
                    self.dealer_index -= 1

        # Go on to the next round
        self.state = GameState.NO_HANDS
        self.next_dealer()
        if not self.options["auto-deal"]:
            messages += self.status_between_rounds()
        return messages

    # Make the current player check, betting no additional money
    def check(self) -> List[object]:
        self.current_player.placed_bet = True
        return [EmbedTitle(f"{self.current_player.name} checks.")] + self.next_turn()

    # Has the current player raise a certain amount
    def raise_bet(self, amount: int) -> List[object]:
        self.pot.handle_raise(self.current_player, amount)
        messages = [EmbedTitle(f"{self.current_player.name} raises by ${amount}.")]
        if self.current_player.balance == 0:
            self.leave_hand(self.current_player)
            self.turn_index -= 1
        return messages + self.next_turn()

    # Has the current player match the current bet
    def call(self) -> List[object]:
        self.pot.handle_call(self.current_player)
        messages = [EmbedTitle(f"{self.current_player.name} calls.")]
        if self.current_player.balance == 0:
            self.leave_hand(self.current_player)
            self.turn_index -= 1
        return messages + self.next_turn()

    def all_in(self) -> List[object]:
        if self.pot.cur_bet > self.current_player.max_bet:
            return self.call()
        else:
            return self.raise_bet(self.current_player.max_bet - self.cur_bet)

    # Has the current player fold their hand
    def fold(self) -> List[object]:
        messages = [EmbedTitle(f"{self.current_player.name} has folded.")]
        self.pot.handle_fold(self.current_player)
        self.leave_hand(self.current_player)

        # If only one person is left in the pot, give it to them instantly
        if len(self.pot.in_pot()) == 1:
            winner = list(self.pot.in_pot())[0]
            messages += [EmbedField(f"{winner.name} wins ${self.pot.value}!", u"\u200B", False)]
            winner.balance += self.pot.value

            # Print winner's chip count
            name = f"**{winner.user.name}:** ${winner.balance} (+${self.pot.value})"
            messages.append(EmbedField(name, u"\u200B", True))

            self.state = GameState.NO_HANDS
            self.next_dealer()
            if not self.options["auto-deal"]:
                messages += self.status_between_rounds()
            return messages

        # If there's still betting to do, go on to the next turn
        if not self.pot.betting_over():
            self.turn_index -= 1
            return messages + self.next_turn()

        # Otherwise, have the showdown immediately
        return self.showdown()

    # Send a message to each player, telling them what their hole cards are
    async def tell_hands(self, client: discord.Client):
        for player in self.players:
            dm_channel = await player.user.create_dm()
            await dm_channel.send(str(player.cards[0]) + "  " + str(player.cards[1]))
