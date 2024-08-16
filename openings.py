openings = {
    "Ruy Lopez": [
        {"name": "Ruy Lopez: Morphy Defense, Closed", "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4", "g8f6", "e1g1", "f8e7", "d2d4", "e5d4", "f3d4"]},
        {"name": "Ruy Lopez: Morphy Defense, Classical Defense", "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "f8c5", "c2c3", "g8f6", "d2d4", "c5d4", "c3d4"]},
        {"name": "Ruy Lopez: Steinitz Defense Deferred", "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "d7d6", "d2d4", "c8d7", "c2c3", "g8f6", "e1g1", "f6e4"]},
        {"name": "Ruy Lopez: Morphy Defense, Modern Steinitz Defense", "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4", "g8f6", "e1g1", "b7b5", "a4b3", "d7d6"]},
        {"name": "Ruy Lopez: Bird's Defense", "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "g8f6", "d2d3", "d7d6", "b1c3", "f6e4", "c3e4"]},
    ],
    "Sicilian Defense": [
        {"name": "Sicilian Defense: Najdorf Variation", "moves": ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "a7a6", "f1e2"]},
        {"name": "Sicilian Defense: Scheveningen Variation", "moves": ["e2e4", "c7c5", "g1f3", "e7e6", "d2d4", "c5d4", "f3d4", "a7a6", "b1c3", "d8c7", "c1e3"]},
        {"name": "Sicilian Defense: Alapin Variation", "moves": ["e2e4", "c7c5", "d2d4", "c5d4", "c2c3", "d4c3", "b1c3", "g8f6", "f1d3", "e7e5", "d1a4"]},
        {"name": "Sicilian Defense: Sozin Attack", "moves": ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3", "a7a6", "f2f4", "e7e5"]},
        {"name": "Sicilian Defense: Richter-Rauzer Attack", "moves": ["e2e4", "c7c5", "g1f3", "e7e6", "d2d4", "c5d4", "f3d4", "a7a6", "d4f3", "g8f6", "c1g5"]},
    ],
    "French Defense": [
        {"name": "French Defense: Winawer Variation", "moves": ["e2e4", "e7e6", "d2d4", "d7d5", "b1c3", "f8b4", "e4e5", "c7c5", "a2a3", "b4a5", "g1f3"]},
        {"name": "French Defense: Classical Variation", "moves": ["e2e4", "e7e6", "d2d4", "d7d5", "b1d2", "g8f6", "e4e5", "f6d7", "f1d3", "b8c6", "c2c3"]},
        {"name": "French Defense: Rubinstein Variation", "moves": ["e2e4", "e7e6", "d2d4", "d7d5", "g1f3", "g8f6", "e4e5", "f6e4", "b1d2", "e4d2", "f1d2"]},
        {"name": "French Defense: Steinitz Variation", "moves": ["e2e4", "e7e6", "d2d4", "d7d5", "b1c3", "c7c5", "g1f3", "g8f6", "c1g5", "f8e7", "d4c5"]},
        {"name": "French Defense: Burn Variation", "moves": ["e2e4", "e7e6", "d2d4", "d7d5", "b1d2", "f8e7", "g1f3", "g8f6", "e4e5", "f6e4", "c2c4"]},
    ],
    "Queen's Gambit": [
        {"name": "Queen's Gambit Declined: Orthodox Defense", "moves": ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5", "f8e7", "e2e3", "e8g8", "f1d3"]},
        {"name": "Queen's Gambit Declined: Tartakower Defense", "moves": ["d2d4", "d7d5", "c2c4", "c7c6", "g1f3", "g8f6", "b1c3", "e7e6", "c1g5", "h7h6", "g5f6"]},
        {"name": "Queen's Gambit Declined: Ragozin Defense", "moves": ["d2d4", "d7d5", "c2c4", "e7e6", "g1f3", "g8f6", "b1c3", "f8b4", "c1d2", "e8g8", "e2e3", "b4c3"]},
        {"name": "Queen's Gambit Accepted: Classical Defense", "moves": ["d2d4", "d7d5", "c2c4", "c7c6", "g1f3", "g8f6", "b1c3", "d5c4", "e2e3", "c8b7", "f1c4"]},
        {"name": "Queen's Gambit Declined: Lasker Defense", "moves": ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6", "c1g5", "h7h6", "g5f6", "d8f6", "g1f3", "f6d8"]},
    ],
}


def get_random_opening_line(opening_name):
      return openings[opening_name]