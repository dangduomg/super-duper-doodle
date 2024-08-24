import pygame

from constants import DATA_DIR, GRAVITY, RLEACCEL, SCREEN_WIDTH, SCREEN_HEIGHT, \
                      LEFT_KEY, RIGHT_KEY, JUMP_KEY, RUN_KEY, SHOOT_KEY
from sprites import FallableSprite, MovableSprite, MySprite, SolidBlock


class Player(FallableSprite):
    IDLE_IMAGE_PATH = DATA_DIR / 'small mario idle.png'
    MOVING_IMAGE_PATH = DATA_DIR / 'small mario moving.png'
    JUMP_IMAGE_PATH = DATA_DIR / 'small mario jumping.png'
    IMAGE_COLORKEY = 221, 91, 249

    WALK_SPEED = 4
    RUN_SPEED = 8
    ACCEL = 0.5
    JUMP_SPEED = 16
    GRAVITY = GRAVITY
    TERMINAL_VELOCITY = 16

    HOLD_SHOOT_DELAY = 30

    def __init__(self, **rect_options):
        super().__init__()
        
        image_idle_right_unscaled = pygame.image.load(self.IDLE_IMAGE_PATH)
        self.image_idle_right = pygame.transform.scale_by(image_idle_right_unscaled, 2).convert()
        self.image_idle_right.set_colorkey(self.IMAGE_COLORKEY, RLEACCEL)
        self.image_idle_left = pygame.transform.flip(self.image_idle_right, True, False)

        image_moving_right_unscaled = pygame.image.load(self.MOVING_IMAGE_PATH)
        self.image_moving_right = pygame.transform.scale_by(image_moving_right_unscaled, 2).convert()
        self.image_moving_right.set_colorkey(self.IMAGE_COLORKEY, RLEACCEL)
        self.image_moving_left = pygame.transform.flip(self.image_moving_right, True, False)

        image_jump_right_unscaled = pygame.image.load(self.JUMP_IMAGE_PATH)
        self.image_jump_right = pygame.transform.scale_by(image_jump_right_unscaled, 2).convert()
        self.image_jump_right.set_colorkey(self.IMAGE_COLORKEY, RLEACCEL)
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, True, False)

        self.surf = self.image_idle_right
        self.rect = self.surf.get_rect(**rect_options)

        self.direction = 1
        self.moving = False
        self.running = False
        self.on_ground = False

        self.moving_start_frame = -1
        self.moving_animation_frame_i = 0

        self.shooting_start_frame = -1

    def update(self, frames, pressed_keys: dict[int, bool]) -> None:
        self.handle_shoot(frames, pressed_keys)
        self.handle_horz_move(pressed_keys)
        self.move_x()
        self.handle_solid_collision_x()
        if pressed_keys[JUMP_KEY] and self.on_ground:
            self.vy = -self.JUMP_SPEED
        self.fall()
        self.move_y()
        self.handle_solid_collision_y()
        self.handle_edge()   
        self.set_image(frames)
        return True

    def handle_shoot(self, frames: int, pressed_keys: dict[int, bool]) -> None:
        if pressed_keys[SHOOT_KEY]:
            if self.shooting_start_frame < 0:
                self.shooting_start_frame = frames
            shooting_frames = (frames - self.shooting_start_frame) % self.HOLD_SHOOT_DELAY
            if shooting_frames == 0:
                Bullet(self.direction, center=self.rect.center)
        else:
            self.shooting_start_frame = -1

    def handle_horz_move(self, pressed_keys: dict[int, bool]) -> None:
        self.running = pressed_keys[RUN_KEY]
        speed = self.RUN_SPEED if self.running else self.WALK_SPEED
        self.moving = False
        if pressed_keys[LEFT_KEY] and not pressed_keys[RIGHT_KEY]:
            self.direction = -1
            self.moving = True
        elif pressed_keys[RIGHT_KEY] and not pressed_keys[LEFT_KEY]:
            self.direction = 1
            self.moving = True
        goal_vx = self.moving * self.direction * speed
        if self.vx < goal_vx:
            self.vx += self.ACCEL
        elif self.vx > goal_vx:
            self.vx -= self.ACCEL

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
            self.on_ground = False
            blocks_collided_on_bottom = [blk for blk in collided_blocks if blk.rect.centery < self.rect.centery]
            if blocks_collided_on_bottom:
                self.vy = 0
                collided_block_bottom = max(blk.rect.bottom for blk in blocks_collided_on_bottom)
                self.rect.top = collided_block_bottom
        elif self.vy >= 0:
            blocks_collided_on_top = [blk for blk in collided_blocks if blk.rect.centery > self.rect.centery]
            if blocks_collided_on_top:
                self.vy = 0
                self.on_ground = True
                collided_block_top = min(blk.rect.top for blk in blocks_collided_on_top)
                self.rect.bottom = collided_block_top
            else:
                self.on_ground = False

    def handle_edge(self) -> None:
        if self.rect.left < 0:
            self.vx = 0
            self.rect.left = 0
        elif self.rect.right >= SCREEN_WIDTH:
            self.vx = 0
            self.rect.right = SCREEN_WIDTH
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.vy = 0
            self.on_ground = True
            self.rect.bottom = SCREEN_HEIGHT

    def handle_jump(self, pressed_keys: dict[int, bool]) -> None:
        if pressed_keys[JUMP_KEY] and self.on_ground:
            self.vy = -self.JUMP_SPEED
            # without this line of code, self.fall() would have prevented the player to jump
            self.rect.move_ip(0, -1)
        elif not pressed_keys[JUMP_KEY]:
            # jump cancelling
            if self.vy < 0:
                self.vy = 0

    def set_image(self, frames: int) -> None:
        if not self.on_ground:
            if self.direction == -1:
                self.surf = self.image_jump_left
            elif self.direction == 1:
                self.surf = self.image_jump_right
        elif self.moving:
            # if player character is walking, alternate between idle and moving sprite every 6 frames
            # if running, every 3 frames
            if self.moving_start_frame < 0:
                self.moving_start_frame = frames
            if self.direction == -1:
                self.moving_animation_frames = self.image_moving_left, self.image_idle_left
            elif self.direction == 1:
                self.moving_animation_frames = self.image_moving_right, self.image_idle_right
            moving_frames = (frames - self.moving_start_frame) % 6
            self.surf = self.curr_moving_animation_frame
            if self.running and moving_frames == 2:
                self.cycle_moving_animation()
            if moving_frames == 5:
                self.cycle_moving_animation()
        else:
            self.moving_start_frame = -1
            self.moving_animation_frame_i = 0
            if self.direction == -1:
                self.surf = self.image_idle_left
            elif self.direction == 1:
                self.surf = self.image_idle_right

    @property
    def curr_moving_animation_frame(self) -> pygame.Surface:
        return self.moving_animation_frames[self.moving_animation_frame_i]

    def cycle_moving_animation(self) -> None:
        self.moving_animation_frame_i = (self.moving_animation_frame_i + 1) % len(self.moving_animation_frames)


class Bullet(MovableSprite):
    IMAGE_PATH = DATA_DIR / 'fireball.png'
    IMAGE_COLORKEY = 160, 208, 248

    SPEED = 10

    __group = pygame.sprite.Group()

    def __init__(self, direction: int, **rect_options):
        super().__init__(vx = direction * self.SPEED, vy=0)
        self.__group.add(self)

        image_unscaled = pygame.image.load(self.IMAGE_PATH)
        self.surf = pygame.transform.scale_by(image_unscaled, 2).convert()
        self.surf.set_colorkey(self.IMAGE_COLORKEY, RLEACCEL)
        self.rect = self.surf.get_rect(**rect_options)

    def update(self) -> None:
        self.move()
        self.handle_collision()
        self.kill_on_edge()

    def handle_collision(self) -> None:
        sprite_list = list(MySprite.group())
        if (i := self.rect.collidelist([spr.rect for spr in sprite_list])) >= 0:
            # create exception for player and bullets themselves
            collided_spr = sprite_list[i]
            if not isinstance(collided_spr, (Player, type(self))):
                self.kill()

    def kill_on_edge(self) -> None:
        if self.rect.right < 0 or self.rect.left >= SCREEN_WIDTH:
            self.kill()

    @classmethod
    def group(cls) -> pygame.sprite.Group:
        return cls.__group