from Parser import *
from Prover import *


class App:
    def __init__(self):
        self.axioms = []  # Список для хранения аксиом
        self.keywords = ['exit', 'help', 'axioms', 'axiom', 'prove', 'del']

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
                    parser = Parser(expression_str, self.keywords)
                    expression = parser.parse()
                    self.axioms.append(expression)
                    print(f"Аксиома {expression} успешно добавлена!")
                    print()

                elif command == "del" and len(parts) > 1:
                    for_del_str = parts[1]
                    parser = Parser(for_del_str, self.keywords)
                    for_del = parser.parse()
                    for i in range(len(self.axioms)):
                        if self.axioms[i] == for_del:
                            self.axioms.pop(i)
                            print(f"Аксиома удалена: {for_del}")

                elif command == 'prove' and len(parts) > 1:
                    expression_str = parts[1]
                    parser = Parser(expression_str, self.keywords)
                    expression = parser.parse()
                    prover = Prover(self.axioms, expression)
                    result = prover.prove()
                    if result:
                        print(f"Выражение {expression} успешно доказано :)")
                        print()
                        continue
                    else:
                        print(f"Выражение не доказуемо :(")
                        print()
                        continue

                else:
                    print("Неизвестная команда или некорректный формат ввода. Введите 'help' для справки.")

            except ValueError as e:
                print(f"Ошибка разбора выражения: {e}")
            except Exception as e:
                print(f"Произошла ошибка: {e}")

            print()

    @staticmethod
    def show_help():
        print("\nСправка по доступным командам:")
        print("- 'axiom <выражение>' : Добавляет аксиому в список.")
        print("- 'del <выражение>'   : Удаляет аксиому из списка.")
        print("- 'prove <выражение>' : Запускает функцию доказательства для введённого выражения.")
        print("- 'help'              : Показывает справку с доступными командами.")
        print("- 'exit'              : Завершает работу программы.\n")

    def show_axioms(self):
        if not self.axioms:
            print("Нет сохранённых аксиом.\n")
        else:
            print("\nСписок аксиом:")
            for i, expr in enumerate(self.axioms, 1):
                print(f"{i}: {expr.to_string()}")
            print()
