<div align="center">

# TCG — Classic card games in your terminal

<pre style="background: transparent; border: none; box-shadow: none; display: inline-block; text-align: left;">
  O=====================================================================O

     ┌─────────┐                                           ┌─────────┐   
     │ A ♠     │       ████████╗  ██████╗   ██████╗        │ Q ♦     │   
     │         │       ╚══██╔══╝ ██╔════╝  ██╔════╝        │         │   
     │   ┌─────┴───┐      ██║    ██║       ██║  ███╗   ┌───┴─────┐   │   
     │   │ K ♥     │      ██║    ██║       ██║   ██║   │ J ♣     │   │   
     │   │         │      ██║    ╚██████╗  ╚██████╔╝   │         │ ♦ │   
     └───┤    ♥    │      ╚═╝     ╚═════╝   ╚═════╝    │    ♣    ├───┘   
         │         │        TERMINAL CARD GAMES        │         │       
         │     K ♥ │                                   │     J ♣ │       
         └─────────┘           ♠   ♥   ♦   ♣           └─────────┘       

  O=====================================================================O
</pre>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=flat-square" alt="Python version">
  <img src="https://img.shields.io/badge/TUI-prompt__toolkit-informational?style=flat-square" alt="prompt_toolkit">
  <img src="https://img.shields.io/badge/tests-45%20passed-brightgreen?style=flat-square" alt="Tests status">
  <img src="https://img.shields.io/badge/code%20style-ruff-black?style=flat-square" alt="Ruff style">
</p>

[Games](#games) · [Install](#install) · [Quick start](#quick-start) · [Solitaire Guide](./solitaire/README.md) · [Development](#development)

</div>

TCG (Terminal Card Games) is an open-source terminal card game platform built with Python and `prompt_toolkit`. It brings classic card games directly to your command line using ASCII card designs.

## Install

Requires Python 3.10+. Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Or install as an editable package to make the `tcg` command available globally:

```bash
pip install -e .
```

## Quick start

Launch the game launcher:

```bash
python main.py
```

If you installed with `pip install -e .`, you can launch directly with:

```bash
tcg
```

Use the arrow keys or number shortcuts in the launcher menu to select and start a game.

## Games

- **[Solitaire (Klondike)](./solitaire/README.md)** — Classic 7-column Klondike. Check the [Solitaire Guide](./solitaire/README.md) for game controls.

## Development

Run tests:

```bash
./tools/run_tests.sh
```

Run code formatting and style checks:

```bash
./tools/validate_code.sh
```
