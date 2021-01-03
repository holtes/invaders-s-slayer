from random import randrange, choice
import GameObjects
import pygame_menu
import pygame
import os

# Иницилизация pygame
pygame.init()

# Инофрмация об разработчиков
ABOUT = ['Popov Maxim']

# Определение констант

# Цвета
COLOR_BACKGROUND = (255, 104, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
MENU_BACKGROUND_COLOR = (228, 55, 36)


# Выбранная сложность
DIFFICULTY = ""

# Системыне настройки
FPS = 60
WINDOW_SIZE = (1270, 720)

clock = None
main_menu = None
surface = None


def change_difficulty(value, difficulty, debag=False):
    """Изменяет выбранную сложность"""

    if debag:
        selected, index = value
        print(f'Selected difficulty: "{selected}"',
              f'({difficulty}) at index {index}')

    DIFFICULTY[0] = difficulty


#Функция начала игры
def play_function():
    # Define globals
    global main_menu
    global clock
    # Выставление сложности
    difficulty = DIFFICULTY

    # Путь до изображений к игре
    path_from_background = 'Data\\Image\\Map1.png'
    path_from_person = pygame.image.load('Data\\Image\\persona.png')
    path_from_person = pygame.transform.scale2x(path_from_person)
    path_from_zombie = ['Data\\Image\\Zombie.png',
                        'Data\\Image\\Zombie1.png',
                        'Data\\Image\\Zombie2.png',
                        'Data\\Image\\Zombie3.png',
                        'Data\\Image\\Zombie4.png']

    # Изменение игровых коэфицентов в зависимости от сложности
    if difficulty == 'EASY':
        add_hp, add_speed, add_damage = 0.0625, 0.0625, 0.0625
    elif difficulty == 'MEDIUM':
        add_hp, add_speed, add_damage = 0.125, 0.125, 0.125
    else:
        add_hp, add_speed, add_damage = 0.25, 0.25, 0.25

    counter_kill = 0  # Счётчик убийст зомби

    # Иницилизация групп

    # Сюда входят все обьекты кроме игрока и камеры
    all_sprite = pygame.sprite.Group()

    # Сюда входят только видимые обьекты
    visible_objects = pygame.sprite.Group()

    # Сюда входят только выстрелы
    bullet = pygame.sprite.Group()

    # Сюда входят только враги
    enemy = pygame.sprite.Group()

    # Шрифты применяющиеся в игре
    counter = pygame.font.Font(None, 48)  # Для счётчика убийст зомби
    damage_indicator = pygame.font.Font(None, 16)   # Для отображения дамага
    bullet_reload_indicator = pygame.font.Font(None, 48)   # Для отображения дамага
    hp_indicator = pygame.font.Font(None, 48)  # Для отоброжения хп персонажа

    # Добавления Фона
    background = GameObjects.GameObject((0, 0), path_from_background)
    background.set_mask()
    background.disabled_alpha()
    all_sprite.add(background)
    visible_objects.add(background)

    # Добавления игрока
    person = GameObjects.Person((900, 900), path_from_person, hp=10000, speed_move=(600, 600))
    visible_objects.add(person)

    # Добавление границ
    wall_up = GameObjects.EmptyObject((0, 0), (WINDOW_SIZE[0] + 1, 1))
    wall_botton = GameObjects.EmptyObject((0, WINDOW_SIZE[1] - 1), (WINDOW_SIZE[0] + 1, 1))
    wall_left = GameObjects.EmptyObject((0, 0), (1, WINDOW_SIZE[1] + 1))
    wall_right = GameObjects.EmptyObject((WINDOW_SIZE[0] - 1, 0), (1, WINDOW_SIZE[1] + 1))

    # Создание камеры
    camera = GameObjects.TargetCamera(all_sprite, person,
                                      traffic_restriction=background.get_size(),
                                      flags=pygame.FULLSCREEN | pygame.HWSURFACE)
    # Поялучаем экран камеры
    screen = camera.get_screen()
    # Регулятор FPS
    clock = pygame.time.Clock()
    # Переменная отвечающая за паузу
    pause = False

    # Счетчик выстрелов
    counter_shot = 0
    # Основной цикл игры
    command_exit = False
    while not command_exit and person.get_hp() > 0:
        screen.fill((0, 0, 0))  # Избавление от шлейфов

        # Обрабатываем нажаните клавишь
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # По нажатию на кнопки выхода выход
                command_exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Если нажата, остановка игры
                    pause = not pause
                if event.key == pygame.K_z:  # Если нажата +100 к счётчику
                    counter_kill += 100
                elif event.key == pygame.K_g:  # Если нажата, обнуляет счётчик
                    counter_kill = 0

        if not pause:
            # Получаем всё нажатые клавиши
            keys = pygame.key.get_pressed()
            buttons = pygame.mouse.get_pressed()

            # Обрабатываем все удержанные клавиши
            x, y = 0, 0
            if keys[pygame.K_d]:
                x += 1
            if keys[pygame.K_a]:
                x -= 1
            if keys[pygame.K_w]:
                y -= 1
            if keys[pygame.K_s]:
                y += 1
            if buttons[0]:
                if not counter_shot % 2:
                    try:
                        person.shoot().add(all_sprite, visible_objects, bullet)
                    except:
                        pass

            if counter_shot == 999:
                counter_shot = 0

            counter_shot += 1

            # Определяем столкновение персонажа с границами
            top, botton, left, right = True, True, True, True
            if pygame.sprite.collide_rect(person, wall_up):
                top = False
            if pygame.sprite.collide_rect(person, wall_botton):
                botton = False
            if pygame.sprite.collide_rect(person, wall_left):
                left = False
            if pygame.sprite.collide_rect(person, wall_right):
                right = False

            # Устанавливаем куда персонаж не может ходить
            person.set_ability_move(top=top, botton=botton, left=left, right=right)

            # Двигаем камеру с персонажем
            camera.sled((x, y))

            # Обнавление всех обьектов
            person.update()
            all_sprite.update()

            # Добавляем зомби если их < 100
            if len(enemy) < 30:
                pos_spanw_x = randrange(-200, WINDOW_SIZE[0] * 1.5)
                if 0 < pos_spanw_x < WINDOW_SIZE[0]:
                    pos_spanw_y = -200 if randrange(2) else WINDOW_SIZE[1] * 1.5
                else:
                    pos_spanw_y = randrange(-200, WINDOW_SIZE[1] * 1.5)

                GameObjects.Enemy((pos_spanw_x, pos_spanw_y), choice(path_from_zombie), speed_move=randrange(100, round(101 + counter_kill * add_speed)),
                    target=person,
                    damage=randrange(1, round(2 + counter_kill * add_damage)),
                    rotate=(1, lambda: person.get_rect().center),
                    hp=randrange(1, round(2 + counter_kill * add_hp))).add(all_sprite, visible_objects, enemy)

            # Изменяем скорость персанажу в зависимости от убитых зомби
            person.edit_speed_move(round(600 + (counter_kill ** 0.5)))

            # Обработка столкновение зомби с персонажем
            for enem in pygame.sprite.spritecollide(person, enemy, False, collided=pygame.sprite.collide_rect):
                if pygame.sprite.collide_mask(person, enem):
                    person.hit(enem.get_damage())
                    pos = person.get_rect().center
                    indicator = GameObjects.GameObject(
                        (pos[0] + randrange(25), pos[1] + randrange(25)),
                        path_image=damage_indicator.render(
                            str(-enem.get_damage()), True, (255, 255, 0)),
                        time_life=10)
                    indicator.add(all_sprite, visible_objects)

            # Обработка пуль с зомби
            for bull, enem in pygame.sprite.groupcollide(bullet, enemy, False, False).items():
                for enemys in enem:
                    if pygame.sprite.collide_mask(bull, enemys):
                        enemys.hit(bull.get_damage())
                        pos = enemys.get_rect().center
                        indicator = GameObjects.GameObject((pos[0] + randrange(25), pos[1] + randrange(25)), path_image=damage_indicator.render(str(-enemys.get_damage()), True, (255, 0, 0)), time_life=10)
                        indicator.add(all_sprite, visible_objects)
                        if randrange(4):
                            bull.kill()
                        if not enemys.get_hp():
                            counter_kill += 1

        # Отрисовка всех элементов на экране
        visible_objects.draw(screen)
        xol = counter.render(f"Всего убито: {counter_kill}", True, [0, 0, 0])
        screen.blit(xol, (0, 0))
        xol = hp_indicator.render(f"Hp: {person.get_hp()}", True, [255, 0, 255])
        screen.blit(xol, (1700, 1000))
        bul = bullet_reload_indicator.render(f"Bullet: {60 - person.count}", True, [255, 0, 255])
        screen.blit(bul, (1700, 70))
        clock.tick(FPS)
        pygame.display.flip()

    pygame.display.flip()

    main()
    pygame.mixer.music.play(True)
    return


if __name__ == '__main__':
    main()