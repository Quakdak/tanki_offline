import pygame
import sys
import os
import random
import time

clock = pygame.time.Clock()
pygame.init()
size = WIDTH, HEIGHT = 1050, 700
screen = pygame.display.set_mode(size)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
bushes_group = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
shot_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
train_group = pygame.sprite.Group()

FPS = 30

SCORE = 0

font = pygame.font.SysFont("Arial", 30)


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(f'FPS: {fps}', 1, pygame.Color("white"))
    return fps_text


def statistics():
    stata = font.render(f'Очки: {SCORE}', 1, pygame.Color("white"))
    return stata


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


start_screen()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('beton.png'),
    'bush': load_image('leaves.png'),
    'border': pygame.transform.scale(load_image('border.png'), (50, 50)),
    'relsi': load_image('relsi.png'),
    'train': load_image('train.png'),
    'broke_relsi': load_image('broken_relsi.png')
}
low_broke_box_image = load_image('low_broke_box.png')
medium_broke_box_image = load_image('medium_broke_box.png')
hard_broke_box_image = load_image('hard_broke_box.png')
low_broke_train_image = load_image('low_broke_train.png')
medium_broke_train_image = load_image('medium_broke_train.png')
hard_broke_train_image = load_image('hard_broke_train.png')
player_image = load_image('main_tank2.png')
shot_image = load_image('ammo3.png')
enemy_image = load_image('enemy_tank1.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'wall':
            walls_group.add(self)
        if tile_type == 'bush':
            bushes_group.add(self)
        if tile_type == 'border':
            borders_group.add(self)
        if tile_type == 'train':
            train_group.add(self)
        self.health = 100
        self.type = tile_type


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.distinction = "w"

    def change_position(self):
        move = (0, 0)

        if pygame.key.get_pressed()[pygame.K_w]:
            move = (0, -tile_width / 10)
            if self.distinction == "w":
                pass
            elif self.distinction == "s":
                self.image = pygame.transform.rotate(self.image, 180)
            elif self.distinction == "a":
                self.image = pygame.transform.rotate(self.image, 270)
            elif self.distinction == "d":
                self.image = pygame.transform.rotate(self.image, 90)
            self.distinction = "w"

        elif pygame.key.get_pressed()[pygame.K_s]:
            move = (0, tile_width / 10)
            if self.distinction == "w":
                self.image = pygame.transform.rotate(self.image, 180)
            elif self.distinction == "s":
                pass
            elif self.distinction == "a":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.distinction == "d":
                self.image = pygame.transform.rotate(self.image, 270)
            self.distinction = "s"

        if pygame.key.get_pressed()[pygame.K_d]:
            move = (tile_width / 10, 0)
            if self.distinction == "w":
                self.image = pygame.transform.rotate(self.image, 270)
            elif self.distinction == "s":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.distinction == "a":
                self.image = pygame.transform.rotate(self.image, 180)
            elif self.distinction == "d":
                pass
            self.distinction = "d"

        if pygame.key.get_pressed()[pygame.K_a]:
            move = (-tile_width / 10, 0)
            if self.distinction == "w":
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.distinction == "s":
                self.image = pygame.transform.rotate(self.image, 270)
            elif self.distinction == "a":
                pass
            elif self.distinction == "d":
                self.image = pygame.transform.rotate(self.image, 180)
            self.distinction = "a"

        self.rect = self.rect.move(move)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, borders_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, enemy_group):
            self.rect = self.rect.move(-move[0], -move[1])
        if pygame.sprite.spritecollideany(self, train_group):
            self.rect = self.rect.move(-move[0], -move[1])


player = None


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == ',':
                Tile('bush', x, y)
            elif level[y][x] == '%':
                Tile('border', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '!':
                Tile('relsi', x, y)
            elif level[y][x] == '*':
                Tile('train', x, y)
    return new_player, x, y


class Shot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(shot_group, all_sprites)
        self.image = shot_image
        self.rect = self.image.get_rect().move(player.rect.x + 11, player.rect.y + 11)
        if player.distinction == "w":
            self.vy = -10
            self.vx = 0

        elif player.distinction == "a":
            self.vy = 0
            self.vx = -10

        elif player.distinction == "d":
            self.vy = 0
            self.vx = 10

        elif player.distinction == "s":
            self.vy = 10
            self.vx = 0

    def update(self, *args):
        global SCORE
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollide(self, walls_group, False):
            all_sprites.remove(self)
            shot_group.remove(self)
        if pygame.sprite.spritecollide(self, borders_group, False):
            all_sprites.remove(self)
            shot_group.remove(self)
        if pygame.sprite.spritecollide(self, enemy_group, True):
            all_sprites.remove(self)
            shot_group.remove(self)
            SCORE += 100

        if pygame.sprite.spritecollide(self, train_group, False):
            all_sprites.remove(self)
            shot_group.remove(self)

        if pygame.sprite.spritecollideany(self, walls_group):
            pygame.sprite.spritecollideany(self, walls_group).health -= 25

            if pygame.sprite.spritecollideany(self, walls_group).health == 75:
                pygame.sprite.spritecollideany(self, walls_group).image = low_broke_box_image

            if pygame.sprite.spritecollideany(self, walls_group).health == 50:
                pygame.sprite.spritecollideany(self, walls_group).image = medium_broke_box_image

            if pygame.sprite.spritecollideany(self, walls_group).health == 25:
                pygame.sprite.spritecollideany(self, walls_group).image = hard_broke_box_image

            if pygame.sprite.spritecollideany(self, walls_group).health == 0:
                pygame.sprite.spritecollideany(self, walls_group).image = tile_images['empty']
                walls_group.remove(pygame.sprite.spritecollideany(self, walls_group))

        if pygame.sprite.spritecollideany(self, train_group):
            pygame.sprite.spritecollideany(self, train_group).health -= 25

            if pygame.sprite.spritecollideany(self, train_group).health == 75:
                pygame.sprite.spritecollideany(self, train_group).image = low_broke_train_image

            if pygame.sprite.spritecollideany(self, train_group).health == 50:
                pygame.sprite.spritecollideany(self, train_group).image = medium_broke_train_image

            if pygame.sprite.spritecollideany(self, train_group).health == 25:
                pygame.sprite.spritecollideany(self, train_group).image = hard_broke_train_image

            if pygame.sprite.spritecollideany(self, train_group).health == 0:
                pygame.sprite.spritecollideany(self, train_group).image = tile_images['broke_relsi']
                train_group.remove(pygame.sprite.spritecollideany(self, train_group))


def get_coord_for_bot_spawn(new_bot):
    x = random.randint(1, 14)
    y = random.randint(1, 8)
    new_bot.rect.x = tile_width * x
    new_bot.rect.y = tile_width * y
    if enemy_group:
        while pygame.sprite.spritecollideany(new_bot, walls_group) \
                or pygame.sprite.spritecollideany(new_bot, borders_group) \
                or pygame.sprite.spritecollideany(new_bot, player_group):
            x = random.randint(8, 10)
            y = random.randint(2, 3)
            new_bot.rect.x = tile_width * x
            new_bot.rect.y = tile_width * y
    return x, y


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.image = enemy_image
        get_coord_for_bot_spawn(self)
        enemy_group.add(self)


player, level_x, level_y = generate_level(load_level("level1.txt"))

for _ in range(10):
    Enemy()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(shot_group) < 3:
                shot = Shot()
    start_time = time.time()
    player.change_position()
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    player_group.draw(screen)
    shot_group.draw(screen)
    screen.blit(update_fps(), (880, 20))
    screen.blit(statistics(), (880, 60))
    shot_group.update()
    walls_group.update()
    train_group.update()
    enemy_group.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)
