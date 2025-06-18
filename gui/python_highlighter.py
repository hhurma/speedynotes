from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt
import re

class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        # Renk şeması
        self.colors = {
            'keyword': QColor(0, 0, 255),        # Mavi - anahtar kelimeler
            'builtin': QColor(128, 0, 128),      # Mor - built-in fonksiyonlar
            'string': QColor(0, 128, 0),         # Yeşil - string'ler
            'comment': QColor(128, 128, 128),    # Gri - yorumlar
            'number': QColor(255, 0, 0),         # Kırmızı - sayılar
            'operator': QColor(0, 0, 0),         # Siyah - operatörler
            'function': QColor(0, 0, 255),       # Mavi - fonksiyon tanımları
            'class': QColor(0, 100, 0),          # Koyu yeşil - sınıf tanımları
            'decorator': QColor(255, 165, 0),    # Turuncu - decorator'lar
        }
        
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        # Python anahtar kelimeleri
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
            'del', 'elif', 'else', 'except', 'exec', 'finally', 'for',
            'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'not', 'or', 'pass', 'print', 'raise', 'return', 'try',
            'while', 'with', 'yield', 'True', 'False', 'None', 'async',
            'await', 'nonlocal'
        ]
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(self.colors['keyword'])
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        for keyword in keywords:
            pattern = QRegularExpression(r'\b' + keyword + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Built-in fonksiyonlar
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'compile', 'complex',
            'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval',
            'filter', 'float', 'format', 'frozenset', 'getattr',
            'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input',
            'int', 'isinstance', 'issubclass', 'iter', 'len', 'list',
            'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object',
            'oct', 'open', 'ord', 'pow', 'property', 'range', 'repr',
            'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
            'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
            'vars', 'zip', '__import__'
        ]
        
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(self.colors['builtin'])
        
        for builtin in builtins:
            pattern = QRegularExpression(r'\b' + builtin + r'\b')
            self.highlighting_rules.append((pattern, builtin_format))
        
        # Fonksiyon tanımları
        function_format = QTextCharFormat()
        function_format.setForeground(self.colors['function'])
        function_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression(r'\bdef\s+([A-Za-z_][A-Za-z0-9_]*)')
        self.highlighting_rules.append((pattern, function_format))
        
        # Sınıf tanımları
        class_format = QTextCharFormat()
        class_format.setForeground(self.colors['class'])
        class_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression(r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)')
        self.highlighting_rules.append((pattern, class_format))
        
        # Decorator'lar
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(self.colors['decorator'])
        pattern = QRegularExpression(r'@[A-Za-z_][A-Za-z0-9_]*')
        self.highlighting_rules.append((pattern, decorator_format))
        
        # String'ler (çift tırnak)
        string_format = QTextCharFormat()
        string_format.setForeground(self.colors['string'])
        pattern = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')
        self.highlighting_rules.append((pattern, string_format))
        
        # String'ler (tek tırnak)
        pattern = QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'")
        self.highlighting_rules.append((pattern, string_format))
        
        # Çok satırlı string'ler (üçlü tırnak)
        pattern = QRegularExpression(r'""".*?"""')
        pattern.setPatternOptions(QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, string_format))
        
        pattern = QRegularExpression(r"'''.*?'''")
        pattern.setPatternOptions(QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, string_format))
        
        # Sayılar
        number_format = QTextCharFormat()
        number_format.setForeground(self.colors['number'])
        pattern = QRegularExpression(r'\b\d+\.?\d*\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Hex sayılar
        pattern = QRegularExpression(r'\b0[xX][0-9a-fA-F]+\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Binary sayılar
        pattern = QRegularExpression(r'\b0[bB][01]+\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Yorumlar
        comment_format = QTextCharFormat()
        comment_format.setForeground(self.colors['comment'])
        comment_format.setFontItalic(True)
        pattern = QRegularExpression(r'#[^\r\n]*')
        self.highlighting_rules.append((pattern, comment_format))
    
    def highlightBlock(self, text):
        # Her kural için metni kontrol et
        for pattern, char_format in self.highlighting_rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), char_format)
