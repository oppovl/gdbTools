import gdb


# TODO форматировать вывод (отступы и прочее), чтобы ничего не съезжало
class GdbPrinter:
    """Базовый класс для вывода в GDB"""
    
    def __init__(self, prefix="", color_enabled=True):
        self.prefix = prefix
        self.color_enabled = color_enabled
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'reset': '\033[0m'
        }
    
    def _colorize(self, text, color):
        """Добавляет цвет к тексту если включено"""
        if self.color_enabled and color in self.colors:
            return f"{self.colors[color]}{text}{self.colors['reset']}"
        return text
    
    def print(self, *args, **kwargs):
        """Основной метод вывода"""
        color = kwargs.pop('color', None)
        sep = kwargs.pop('sep', ' ')
        end = kwargs.pop('end', '\n')
        
        # Формируем строку
        message = sep.join(str(arg) for arg in args)
        if self.prefix:
            message = f"{self.prefix}{message}"
        
        # Добавляем цвет если указан
        if color:
            message = self._colorize(message, color)
        
        # Выводим в GDB
        gdb.write(message + end)
    
    def info(self, *args, **kwargs):
        """Вывод информационного сообщения"""
        self.print(*args, color='green', **kwargs)
    
    def warning(self, *args, **kwargs):
        """Вывод предупреждения"""
        self.print(*args, color='yellow', **kwargs)
    
    def error(self, *args, **kwargs):
        """Вывод ошибки"""
        self.print(*args, color='red', **kwargs)

    def data(self, *args, **kwargs):
        """Вывод  данных"""
        self.print(*args, color='blue', **kwargs)
    
    def debug(self, *args, **kwargs):
        """Вывод отладочной информации"""
        self.print(*args, color='cyan', **kwargs)
    
    def section(self, *args, **kwargs):
        """Вывод заголовка секции"""
        text = ' '.join(str(arg) for arg in args)
        self.print(f"\n=== {text.upper()} ===", color='bold', **kwargs)
    
    def table_row(self, *columns, widths=None, separator=" | "):
        """Вывод строки таблицы"""
        if widths:
            formatted_columns = []
            for i, col in enumerate(columns):
                if i < len(widths):
                    formatted_columns.append(str(col).ljust(widths[i]))
                else:
                    formatted_columns.append(str(col))
            self.print(separator.join(formatted_columns))
        else:
            self.print(separator.join(str(col) for col in columns))