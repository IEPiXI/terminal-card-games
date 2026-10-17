# Solitaire

Terminal-based Solitaire (Klondike) game.

## Controls

| Key                                         | Action                                                 |
| ------------------------------------------- | ------------------------------------------------------ |
| `↑` `↓` `←` `→`                             | Navigate cursor between piles                          |
| `Space` / `Enter`                           | Select pile / move cards / flip card / draw from stock |
| `Esc`                                       | Deselect / cancel move                                 |
| `w` / `s`                                   | Increase / decrease number of cards selected           |
| `1` – `7`                                   | Jump to Tableau column 1–7                             |
| `Shift+1` – `Shift+4` / `Ctrl+1` – `Ctrl+4` | Jump to Foundation 1–4                                 |
| `Shift+5` / `Ctrl+5`                        | Jump to Waste pile                                     |
| `Shift+6` / `Ctrl+6`                        | Jump to Stock pile                                     |
| `m`                                         | Return to Main Menu                                    |
| `r`                                         | Restart new game                                       |
| `q` / `Ctrl+C`                              | Quit                                                   |

### Mouse Controls

| Action                  | Result                                     |
| ----------------------- | ------------------------------------------ |
| **Left Click** on Stock | Draw card to Waste (or recycle when empty) |
| **Left Click** on Pile  | Select pile / move card(s) / flip card     |
| **Left Click** on Card  | Select run starting from clicked card      |
| **Double Click**        | Auto-move card to eligible Foundation      |
