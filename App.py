from Parser import *
from Prover import *


class App:
    def __init__(self):
        self.axioms = []  # Список для хранения аксиом

    def run(self):
        print("Добро пожаловать!")
        print("Введите 'help' для получения списка доступных команд.")
        print()

        while True:
            user_input = input("> ").strip()

            if user_input.lower() == 'exit':
                print("Завершение работы программы.")
                break
            elif user_input.lower() == 'help':
                self.show_help()
                continue
            elif user_input.lower() == 'axioms':
                self.show_axioms()
                continue

            try:
                # Разделение команды и выражения
                parts = user_input.split(' ', 1)
                command = parts[0].lower()

                if command == 'axiom' and len(parts) > 1:
                    expression_str = parts[1]
                    parser = Parser(expression_str)
                    expression = parser.parse()
                    self.axioms.append(expression)
                    print("Аксиома успешно добавлена:")
                    print()

                elif command == 'prove' and len(parts) > 1:
                    expression_str = parts[1]
                    parser = Parser(expression_str)
                    expression = parser.parse()
                    # TODO: Здесь будет вызов функции доказательства

                else:
                    print("Неизвестная команда или некорректный формат ввода. Введите 'help' для справки.")

            except ValueError as e:
                print(f"Ошибка разбора выражения: {e}")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

            print()

    def show_help(self):
        print("\nСправка по доступным командам:")
        print("- 'axiom <выражение>' : Добавляет аксиому в список.")
        print("- 'prove <выражение>' : Запускает функцию доказательства для введённого выражения.")
        print("- 'help'              : Показывает справку с доступными командами.")
        print("- 'exit'              : Завершает работу программы.\n")

    def show_axioms(self):
        if not self.axioms:
            print("Нет сохранённых аксиом.")
        else:
            print("\nСписок аксиом:")
            for i, expr in enumerate(self.axioms, 1):
                print(f"{i}: {expr.to_string()}")
            print()


# Точка входа в программу
if __name__ == "__main__":
    app = App()
    app.run()
