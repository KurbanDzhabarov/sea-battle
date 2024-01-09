from random import randint, choice


class BoardOutException(Exception):
    """Класс исключения, например, когда игрок пытается выстрелить в клетку за пределами поля"""
    def __init__(self):
        pass

    def __str__(self):
        return "Точка за пределами поля"


class CantcreateboardException(Exception):
    """Класс исключения, например, когда не удалось создать доску после всех попыток"""
    def __init(self):
        pass

    def __str__(self):
        return "Не удалось создать доску"


class Dot:
    """класс точек на поле"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        """переопределяем метод сравнения двух объектов класса Dot"""
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"{self.x},{self.y}"

    def __hash__(self):
        return hash(str(self))

    def neighbors(self):
        """метод соседних точек"""
        return [Dot(self.x+x, self.y+y) for y in range(-1, 2) for x in range(-1, 2)]


class Ship:
    """корабль на игровом поле, имеет поля: длина, колличество жизней, точка начала корабля, направление корабля"""
    def __init__(self, length, start, direction):
        self.length = length
        self.hp = length
        self.start = start
        self.direction = direction

    def dots(self):
        """возвращает список всех точек корабля"""
        x = self.start.x
        y = self.start.y
        if self.direction == "horizontal":
            return [Dot(x+i, y) for i in range(self.length)]
        else:
            return [Dot(x, y+i) for i in range(self.length)]


class Board:
    """класс — игровая доска. Доска описывается параметрами:
    1. Двумерный список, в котором хранятся состояния каждой из клеток.
    2. Список кораблей доски.
    3. Параметр hid типа bool — информация о том, нужно ли скрывать корабли на доске (для вывода доски врага)
    или нет (для своей доски).
    4. Количество живых кораблей на доске.
    5. Добавляем словарь mask для замены символов на доске, в случае, если это доска противника"""
    def __init__(self, hide=False):
        self.hid = hide
        self.cels = [["0" for i in range(6)] for j in range(6)]
        self.free_cels = [Dot(x, y) for x in range(6) for y in range(6)]
        self.marker_cels = []
        self.ships = []
        self.ships_count = 0
        self.last_ship = None
        self.mask = {"0": "?",
                     "■": "?"}

    def out(self, dot: Dot):
        """если координаты точки не в доске - вернет True"""
        return not (dot.x in range(6) and dot.y in range(6))

    def add_ship(self, ship: Ship):
        """Метод, который ставит корабль на доску"""
        if all(map(lambda x: x in self.free_cels, ship.dots())):
            self.ships.append(ship)
            self.ships_count += 1
            for dot in ship.dots():
                self.cels[dot.y][dot.x] = "■"
            self.contour(ship)

        else:
            raise CantcreateboardException

    def __str__(self):
        result = "   A|B|C|D|E|F\n"
        i = 1
        if not self.hid:
            for line in self.cels:
                result += f"{i} |" + "|".join(line) + "\n"
                i += 1
        else:
            for line in self.cels:
                result += f"{i} |" + "|".join(map(lambda x: self.mask[x] if x in self.mask else x, line)) + "\n"
                i += 1

        return result

    def contour(self, ship: Ship):
        dots = set()
        for dot in ship.dots():
            dots.update(dot.neighbors())

        for dot in dots:
            if not self.out(dot) and dot in self.free_cels:
                self.marker_cels.append(dot)
                self.free_cels.remove(dot)
        return dots.difference(set(ship.dots()))
    def shoot(self, dot: Dot):
        if self.out(dot):
            raise BoardOutException
        else:
            if self.cels[dot.x][dot.y] == "■":
                self.cels[dot.x][dot.y] = "X"
                for ship in self.ships:
                    if dot in ship.dots():
                        ship.hp -= 1
                        if ship.hp == 0:
                            self.ships.remove(ship)
                            self.ships_count -= 1
                            self.last_ship = ship
                            print("Ты потопил корабль!")


                return True

            else:
                self.cels[dot.x][dot.y] = "*"
                return False


class Player:
    """Родительский класс - игрок"""
    def __init__(self, my_board: Board, enemy_board: Board):
        self.my_board = my_board
        self.enemy_board = enemy_board
        self.shoot_cels = []

    def ask(self):
        """переопределять метод ask будем в классе - наследнике"""
        pass

    def move(self):
        dot = self.ask()
        try:
            ships_count = self.enemy_board.ships_count
            if self.enemy_board.shoot(dot):
                print("Есть пробитие, сделай еще ход!")
                if ships_count != self.enemy_board.ships_count:
                    self.shoot_cels += list(self.enemy_board.contour(self.enemy_board.last_ship))
                return True
        except BoardOutException:
            print("Ты указал точку за пределами поля, сделай ход заново!")
            return True
        return False


class Ai(Player):
    """Класс - наследник класса игрок. Представляет компьютер"""


    def ask(self):
        x = randint(0, 5)
        y = randint(0, 5)
        while Dot(x, y) in self.shoot_cels:
            x = randint(0, 5)
            y = randint(0, 5)

        self.shoot_cels.append(Dot(x, y))
        return Dot(x, y)


class User(Player):
    """Класс - наследник класса игрок. Представляет игрока"""
    def ask(self):
        while True:
            a = input("Введите ход (например A1, B3): ").upper()
            board_dict = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}
            try:
                if len(a) < 2 or a[0] not in "ABCDEF" or int(a[1]) not in range(1, 7):
                    print("Вы ввели неверный ход, попробуйте снова!")
                else:

                    x = board_dict[a[0]]
                    y = int(a[1:]) - 1
                    break
            except ValueError:
                print("Вы ввели неверный ход, попробуйте снова!")
        return Dot(y, x)


class Game:
    """Класс игры. Описывается параметрами:
Игрок-пользователь, объект класса User.
Доска пользователя.
Игрок-компьютер, объект класса AI.
Доска компьютера"""
    def __init__(self):
        self.user_board = Board()
        self.ai_board = Board(hide=True)
        self.user = User(self.user_board, self.ai_board)
        self.ai = Ai(self.ai_board, self.user_board)

    def greet(self):
        print("Это игра Морской бой, добро пожаловать!")

    def random_board(self, target_board: Board):
        ships = [3, 2, 2, 1, 1, 1, 1]
        while True:
            if target_board.ships_count < 7 and len(target_board.free_cels) == 0:
                target_board.__init__()
            elif target_board.ships_count == 7:
                break

            for i in ships:
                counter = 0
                while counter < 2000:
                    if len(target_board.free_cels) == 0:
                        break
                    try:
                        new_ship = Ship(i, choice(target_board.free_cels), choice(["horizontal", "vertical"]))
                        target_board.add_ship(new_ship)
                        break
                    except CantcreateboardException:
                        counter += 1

    def loop(self):
        print(self.user_board)
        print(self.ai_board)

        while self.user.move():
            print(self.ai_board)
        while self.ai.move():
            print(self.user_board)

        if self.user_board.ships_count == 0:
            print("Победил компьютер!")
        elif self.ai_board.ships_count == 0:
            print("Победил пользователь!")
        else:
            self.loop()

    def start(self):
        self.greet()
        self.random_board(self.user_board)
        self.random_board(self.ai_board)
        self.loop()


if __name__ == "__main__":

    Game().start()
