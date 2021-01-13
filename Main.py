import sqlite3
from random import randrange, choice
import GameObjects
import pygame_menu
import pygame
import os
from datetime import datetime, timedelta

# Иницилизация pygame
pygame.init()

# Инофрмация о разработчике
ABOUT = ['Popov Maxim']

# Определение констант

# Цвета
COLOR_BACKGROUND = (255, 104, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
MENU_BACKGROUND_COLOR = (40, 40, 40)

# курсор
MANUAL_CURSOR = pygame.image.load('Data\\Image\\scope.png')

# Системыне настройки
FPS = 60
WINDOW_SIZE = (1270, 720)
FULLSCREEN = pygame.display.Info()

# Назначение глобальных переменных
clock = None
main_menu = None
surface = None
cursor_angle = 2
# Выбранная сложность
difficulty = "EASY"
screen_size = (1280, 1024)


# Функция начала игры
def play_function():
    # Define globals
    global clock
    global cursor_angle
    global difficulty
    global screen_size

    flag = True
    pause_time = timedelta()
    delta_quit = timedelta()
    time_now = datetime.now()
    con = sqlite3.connect('records.db')
    cur = con.cursor()
    pygame.mouse.set_visible(False)
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
    bullet_reload_indicator = pygame.font.Font(None, 48)   # Для отображения перезарядки
    hp_indicator = pygame.font.Font(None, 48)  # Для отоброжения хп персонажа

    # Добавления Фона
    background = GameObjects.GameObject((0, 0), path_from_background)
    background.set_mask()
    background.disabled_alpha()
    all_sprite.add(background)
    visible_objects.add(background)

    # Добавления игрока
    person = GameObjects.Person((900, 900), path_from_person, hp=1000, speed_move=(600, 600))
    visible_objects.add(person)

    # Добавление границ
    wall_up = GameObjects.EmptyObject((0, 0), (screen_size[0] + 1, 1))
    wall_botton = GameObjects.EmptyObject((0, screen_size[0] - 1), (screen_size[0] + 1, 1))
    wall_left = GameObjects.EmptyObject((0, 0), (1, screen_size[1] + 1))
    wall_right = GameObjects.EmptyObject((screen_size[1] - 1, 0), (1, screen_size[1] + 1))

    # Создание камеры
    camera = GameObjects.TargetCamera(all_sprite, person,
                                      traffic_restriction=background.get_size(),
                                      size=screen_size)
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
                delta = datetime.now() - time_now - delta_quit
                result = cur.execute(f"""INSERT INTO records(rec) VALUES('{delta.seconds}') """)
                con.commit()
                command_exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Если нажата, остановка игры
                    if not pause:
                        pause_time = datetime.now()
                    else:
                        delta_pause = pause_time - datetime.now()
                    pause = not pause
                if event.key == pygame.K_z:  # Если нажата, выход в меню
                    delta = datetime.now() - time_now - delta_quit
                    result = cur.execute(f"""INSERT INTO records(rec) VALUES('{delta.seconds}') """)
                    con.commit()
                    command_exit = True

        if not pause:
            # Получаем всё нажатые клавиши
            keys = pygame.key.get_pressed()
            buttons = pygame.mouse.get_pressed()
            try:
                delta_quit += delta_pause
            except:
                pass
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

            # Добавляем зомби если их < 30
            if len(enemy) < 30:
                pos_spanw_x = randrange(-200, screen_size[0] * 1.5)
                if 0 < pos_spanw_x < screen_size[0]:
                    pos_spanw_y = -200 if randrange(2) else screen_size[1] * 1.5
                else:
                    pos_spanw_y = randrange(-200, screen_size[1] * 1.5)

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
                    if person.get_hp() <= 0 and flag:
                        flag = False
                        delta = datetime.now() - time_now - delta_quit
                        result = cur.execute(f"""INSERT INTO records(rec) VALUES('{delta.seconds}') """)
                        con.commit()
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
                        if enemys.get_hp() <= 0:
                            counter_kill += 1

        # Отрисовка всех элементов на экране
        visible_objects.draw(screen)
        xol = counter.render(f"Всего убито: {counter_kill}", True, [0, 0, 0])
        screen.blit(xol, (0, 0))
        hp_ind = hp_indicator.render(f"Hp: {person.get_hp()}", True, [255, 0, 255])
        screen.blit(hp_ind, (screen_size[0] - 200, screen_size[1] - 100))
        bul = bullet_reload_indicator.render(f"Bullet: {60 - person.get_count()}", True, [255, 0, 255])
        screen.blit(bul, (screen_size[0] - 200, 50))
        cursor_angle += 1
        screen.blit(pygame.transform.rotate(MANUAL_CURSOR, cursor_angle), (pygame.mouse.get_pos()))
        clock.tick(FPS)
        pygame.display.flip()

    pygame.display.flip()
    main()
    return


def set_difficulty(value, dif):
    global difficulty
    difficulty = dif


def set_resolution(value, size):
    global screen_size
    global FULLSCREEN
    if size == 'Full Screen':
        screen_size = (FULLSCREEN.current_w, FULLSCREEN.current_h)
    else:
        screen_size = size


def main_background():
    surface.fill(MENU_BACKGROUND_COLOR)


def main():
    global main_menu
    global surface

    # Init pygame
    pygame.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    con = sqlite3.connect('records.db')
    cur = con.cursor()
    result = cur.execute("""SELECT * FROM records""").fetchall()
    # Создание экрана и объектов
    surface = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Invaders slayer - Main menu')
    clock = pygame.time.Clock()

    # Создвние меню Настройки
    settings_menu_theme = pygame_menu.themes.THEME_ORANGE.copy()
    settings_menu_theme.title_offset = (5, -2)
    settings_menu_theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
    settings_menu_theme.widget_font = pygame_menu.font.FONT_OPEN_SANS_LIGHT
    settings_menu_theme.widget_font_size = 20

    # Создание меню Истории
    story_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.85,
        onclose=pygame_menu.events.DISABLE_CLOSE,
        theme=settings_menu_theme,
        title='Story',
        width=WINDOW_SIZE[0] * 0.9,
    )

    story_menu.add_label("1990, исследовательский центр \"Рассвет\":")
    story_menu.add_label("Правительство СССР решает уничтожить все свидетельства ")
    story_menu.add_label("контакта с внеземной цивилизацией. Из-за халатного управления, ")
    story_menu.add_label("процесс по упокоению пришельцев срывается, выпустив их на")
    story_menu.add_label("свободу в окрестностях поселка Косколь в Казахстане. Вы ")
    story_menu.add_label("обычный солдат, оказавшийся в самом пекле совсем один. По еле ")
    story_menu.add_label("живой рации вы слышите последний приказ: \"Держаться до ")
    story_menu.add_label("конца!\" Взяв оставшееся оружие, вы выходите на встречу ")
    story_menu.add_label("опасности, зная, что за вами никто не придёт...")

    settings_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1] * 0.85,
        onclose=pygame_menu.events.DISABLE_CLOSE,
        theme=settings_menu_theme,
        title='Settings',
        width=WINDOW_SIZE[0] * 0.9,
    )
    settings_menu.add_label("Правила:", label_id="rules")
    settings_menu.add_label("Перемещение: WASD")
    settings_menu.add_label("Стрельба: Левая кнопка мыши")
    settings_menu.add_label("Пауза: Esc")
    settings_menu.add_label("Выход в меню: Z")

    # Создание выбора сложности
    settings_menu.add_selector('Select difficulty ',
                               [('Easy', 'EASY'),
                                ('Medium', 'MEDIUM'),
                                ('Hard', 'HARD')],
                               selector_id='difficulty',
                               default=1, onchange=set_difficulty)

    settings_menu.add_selector('Select resolution ',
                               [('600×800', (800, 600)),
                                ('1600×1024', (1600, 1024)),
                                ('1680×1050', (1680, 1050)),
                                ('1920×1080', (1920, 1080)),
                                ('Full Screen', 'Full Screen')],
                               selector_id='screen',
                               default=4, onchange=set_resolution)

    settings_menu.add_button('Return to main menu', pygame_menu.events.BACK,
                             align=pygame_menu.locals.ALIGN_CENTER)

    # Создание главного меню
    main_menu_theme = pygame_menu.themes.THEME_ORANGE.copy()
    main_menu_theme.widget_offset = (0, 0.09)
    main_menu_theme.title_font = pygame_menu.font.FONT_COMIC_NEUE
    main_menu_theme.widget_font = pygame_menu.font.FONT_COMIC_NEUE
    main_menu_theme.widget_font_size = 30

    main_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1],
        width=WINDOW_SIZE[0],
        onclose=pygame_menu.events.EXIT,  # User press ESC button
        title='Main menu',
        theme=main_menu_theme,
    )

    rec_menu = pygame_menu.Menu(
        height=WINDOW_SIZE[1],
        width=WINDOW_SIZE[0],
        onclose=pygame_menu.events.EXIT,  # User press ESC button
        title='Records',
        theme=main_menu_theme,
    )
    maxx = 0
    for elem in result:
        if int(elem[1]) > maxx:
            maxx = int(elem[1])
    high_score = 'Your high score: ' + str(maxx)
    now_score = 'Your previous score: ' + result[len(result) - 1][1]
    rec_menu.add_label(high_score)
    rec_menu.add_label(now_score)

    # Содание кнопок
    main_menu.add_button('Play', play_function, font_size=100)
    main_menu.add_button('Story', story_menu)
    main_menu.add_button('Settings', settings_menu)
    main_menu.add_button('Your records', rec_menu)
    main_menu.add_button('Quit', pygame_menu.events.EXIT)

    # Главный цикл
    while True:
        # Тик
        clock.tick(FPS)

        # Отрисовка заднего фона
        main_background()

        # Главное меню
        main_menu.mainloop(surface, main_background, fps_limit=FPS)

        # Окончательная отрисовка
        pygame.display.flip()


if __name__ == '__main__':
    main()