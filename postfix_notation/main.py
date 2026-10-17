import math
import sys


class StackMachine:
    # Стековая машина для пошагового вычисления постфиксных выражений

    OPERATORS = ("+", "-", "*", "/", "~")

    def __init__(self):
        self.stack = []

    @staticmethod
    def _clean_number(value):
        # Превращает дробные числа без дробной части в целые
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    def _parse_operand(self, token):
        # Проверяет токен и переводит его в число с подсказками
        if "/" in token or "\\" in token:
            raise ValueError(
                f"Элемент '{token}' похож на системный путь. "
                "Пожалуйста, возьмите выражение в кавычки, чтобы терминал не раскрывал символ '~'"
            )

        if token.endswith(".py") or token.endswith(".md") or "__pycache__" in token:
            raise ValueError(
                f"Вместо оператора получено имя файла '{token}'. "
                "Пожалуйста, возьмите выражение в кавычки"
            )

        if "," in token:
            raise ValueError(
                f"В записи числа '{token}' использована запятая. "
                "Пожалуйста, используйте точку для дробных чисел (например, 2.5)"
            )

        try:
            number = float(token)
        except ValueError as err:
            raise ValueError(
                f"Неизвестный элемент '{token}'. "
                "Используйте только числа и операторы (+, -, *, /, ~), разделенные пробелами"
            ) from err

        if not math.isfinite(number):
            raise ValueError(
                f"Значение '{token}' не является конечным числом"
            )

        return self._clean_number(number)

    def _apply_operator(self, operator, step):
        # Извлекает два операнда из стека и выполняет операцию
        if len(self.stack) < 2:
            raise ValueError(
                f"На шаге {step} для операции '{operator}' не хватает данных "
                f"(в стеке сейчас {self.stack}, а нужно минимум 2 числа)"
            )

        y = self.stack.pop()
        x = self.stack.pop()

        if operator == "+":
            result = x + y
        elif operator == "-":
            result = x - y
        elif operator == "*":
            result = x * y
        elif operator == "/":
            if y == 0:
                raise ZeroDivisionError(
                    f"На шаге {step} произошла попытка деления на ноль ({x} / 0). "
                    "Делить на ноль нельзя"
                )
            result = x / y
        else:  # Оператор '~'
            if x == 0 or y == 0:
                total = sum(self.stack) + x + y
                self.stack.clear()
                result = total ** 2
            else:
                result = abs(x - y)

        self.stack.append(self._clean_number(result))

    def calculate(self, expression):
        # Вычисляет выражение и выводит состояние стека на каждом шаге
        tokens = expression.split()
        if not tokens:
            raise ValueError(
                'Передано пустое выражение. Введите числа и операторы, например: "3 0 4 ~ 2 ~"'
            )

        self.stack.clear()

        for step, token in enumerate(tokens, start=1):
            if token in self.OPERATORS:
                self._apply_operator(token, step)
            else:
                self.stack.append(self._parse_operand(token))

            print(f"Шаг {step}: токен '{token}' -> стек {self.stack}")

        if len(self.stack) != 1:
            raise ValueError(
                f"Вычисление завершено, но в стеке осталось несколько чисел: {self.stack}. "
                "Проверьте выражение — возможно, вы пропустили оператор"
            )

        return self.stack[0]


def print_usage():
    # Выводит справку по использованию программы
    print(
        "Стековая машина\n\n"
        "Использование:\n"
        '  python main.py "<выражение>"\n'
        "  python main.py --help\n\n"
        "Доступные операции:\n"
        "  + , - , * , /  — стандартные арифметические действия\n"
        "  ~              — модуль разницы |x - y| (если оба != 0) или квадрат суммы\n"
        "                   всех чисел в стеке, включая извлеченные операнды (если есть 0)\n\n"
        "Примеры запуска:\n"
        '  python main.py "3 0 4 ~ 2 ~"\n'
        '  python main.py "2 2 + 4 - 4 ~ 2 3 * +"'
    )


def main(argv=None):
    # Точка входа для работы через командную строку
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print("Выражение для вычисления не передано\n")
        print_usage()
        return 1

    if "-h" in args or "--help" in args:
        print_usage()
        return 0

    expression = " ".join(args).strip()
    machine = StackMachine()

    try:
        result = machine.calculate(expression)
        print(f"{expression} = {result}")
        return 0
    except (ValueError, ZeroDivisionError) as error:
        print(f"Внимание: {error}")
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())