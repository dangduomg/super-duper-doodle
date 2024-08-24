import random
import pygame

import sprites
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, FPS, \
                      QUIT, KEYDOWN, QUIT_KEYS, BG_COLOR
from sprites import MySprite, SolidBlock
from player import Player, Bullet


pygame.init()


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

clock = pygame.time.Clock()
frames = 0

INSTRUCTIONS_TEXT = ( 'Press Left and Right keys to move.'
                    , 'Hold S while moving to move faster.'
                    , 'Press Up to hop, hold Up for a high jump.'
                    , 'Press A to shoot.'
                    , 'Press Q or Escape to quit the game.'
                    )
HUD_TEXT = ( *INSTRUCTIONS_TEXT
           , ''
           , 'center x: {centerx}, center y: {centery}'
           , 'x velocity: {vx}, y velocity: {vy}'
           )
HUD_FONT = pygame.font.SysFont(None, 24)
HUD_TEXT_COLOR = 255, 255, 255
HUD_HORZ_MARGIN = 8
HUD_VERT_MARGIN = 8
HUD_LINE_SPACING = 4

class Block(SolidBlock):
    SIZE = 32
    COLOR = 255, 255, 255

    # all blocks are 32x32 and organized based on a grid
    def __init__(self, grid_col: int, grid_row: int):
        super().__init__()
        self.surf = pygame.Surface((self.SIZE, self.SIZE))
        self.surf.fill(self.COLOR)
        self.rect = self.surf.get_rect(
            top = grid_row * self.SIZE,
            left = grid_col * self.SIZE,
        )

    @classmethod
    def generate(cls, n: int) -> None:
        for blk in cls.group():
            blk.kill()
        while len(cls.group()) < n:
            blk = cls(
                random.randrange(SCREEN_WIDTH // cls.SIZE),
                random.randrange(SCREEN_HEIGHT // cls.SIZE),
            )
            MySprite.group().remove(blk)
            if blk.rect.collidelist(MySprite.rects()) == -1:
                MySprite.group().add(blk)
            else:
                blk.kill()


def draw_hud(player: Player) -> None:
    text_top = HUD_VERT_MARGIN
    for line in HUD_TEXT:
        formatted_line = line.format(
            centerx=player.rect.centerx,
            centery=player.rect.centery,
            vx=player.vx,
            vy=player.vy,
        )
        font_surf = HUD_FONT.render(formatted_line, True, HUD_TEXT_COLOR)
        screen.blit(font_surf, (HUD_HORZ_MARGIN, text_top))
        text_top += font_surf.get_height() + HUD_LINE_SPACING


def loop() -> None:
    global frames

    Block.generate(50)

    player = Player(center=(random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT // 3)))

    while True:
        # get events
        for e in pygame.event.get():
            if e.type == QUIT:
                return 
            elif e.type == KEYDOWN and e.key in QUIT_KEYS:
                return

        pressed_keys = pygame.key.get_pressed()

        # update
        alive = player.update(frames, pressed_keys)
        if not alive:
            return
        for bl in Bullet.group():
            bl.update()

        # draw
        screen.fill(BG_COLOR)
        draw_hud(player)
        for spr in MySprite.group():
            spr.draw(screen)
        pygame.display.flip()

        # tick
        frames += 1
        clock.tick(FPS)


def main() -> None:
    print('', *INSTRUCTIONS_TEXT, '', sep='\n')
    loop()
    print('Game over.')
    pygame.quit()

if __name__ == '__main__':
    main()