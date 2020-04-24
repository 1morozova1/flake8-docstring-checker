class Sum:
    '''Класс для суммы чисел.'''

    def sum(self, a: int, b: int) -> int:
        '''Складывает цифры.

        Args:
            a: Первое слагаемое.
            b: Второе слагаемое.
        '''
        return a + b

    def useless(self, x: int) -> int:
        '''Ничего не делает.

        Совсем ничего не делает.

        Args:
            x: Переменная.

        Returns:
            Цифра.
        '''
        return 5

    def boring(self) -> str:
        '''Пишет строчку.

        Returns:
        '''
        return 'I write'
