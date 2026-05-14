# generated file

import pygame
import sys

from game.manager.game_manager import GameManager
from game.world.config import DT, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT
from game.world.map import MAP_DATA


SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = MAP_HEIGHT * TILE_SIZE

FPS = 60


def draw_map(screen):

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):

            tile = MAP_DATA[
                y * MAP_WIDTH + x
            ]

            rect = pygame.Rect(
                x * TILE_SIZE,
                y * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE,
            )

            if tile == 1:
                pygame.draw.rect(
                    screen,
                    (100, 100, 100),
                    rect,
                )
            else:
                pygame.draw.rect(
                    screen,
                    (30, 30, 30),
                    rect,
                )

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                rect,
                1,
            )


def draw_players(screen, players):

    for player in players:

        if not player.alive:
            color = (40, 40, 40)

        elif player.is_tagger:
            color = (255, 60, 60)

        elif player.number == 1:
            color = (80, 180, 255)

        elif player.number == 2:
            color = (80, 255, 120)

        elif player.number == 3:
            color = (255, 220, 80)

        else:
            color = (200, 80, 255)

        size = TILE_SIZE * 0.5

        rect = pygame.Rect(
            int(player.x * TILE_SIZE - size / 2),
            int(player.y * TILE_SIZE - size / 2),
            int(size),
            int(size),
        )

        pygame.draw.rect(
            screen,
            color,
            rect,
        )

        font = pygame.font.SysFont(
            None,
            20,
        )

        text = font.render(
            str(player.number),
            True,
            (255, 255, 255),
        )

        screen.blit(
            text,
            (
                rect.x + 8,
                rect.y + 6,
            ),
        )


def draw_ui(screen, game, game_count):

    font = pygame.font.SysFont(
        None,
        24,
    )

    alive_count = sum(
        1 for p in game.players
        if p.alive
    )

    tagger_name = (
        game.tagger.name
        if game.tagger
        else "None"
    )

    text = font.render(
        f"GAME {game_count} | alive={alive_count} | tagger={tagger_name}",
        True,
        (255, 255, 255),
    )

    screen.blit(
        text,
        (10, 10),
    )


def main():

    pygame.init()

    screen = pygame.display.set_mode(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
        )
    )

    pygame.display.set_caption(
        "AI Watch Mode"
    )

    clock = pygame.time.Clock()

    game_count = 1
    game = GameManager()

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not game.game_over:
            game.update(DT)
        else:
            game_count += 1
            game = GameManager()

        screen.fill(
            (0, 0, 0)
        )

        draw_map(screen)
        draw_players(screen, game.players)
        draw_ui(screen, game, game_count)

        pygame.display.flip()

        clock.tick(FPS)


if __name__ == "__main__":
    main()