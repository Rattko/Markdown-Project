import sys


class NoTextException(Exception):
    pass


class InputController:
    def __init__(self, file_name='./input.txt'):
        self.file_name = file_name

        self.__create_file()
        self.__clear_file()
        self.__print_intro_message()

    def __create_file(self):
        with open(self.file_name, 'w') as input_file:
            input_file.write('File created.')

    def __clear_file(self):
        with open(self.file_name, 'w') as input_file:
            input_file.write('')

    def __append_to_file(self, line):
        with open(self.file_name, 'a') as input_file:
            input_file.write(line + '\n')

    @staticmethod
    def __print_intro_message():
        print('Enter text in MarkDown format.')
        print('To submit your MarkDown text, enter "Exit". \n')

    def read_user_input(self):
        """
        Try to read the user's input until 'Exit' is entered.

        Raises NoTextException if 'Exit' is entered before anything else.
        Raises KeyboardInterrupt if Ctrl+C is pressed while awaiting input.
        """

        try:
            user_input = input()
            if user_input.lower() == 'exit':
                raise NoTextException()
            while user_input.lower() != 'exit':
                self.__append_to_file(user_input)
                user_input = input()
        except NoTextException:
            print('No Text!', file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(130)
