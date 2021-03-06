# Arcade-CS-Games-2015
Jeux pour l'arcade des CS Games 2015

Began so far:
Dirty framework hacked together with love <3

## Ajouter un minigame
Créer un nouveau module sous `/minigames/` et créer une classe dérivant de `multiplayer.Minigame` ou `singleplayer.Minigame`. Un jeu de type singleplayer consiste à un minigame joué tour par tour jusqu'à ce qu'un joueur ait 3 défaites. Un jeu multijoueur est joué par les deux joueurs simultanément.

Finalement, importé la classe du jeu dans `/minigames/__init__.py`.

Chaque classe de minigame doivent définir l'attribut de classe `name` qui sera affiché aux joueurs.

Les méthode suivante peuvent être définit dans la classe de jeu:

### init(self)
Méthode appelé avant une manche du jeu.

### tick(self)
Méthode appelé à chaque boucle d'update.

### get\_duration(self)
Méthode retournant le temps de jeu total. Peut être généré à partir de `self.difficulty` pour diminuer le temps selon la difficulté.

### get\_results(self) ou get\_result(self)
Méthode retournant le résultat des joueurs ou du joueur dans le cas d'un jeu singleplayer.

## Exemple multiplayer
```python
import pygame
from pygame.locals import *
import multiplayer
from input_map import *

class MTest(multiplayer.Minigame):
    name = "Multiplayer Test"

    def init(self):
        self.results = [False, False]

    def tick(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                for i in range(2):
                    if event.key == PLAYERS_MAPPING[i][UP]:
                        self.results[i] = True
                    elif event.key == PLAYERS_MAPPING[i][DOWN]:
                        self.results[i] = False

        self.gfx.print_msg("[W]in or [L]ose", (50, 50))

        if self.results[0]:
            self.gfx.print_msg("Winning", (50, 100), color=(0, 255, 0))
        else:
            self.gfx.print_msg("Losing", (50, 100), color=(255, 0, 0))

        if self.results[1]:
            self.gfx.print_msg("Winning", topright=(750, 100), color=(0, 255, 0))
        else:
            self.gfx.print_msg("Losing", topright=(750, 100), color=(255, 0, 0))

    def get_results(self):
        return self.results
```

## Exemple singleplayer
```python
import pygame
from pygame.locals import *
import singleplayer
from input_map import *

class STest(singleplayer.Minigame):
    name = "Singleplayer Test"

    def init(self):
        self.result = False

    def tick(self):
        pygame.event.get()
        self.result = self.get_player_keys()[UP]

        self.gfx.print_msg("[W]in or [L]ose", (50, 50))

        if self.result:
            self.gfx.print_msg("Winning", (50, 100), color=(0, 255, 0))
        else:
            self.gfx.print_msg("Losing", (50, 100), color=(255, 0, 0))

    def get_result(self):
        return self.result
```
