# Scoundrel

Terminal-based implementation of **Scoundrel** (a single-player rogue-like card game by Zach Gage and Kurt Bieg).

## Rules Summary

* **Deck (44 cards)**: Standard deck with Jokers, Red Face Cards (`J♦, Q♦, K♦, J♥, Q♥, K♥`), and Red Aces (`A♦, A♥`) removed.
  * **26 Monsters (`♣` / `♠`)**: Deal damage equal to their ordered rank (`2`–`10`, `J=11`, `Q=12`, `K=13`, `A=14`).
  * **9 Weapons (`♦` `2`–`10`)**: Binding when picked up; replace and discard your previous weapon and its slain monsters.
  * **9 Health Potions (`♥` `2`–`10`)**: Restore health up to `20` (maximum 1 potion per turn; a second potion in the same turn is discarded for `0`).
* **Rooms & Turns**: Each turn deals cards from the **Dungeon** until 4 cards are face-up in the **Room**.
  * **Avoid Room**: At the start of a turn (before resolving any of the 4 Room cards), you may scoop all 4 cards to the bottom of the Dungeon—never two turns in a row.
  * **Face the Room**: Resolve 3 of the 4 cards one at a time. The 4th card stays face-up as the first card of the next Room.
* **Combat**:
  * **Barehanded**: Subtract full Monster value from your Health and discard the Monster.
  * **Equipped Weapon**: Subtract `max(0, Monster - Weapon)` from your Health and stack the Monster face-up onto the Weapon. Once a Weapon slays a Monster of value `N`, it can only be used against Monsters of value `≤ N`.

## Controls

### Keyboard Controls

| Key                 | Action                                                                   |
| ------------------- | ------------------------------------------------------------------------ |
| `1` – `4`           | Jump cursor directly to Room slot 1–4                                    |
| `Space` / `Enter`   | Play focused card (Smart Play: equip weapon, drink potion, or attack)    |
| `w`                 | Fight with equipped Weapon (or equip Weapon card)                        |
| `b`                 | Fight Barehanded (take monster damage directly)                          |
| `p` / `h`           | Drink Health Potion                                                      |
| `v`                 | Avoid current Room (scoop all 4 Room cards to bottom of Dungeon)         |
| `Arrow Keys`        | Navigate cursor between piles                                            |
| `Esc`               | Deselect / cancel selection                                              |
| `d` / `0`           | Jump cursor to Dungeon pile                                              |
| `e` / `5`           | Jump cursor to Equipped Weapon pile                                      |
| `m`                 | Return to Main Menu                                                      |
| `r`                 | Restart new game                                                         |
| `q` / `Ctrl+C`      | Quit                                                                     |

> **HUD Combat & Action Forecast**: As you move the cursor or press `1`–`4`, the HUD dynamically forecasts the outcome of every option (e.g. `Weapon (-3 HP -> ♥ 17, limit ≤ 8)   Barehanded (-8 HP -> ♥ 12)`), preventing arithmetic mistakes.

### Mouse Controls

| Action                          | Result                                                               |
| ------------------------------- | -------------------------------------------------------------------- |
| **Left Click** on Room Card     | Select and inspect Room card (updates HUD combat preview)            |
| **Double Click** on Room Card   | Smart play card (equip weapon, drink potion, or fight with weapon)   |
| **Left Click** on Weapon Pile   | Equip selected Weapon or fight selected Monster with Weapon          |
| **Left Click** on Discard Pile  | Drink selected Potion or fight selected Monster barehanded           |
| **Left Click** on Dungeon       | Avoid the current Room (if allowed)                                  |
