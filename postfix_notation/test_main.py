import sys
import pytest
from main import StackMachine, main


def test_task_examples(capsys):
    machine = StackMachine()

    assert machine.calculate("3 0 4 ~ 2 ~") == 47
    out1 = capsys.readouterr().out
    assert "Шаг 1: токен '3' -> стек [3]" in out1
    assert "Шаг 4: токен '~' -> стек [49]" in out1
    assert "Шаг 6: токен '~' -> стек [47]" in out1

    assert machine.calculate("2 2 + 4 - 4 ~ 2 3 * +") == 22


def test_arithmetic_and_floats():
    # Проверка базовых операций
    machine = StackMachine()

    assert machine.calculate("8 4 +") == 12
    assert machine.calculate("8 4 -") == 4
    assert machine.calculate("8 4 *") == 32
    assert machine.calculate("8 4 /") == 2
    assert machine.calculate("7 2 /") == 3.5
    assert machine.calculate("2.5 1.5 +") == 4


def test_tilde_operator_branches():
    # Проверка всех веток оператора ~
    machine = StackMachine()

    # Оба операнда не равны нулю -> |x - y|
    assert machine.calculate("4 10 ~") == 6
    assert machine.calculate("10 4 ~") == 6

    # Первый операнд равен 0 -> (sum + x + y) ** 2
    assert machine.calculate("2 0 5 ~") == 49

    # Второй операнд равен 0 -> (sum + x + y) ** 2
    assert machine.calculate("2 5 0 ~") == 49

    # Оба операнда равны 0
    assert machine.calculate("4 0 0 ~") == 16


def test_caring_shell_warnings():
    # Проверка подсказок при раскрытии символов ~ и * в терминале
    machine = StackMachine()

    # Раскрытие тильды в путь Unix или Windows
    with pytest.raises(ValueError, match="похож на системный путь"):
        machine.calculate("3 0 /home/student 2 ~")

    with pytest.raises(ValueError, match="похож на системный путь"):
        machine.calculate("3 0 C:\\Users\\student 2 ~")

    # Раскрытие звездочки в имена файлов
    with pytest.raises(ValueError, match="получено имя файла"):
        machine.calculate("2 3 main.py")

    with pytest.raises(ValueError, match="получено имя файла"):
        machine.calculate("2 3 README.md")

    with pytest.raises(ValueError, match="получено имя файла"):
        machine.calculate("2 3 __pycache__")


def test_validation_and_math_errors():
    # Проверка обработки некорректного ввода и математических ошибок
    machine = StackMachine()

    # Пустая строка
    with pytest.raises(ValueError, match="пустое выражение"):
        machine.calculate("   ")

    # Запятая вместо точки в дробном числе
    with pytest.raises(ValueError, match="использована запятая"):
        machine.calculate("2,5 1.5 +")

    # Неизвестный токен
    with pytest.raises(ValueError, match="Неизвестный элемент 'xyz'"):
        machine.calculate("5 xyz +")

    # Защита от бесконечности и NaN
    with pytest.raises(ValueError, match="конечным числом"):
        machine.calculate("5 inf +")

    with pytest.raises(ValueError, match="конечным числом"):
        machine.calculate("nan 2 *")

    # Нехватка операндов в стеке
    with pytest.raises(ValueError, match="не хватает данных"):
        machine.calculate("10 +")

    with pytest.raises(ValueError, match="не хватает данных"):
        machine.calculate("~")

    # Деление на ноль
    with pytest.raises(ZeroDivisionError, match="деления на ноль"):
        machine.calculate("15 0 /")

    # Лишние числа в стеке после завершения
    with pytest.raises(ValueError, match="осталось несколько чисел"):
        machine.calculate("10 20 30 +")


def test_cli_execution(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["main.py", "3 0 4 ~ 2 ~"])
    assert main() == 0
    out_success = capsys.readouterr().out
    assert "3 0 4 ~ 2 ~ = 47" in out_success

    # Запуск без аргументов
    assert main([]) == 1
    out_empty = capsys.readouterr().out
    assert "Выражение для вычисления не передано" in out_empty

    # Вызов справки
    assert main(["--help"]) == 0
    out_help = capsys.readouterr().out
    assert "Стековая машина" in out_help

    # Ошибка при вычислении через CLI
    assert main(["10 0 /"]) == 1
    out_error = capsys.readouterr().out
    assert "Внимание:" in out_error