import pygame


class MySprite(pygame.sprite.Sprite):
    surf: pygame.Surface
    rect: pygame.Rect

    __group = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.__group.add(self)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.surf, self.rect)

    @classmethod
    def group(cls) -> pygame.sprite.Group:
        return cls.__group

    @classmethod
    def rects(cls) -> list[pygame.Rect]:
        return [spr.rect for spr in cls.__group]


class MovableSprite(MySprite):
    vx: float
    vy: float

    def __init__(self, vx: int | float = 0, vy: int | float = 0):
        super().__init__()
        self.vx = float(vx)
        self.vy = float(vy)

    def move(self) -> None:
        self.rect.move_ip(self.vx, self.vy)

    def move_x(self) -> None:
        self.rect.move_ip(self.vx, 0)

    def move_y(self) -> None:
        self.rect.move_ip(0, self.vy)

    def handle_solid_collision_x(self) -> None:
        collided_blocks = [blk for blk in SolidBlock.group() if self.rect.colliderect(blk.rect)]
        if self.vx < 0:
            blocks_collided_on_right = [blk for blk in collided_blocks if blk.rect.centerx < self.rect.centerx]
            if blocks_collided_on_right:
                self.vx = 0
                collided_block_right = max(blk.rect.right for blk in blocks_collided_on_right)
                self.rect.left = collided_block_right
        elif self.vx > 0:
            blocks_collided_on_left = [blk for blk in collided_blocks if blk.rect.centerx > self.rect.centerx]
            if blocks_collided_on_left:
                self.vx = 0
                collided_block_left = min(blk.rect.left for blk in blocks_collided_on_left)
                self.rect.right = collided_block_left

    def handle_solid_collision_y(self) -> None:
        collided_blocks = [blk for blk in SolidBlock.group() if self.rect.colliderect(blk.rect)]
        if self.vy < 0:
            blocks_collided_on_bottom = [blk for blk in collided_blocks if blk.rect.centery < self.rect.centery]
            if blocks_collided_on_bottom:
                self.vy = 0
                collided_block_bottom = max(blk.rect.bottom for blk in blocks_collided_on_bottom)
                self.rect.top = collided_block_bottom
        elif self.vy > 0:
            blocks_collided_on_top = [blk for blk in collided_blocks if blk.rect.centery > self.rect.centery]
            if blocks_collided_on_top:
                self.vy = 0
                collided_block_top = min(blk.rect.top for blk in blocks_collided_on_top)
                self.rect.bottom = collided_block_top


class FallableSprite(MovableSprite):
    GRAVITY: float
    TERMINAL_VELOCITY: float

    on_ground: bool = False

    def fall(self) -> None:
        if self.vy < self.TERMINAL_VELOCITY:
            self.vy += self.GRAVITY
        else:
            self.vy = self.TERMINAL_VELOCITY

    def handle_solid_collision_y(self) -> None:
        collided_blocks = [blk for blk in SolidBlock.group() if self.rect.colliderect(blk.rect)]
        if self.vy < 0:
            self.on_ground = False
            blocks_collided_on_bottom = [blk for blk in collided_blocks if blk.rect.centery < self.rect.centery]
            if blocks_collided_on_bottom:
                self.vy = 0
                collided_block_bottom = max(blk.rect.bottom for blk in blocks_collided_on_bottom)
                self.rect.top = collided_block_bottom
        elif self.vy > 0:
            blocks_collided_on_top = [blk for blk in collided_blocks if blk.rect.centery > self.rect.centery]
            if blocks_collided_on_top:
                self.vy = 0
                self.on_ground = True
                collided_block_top = min(blk.rect.top for blk in blocks_collided_on_top)
                self.rect.bottom = collided_block_top
            else:
                self.on_ground = False


class SolidBlock(MySprite):
    __group = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.__group.add(self)

    @classmethod
    def group(cls) -> pygame.sprite.Group:
        return cls.__group

    @classmethod
    def rects(cls) -> list[pygame.Rect]:
        return [blk.rect for blk in cls.__group]