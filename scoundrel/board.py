from termcolor import colored

from core.board import Board as BaseBoard
from core.card import Card, Rank, Suit
from core.pile import Pile
from scoundrel.pile import ScoundrelPile, card_value, is_monster, is_potion, is_weapon


class Board(BaseBoard):
    """Scoundrel board implementation."""

    MAX_HEALTH: int = 20
    ROOM_SIZE: int = 4
    CARDS_PER_TURN: int = 3
    DUNGEON_COL: int = 0
    ROOM_START_COL: int = 2
    DISCARD_COL: int = 7
    WEAPON_COL: int = 2

    def reset(self):
        """Reset the Scoundrel board to a newly shuffled 44-card dungeon."""
        deck: list[Card] = [
            Card(rank, suit, face_up=False)
            for suit in Suit
            for rank in Rank
            if not (suit in (Suit.DIAMOND, Suit.HEART) and rank in (Rank.ACE, Rank.JACK, Rank.QUEEN, Rank.KING))
        ]
        self.dungeon_pile = ScoundrelPile(deck)
        self.dungeon_pile.shuffle()

        self.room: list[ScoundrelPile] = [ScoundrelPile([]) for _ in range(self.ROOM_SIZE)]
        self.discard_pile = ScoundrelPile([])
        self.weapon_pile = ScoundrelPile([], stretched=True)
        self.from_pile: ScoundrelPile | None = None

        self.health: int = self.MAX_HEALTH
        self.avoided_last_turn: bool = False
        self.potion_used_this_turn: bool = False
        self.cards_taken_this_turn: int = 0
        self.last_card: Card | None = None
        self._last_top_col: int = self.ROOM_START_COL

        self.board: list[list[ScoundrelPile]] = [
            [
                self.dungeon_pile,
                ScoundrelPile(None),
                *self.room,
                ScoundrelPile(None),
                self.discard_pile,
            ],
            [
                ScoundrelPile(None),
                ScoundrelPile(None),
                self.weapon_pile,
                ScoundrelPile(None),
                ScoundrelPile(None),
                ScoundrelPile(None),
                ScoundrelPile(None),
                ScoundrelPile(None),
            ],
        ]

        self.deal_room()
        self.current_selection = (0, self.ROOM_START_COL)
        self.current_pile.select()

    # --- properties & game state ---

    @property
    def room_card_count(self) -> int:
        """Return the number of cards currently face-up in the Room."""
        return sum(len(p) for p in self.room)

    @property
    def equipped_weapon(self) -> Card | None:
        """Return currently equipped weapon card, or None."""
        return self.weapon_pile.get_weapon_card()

    @property
    def slain_monsters(self) -> list[Card]:
        """Return list of monsters slain by the currently equipped weapon."""
        return self.weapon_pile.get_slain_monsters()

    @property
    def last_slain_monster(self) -> Card | None:
        """Return the last monster slain by the current weapon, or None."""
        return self.weapon_pile.get_last_slain_monster()

    def is_lost(self) -> bool:
        """True if the player's health has dropped to 0."""
        return self.health <= 0

    def is_won(self) -> bool:
        """True if the player survived all cards in the Dungeon and Room."""
        return self.health > 0 and self.dungeon_pile.is_empty() and self.room_card_count == 0

    def is_game_over(self) -> bool:
        """True if the game has ended in either victory or defeat."""
        return self.is_won() or self.is_lost()

    def get_score(self) -> int:
        """
        Compute the official Scoundrel score:
        - If life reached 0: negative sum of all remaining monsters in the Dungeon (and Room).
        - If dungeon cleared: current health, plus last potion value if health is 20 and last card was a potion.
        """
        if self.is_lost():
            remaining = [*self.dungeon_pile.cards, *(c for p in self.room for c in p.cards)]
            monster_total = sum(card_value(c) for c in remaining if is_monster(c))
            return self.health - monster_total
        if self.is_won() and self.health == self.MAX_HEALTH and is_potion(self.last_card):
            return self.health + card_value(self.last_card)
        return self.health

    # --- room & turn progression ---

    def deal_room(self):
        """Fill empty Room slots from the top of the Dungeon up to 4 cards."""
        for pile in self.room:
            if pile.is_empty() and not self.dungeon_pile.is_empty():
                self.dungeon_pile.move_top_card_to_pile(pile, face_up=True)
            pile.reset_selection()
        self.dungeon_pile.reset_selection()

    def can_avoid_room(self) -> bool:
        """True if the player may avoid the current Room."""
        return (
            not self.is_game_over()
            and not self.avoided_last_turn
            and self.cards_taken_this_turn == 0
            and self.room_card_count == self.ROOM_SIZE
        )

    def avoid_room(self) -> bool:
        """Scoop all 4 Room cards to the bottom of the Dungeon and deal a new Room."""
        if not self.can_avoid_room():
            return False
        self.deselect_from_pile()
        for pile in self.room:
            pile.move_top_card_to_bottom(self.dungeon_pile, face_up=False)
        self.avoided_last_turn = True
        self.potion_used_this_turn = False
        self.cards_taken_this_turn = 0
        self.deal_room()
        self.current_pile.reset_selection()
        return True

    def _complete_card_action(self, source_pile: ScoundrelPile, card: Card):
        """Update turn counters after resolving a Room card and deal next Room when turn ends."""
        self.last_card = card
        self.cards_taken_this_turn += 1
        source_pile.reset_selection()
        self.deselect_from_pile()

        if self.is_game_over():
            self.current_pile.reset_selection()
            return

        if self.cards_taken_this_turn >= self.CARDS_PER_TURN or (
            self.room_card_count <= 1 and not self.dungeon_pile.is_empty()
        ):
            self.cards_taken_this_turn = 0
            self.potion_used_this_turn = False
            self.avoided_last_turn = False
            self.deal_room()

        # If the cursor was on the card that was just resolved and it is now empty,
        # advance cursor to the next non-empty room card.
        if self.current_pile == source_pile and source_pile.is_empty():
            for offset in range(1, self.ROOM_SIZE):
                next_idx = (self.room.index(source_pile) + offset) % self.ROOM_SIZE
                if not self.room[next_idx].is_empty():
                    self.navigate_to_coordinate(0, self.ROOM_START_COL + next_idx)
                    break

        self.current_pile.reset_selection()

    # --- card actions ---

    def can_fight_with_weapon(self, card: Card | None) -> bool:
        """True if `card` is a Monster that can be slain with the currently equipped weapon."""
        return self.weapon_pile.can_slay_monster(card)

    def equip_weapon(self, room_pile: ScoundrelPile) -> bool:
        """Equip a Diamond weapon from `room_pile`, discarding any previous weapon and its monsters."""
        if self.is_game_over() or room_pile not in self.room or room_pile.is_empty():
            return False
        card = room_pile.get_top_card()
        if not is_weapon(card):
            return False

        while not self.weapon_pile.is_empty():
            self.weapon_pile.move_card_to_pile(self.weapon_pile.cards[0], self.discard_pile, face_up=False)

        room_pile.move_top_card_to_pile(self.weapon_pile, face_up=True)
        self._complete_card_action(room_pile, card)
        return True

    def use_potion(self, room_pile: ScoundrelPile) -> bool:
        """Consume a Heart potion from `room_pile` (up to 1 per turn, max 20 HP) and discard it."""
        if self.is_game_over() or room_pile not in self.room or room_pile.is_empty():
            return False
        card = room_pile.get_top_card()
        if not is_potion(card):
            return False

        if not self.potion_used_this_turn:
            self.health = min(self.MAX_HEALTH, self.health + card_value(card))
            self.potion_used_this_turn = True

        room_pile.move_top_card_to_pile(self.discard_pile, face_up=False)
        self._complete_card_action(room_pile, card)
        return True

    def fight_monster(self, room_pile: ScoundrelPile, use_weapon: bool = False) -> bool:
        """Fight a Club/Spade monster from `room_pile` either with the equipped weapon or barehanded."""
        if self.is_game_over() or room_pile not in self.room or room_pile.is_empty():
            return False
        card = room_pile.get_top_card()
        if not is_monster(card):
            return False

        if use_weapon:
            if not self.can_fight_with_weapon(card):
                return False
            damage = max(0, card_value(card) - self.weapon_pile.get_weapon_value())
            self.health = max(0, self.health - damage)
            room_pile.move_top_card_to_pile(self.weapon_pile, face_up=True)
        else:
            damage = card_value(card)
            self.health = max(0, self.health - damage)
            room_pile.move_top_card_to_pile(self.discard_pile, face_up=False)

        self._complete_card_action(room_pile, card)
        return True

    # --- high-level interaction & pile moves ---

    def can_move_to(self, to_pile: ScoundrelPile) -> bool:
        """True if the currently selected `from_pile` Room card can legally move to `to_pile`."""
        if self.is_game_over() or self.from_pile is None or self.from_pile.is_empty():
            return False
        card = self.from_pile.get_top_card()
        if is_weapon(card):
            return to_pile == self.weapon_pile
        if is_potion(card):
            return to_pile == self.discard_pile
        if is_monster(card):
            if to_pile == self.discard_pile:
                return True
            if to_pile == self.weapon_pile:
                return self.can_fight_with_weapon(card)
        return False

    def _execute_move(self, from_pile: ScoundrelPile, to_pile: ScoundrelPile):
        """Resolve moving the selected Room card onto `weapon_pile` or `discard_pile`."""
        card = from_pile.get_top_card()
        if to_pile == self.weapon_pile:
            if is_weapon(card):
                self.equip_weapon(from_pile)
            else:
                self.fight_monster(from_pile, use_weapon=True)
        elif to_pile == self.discard_pile:
            if is_potion(card):
                self.use_potion(from_pile)
            else:
                self.fight_monster(from_pile, use_weapon=False)

    def auto_resolve_card(self, pile: ScoundrelPile | None = None) -> bool:
        """Automatically resolve a Room card (equip weapon, drink potion, or fight with weapon if possible)."""
        source = pile or self.from_pile or self.current_pile
        if self.is_game_over() or source not in self.room or source.is_empty():
            return False
        card = source.get_top_card()
        if is_weapon(card):
            return self.equip_weapon(source)
        if is_potion(card):
            return self.use_potion(source)
        if is_monster(card):
            return self.fight_monster(source, use_weapon=self.can_fight_with_weapon(card))
        return False

    def act_with_weapon(self, pile: ScoundrelPile | None = None) -> bool:
        """Equip a weapon or fight a monster using the equipped weapon."""
        source = pile or self.from_pile or self.current_pile
        if self.is_game_over() or source not in self.room or source.is_empty():
            return False
        card = source.get_top_card()
        if is_weapon(card):
            return self.equip_weapon(source)
        if is_monster(card):
            return self.fight_monster(source, use_weapon=True)
        return False

    def act_barehanded(self, pile: ScoundrelPile | None = None) -> bool:
        """Fight a monster barehanded or consume a health potion."""
        source = pile or self.from_pile or self.current_pile
        if self.is_game_over() or source not in self.room or source.is_empty():
            return False
        card = source.get_top_card()
        if is_potion(card):
            return self.use_potion(source)
        if is_monster(card):
            return self.fight_monster(source, use_weapon=False)
        return False

    def act_potion(self, pile: ScoundrelPile | None = None) -> bool:
        """Consume a Health Potion from `pile` (or selected/current pile)."""
        source = pile or self.from_pile or self.current_pile
        if self.is_game_over() or source not in self.room or source.is_empty():
            return False
        card = source.get_top_card()
        if is_potion(card):
            return self.use_potion(source)
        return False

    def choose_pile(self):
        """Handle selecting, deselecting, avoiding the Room, and moving Room cards."""
        if self.is_game_over():
            return
        to_pile = self.current_pile

        if to_pile == self.dungeon_pile:
            self.deselect_from_pile()
            self.avoid_room()
            return

        if self.from_pile == to_pile:
            self.deselect_from_pile()
            return

        if self.from_pile is None:
            if to_pile in self.room and not to_pile.is_empty():
                if not to_pile.is_selected:
                    to_pile.select()
                self.from_pile = to_pile
            return

        if self.can_move_to(to_pile):
            self._execute_move(self.from_pile, to_pile)

    # --- navigation & selection hooks ---

    def navigate_board(self, direction: str):
        """Navigate cleanly between Row 0 piles and the single Weapon pile on Row 1."""
        row, col = self.current_selection
        if direction in ('up', 'down'):
            if row == 0:
                self._last_top_col = col
                self._move_cursor(1, self.WEAPON_COL)
            else:
                target_col = self._last_top_col if self.is_navigable(0, self._last_top_col) else self.ROOM_START_COL
                self._move_cursor(0, target_col)
            return
        super().navigate_board(direction)

    def deselect_from_pile(self):
        if self.from_pile is None:
            return
        self.from_pile.deselect()
        self.from_pile = None
        self.current_pile.select()

    def _on_leave(self, row: int, col: int):
        if row == 0:
            self._last_top_col = col
        pile = self.board[row][col]
        if self.from_pile != pile:
            pile.deselect()

    def _on_enter(self, row: int, col: int):
        self.board[row][col].select()

    def _pile_indicator(self, pile: Pile) -> tuple[str, str | None] | None:
        is_chosen = self.from_pile == pile
        if pile.is_selected or is_chosen:
            color = 'yellow' if (pile.is_selected and is_chosen) else ('red' if is_chosen else None)
            return (self.INDICATOR, color)
        return None

    # --- rendering ---

    def _build_action_preview(self) -> str:
        """Return a dynamic combat and action forecast for the active card or pile."""
        target = self.from_pile or self.current_pile
        if target in self.room:
            if target.is_empty():
                return colored(' Target: Empty Slot', 'dark_grey')
            card = target.get_top_card()
            slot_num = self.room.index(target) + 1
            card_label = f'[{slot_num}] {card_value(card)}{card.suit.value}'

            if is_weapon(card):
                power = card_value(card)
                if self.equipped_weapon:
                    old_power = self.weapon_pile.get_weapon_value()
                    return (
                        f' Target: {card_label} Weapon | [Space/Enter/w] Equip (Power {power}, replaces ♦ {old_power})'
                    )
                return f' Target: {card_label} Weapon | [Space/Enter/w] Equip (Power {power})'

            if is_potion(card):
                pot_val = card_value(card)
                if not self.potion_used_this_turn:
                    heal = min(pot_val, self.MAX_HEALTH - self.health)
                    new_hp = self.health + heal
                    heal_str = colored(f'+{heal} HP', 'green')
                    return f' Target: {card_label} Potion | [Space/Enter/p] Drink ({heal_str} -> ♥ {new_hp})'
                return f' Target: {card_label} Potion | [Space/Enter/p] Discard (already used potion this turn -> +0 HP)'

            if is_monster(card):
                m_val = card_value(card)
                bare_dmg = m_val
                bare_hp = max(0, self.health - bare_dmg)
                bare_color = 'red' if bare_hp <= 5 else 'yellow'
                bare_text = f"[b] Bare ({colored(f'-{bare_dmg}', bare_color)} -> ♥ {bare_hp})"

                if self.can_fight_with_weapon(card):
                    w_dmg = max(0, m_val - self.weapon_pile.get_weapon_value())
                    w_hp = max(0, self.health - w_dmg)
                    w_color = 'green' if w_dmg == 0 else ('red' if w_hp <= 5 else 'yellow')
                    w_text = f"[Space/Enter/w] Weapon ({colored(f'-{w_dmg}', w_color)} -> ♥ {w_hp}, limit ≤ {m_val})"
                    return f' Target: {card_label} Monster | {w_text}   {bare_text}'

                if self.equipped_weapon is not None:
                    max_slay = self.weapon_pile.get_max_monster_value()
                    w_text = colored(f'[w] Unusable ({m_val} > cap {max_slay})', 'dark_grey')
                    bare_action = f"[Space/Enter/b] Bare ({colored(f'-{bare_dmg}', bare_color)} -> ♥ {bare_hp})"
                    return f' Target: {card_label} Monster | {bare_action}   {w_text}'

                bare_action = f"[Space/Enter/b] Bare ({colored(f'-{bare_dmg}', bare_color)} -> ♥ {bare_hp})"
                return f' Target: {card_label} Monster | {bare_action}   (No weapon)'

        if target == self.dungeon_pile:
            if self.can_avoid_room():
                msg = ' Target: Dungeon | [v/Space/Enter] Avoid Room (put 4 room cards at bottom of deck)'
                return colored(msg, 'cyan')
            if self.avoided_last_turn:
                reason = 'cannot avoid 2 turns in a row'
            elif self.cards_taken_this_turn > 0:
                reason = 'already resolved cards this turn'
            else:
                reason = 'room not full'
            return colored(f' Target: Dungeon | Cannot avoid room ({reason})', 'dark_grey')

        if target == self.weapon_pile:
            if self.equipped_weapon:
                slain = self.slain_monsters
                slain_str = ', '.join(f'{card_value(c)}{c.suit.value}' for c in slain) if slain else 'None'
                max_s = self.weapon_pile.get_max_monster_value()
                w_val = self.weapon_pile.get_weapon_value()
                return (
                    f' Target: Weapon Pile | Equipped: ♦ {w_val} | Slain: [{slain_str}] | Next monster cap: ≤ {max_s}'
                )
            return ' Target: Weapon Pile | Unarmed'

        if target == self.discard_pile:
            return f' Target: Discard Pile | {len(self.discard_pile)} cards discarded'

        return ''

    def _build_hud_rows(self) -> list[list[str]]:
        """Render status and control lines below the card grid."""
        hp_color = 'green' if self.health > 10 else ('yellow' if self.health > 5 else 'red')
        hp_text = colored(f'♥ {self.health}/{self.MAX_HEALTH}', hp_color)

        weapon = self.equipped_weapon
        if weapon is None:
            weapon_text = 'None'
        else:
            w_val = self.weapon_pile.get_weapon_value()
            last_monster = self.last_slain_monster
            limit_str = f'≤ {card_value(last_monster)}' if last_monster else 'any'
            weapon_text = f'♦ {w_val} ({limit_str})'

        avoid_text = colored('Ready [v]', 'cyan') if self.can_avoid_room() else 'No'
        potion_text = 'Ready' if not self.potion_used_this_turn else 'Used'
        rem_in_turn = max(0, min(self.CARDS_PER_TURN - self.cards_taken_this_turn, self.room_card_count))

        lines = [
            [''],
            [
                f' Health: {hp_text}   Weapon: {weapon_text}   '
                f'Dungeon: {len(self.dungeon_pile)}   Discard: {len(self.discard_pile)}'
            ],
            [f' Room: {rem_in_turn} to play   Potion: {potion_text}   Avoid Room: {avoid_text}'],
        ]
        if self.is_lost():
            msg = f' GAME OVER — You fell in the dungeon! Final Score: {self.get_score()}  ([r] Restart  [m] Menu)'
            lines.append([colored(msg, 'red', attrs=['bold'])])
        elif self.is_won():
            msg = f' VICTORY! — You cleared the dungeon! Final Score: {self.get_score()}  ([r] Restart  [m] Menu)'
            lines.append([colored(msg, 'green', attrs=['bold'])])
        else:
            preview = self._build_action_preview()
            if preview:
                lines.append([preview])
            lines.append([' [1-4] Target   [Space/Enter] Play   [w] Weapon   [b] Barehanded   [v] Avoid'])
        return lines

    def get_print_string(self) -> list[list[str]]:
        """Render all board rows followed by the Scoundrel status HUD."""
        return [*super().get_print_string(), *self._build_hud_rows()]
