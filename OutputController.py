class OutputController:
    def __init__(self, file_name='./input.txt'):
        self.file_name = file_name

    def print_formatted_text(self):
        print('=====')
        print(open(self.file_name, 'r').read().strip())
        print('=====')
