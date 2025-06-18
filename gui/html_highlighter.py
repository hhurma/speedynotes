from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt

class HtmlSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        # Renk şeması
        self.colors = {
            'tag': QColor(0, 0, 255),            # Mavi - HTML etiketleri
            'attribute': QColor(255, 0, 0),      # Kırmızı - attribute'lar
            'value': QColor(0, 128, 0),          # Yeşil - attribute değerleri
            'comment': QColor(128, 128, 128),    # Gri - yorumlar
            'doctype': QColor(128, 0, 128),      # Mor - DOCTYPE
            'entity': QColor(255, 165, 0),       # Turuncu - HTML entities
            'keyword': QColor(0, 0, 255),        # Mavi - CSS/JS keywords
            'string': QColor(0, 128, 0),         # Yeşil - CSS/JS strings
            'css_property': QColor(128, 0, 128), # Mor - CSS properties
            'css_value': QColor(255, 0, 0),      # Kırmızı - CSS values
        }
        
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        # HTML Yorumları
        comment_format = QTextCharFormat()
        comment_format.setForeground(self.colors['comment'])
        comment_format.setFontItalic(True)
        pattern = QRegularExpression(r'<!--.*?-->')
        pattern.setPatternOptions(QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, comment_format))
        
        # DOCTYPE
        doctype_format = QTextCharFormat()
        doctype_format.setForeground(self.colors['doctype'])
        doctype_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression(r'<!DOCTYPE[^>]*>')
        pattern.setPatternOptions(QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.highlighting_rules.append((pattern, doctype_format))
        
        # HTML Etiketleri
        tag_format = QTextCharFormat()
        tag_format.setForeground(self.colors['tag'])
        tag_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression(r'</?[a-zA-Z][a-zA-Z0-9]*(?=\s|>|/>)')
        self.highlighting_rules.append((pattern, tag_format))
        
        # HTML Attribute'ları
        attribute_format = QTextCharFormat()
        attribute_format.setForeground(self.colors['attribute'])
        pattern = QRegularExpression(r'\b[a-zA-Z-]+(?=\s*=)')
        self.highlighting_rules.append((pattern, attribute_format))
        
        # Attribute Değerleri (çift tırnak)
        value_format = QTextCharFormat()
        value_format.setForeground(self.colors['value'])
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, value_format))
        
        # Attribute Değerleri (tek tırnak)
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, value_format))
        
        # HTML Entities
        entity_format = QTextCharFormat()
        entity_format.setForeground(self.colors['entity'])
        pattern = QRegularExpression(r'&[a-zA-Z][a-zA-Z0-9]*;|&#[0-9]+;|&#x[0-9a-fA-F]+;')
        self.highlighting_rules.append((pattern, entity_format))
        
        # CSS içeriği (style etiketleri arası)
        self.setup_css_rules()
        
        # JavaScript içeriği (script etiketleri arası)
        self.setup_js_rules()
    
    def setup_css_rules(self):
        # CSS Properties
        css_property_format = QTextCharFormat()
        css_property_format.setForeground(self.colors['css_property'])
        css_properties = [
            'color', 'background', 'background-color', 'font-size', 'font-family',
            'font-weight', 'margin', 'padding', 'border', 'width', 'height',
            'display', 'position', 'top', 'left', 'right', 'bottom', 'float',
            'clear', 'text-align', 'text-decoration', 'line-height', 'z-index',
            'opacity', 'cursor', 'overflow', 'visibility', 'box-shadow',
            'border-radius', 'transform', 'transition', 'animation'
        ]
        
        for prop in css_properties:
            pattern = QRegularExpression(r'\b' + prop + r'(?=\s*:)')
            self.highlighting_rules.append((pattern, css_property_format))
        
        # CSS Values
        css_value_format = QTextCharFormat()
        css_value_format.setForeground(self.colors['css_value'])
        css_values = [
            'px', 'em', 'rem', '%', 'vh', 'vw', 'pt', 'pc', 'in', 'mm', 'cm',
            'none', 'auto', 'inherit', 'initial', 'unset', 'solid', 'dashed',
            'dotted', 'double', 'groove', 'ridge', 'inset', 'outset', 'hidden',
            'visible', 'block', 'inline', 'inline-block', 'flex', 'grid',
            'absolute', 'relative', 'fixed', 'static', 'sticky', 'left', 'center',
            'right', 'justify', 'bold', 'normal', 'italic', 'underline'
        ]
        
        for value in css_values:
            pattern = QRegularExpression(r'\b' + value + r'\b')
            self.highlighting_rules.append((pattern, css_value_format))
        
        # CSS Renk değerleri
        pattern = QRegularExpression(r'#[0-9a-fA-F]{3,6}\b')
        self.highlighting_rules.append((pattern, css_value_format))
        
        # CSS rgb/rgba
        pattern = QRegularExpression(r'rgba?\([^)]+\)')
        self.highlighting_rules.append((pattern, css_value_format))
    
    def setup_js_rules(self):
        # JavaScript Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(self.colors['keyword'])
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        js_keywords = [
            'var', 'let', 'const', 'function', 'return', 'if', 'else', 'for',
            'while', 'do', 'switch', 'case', 'default', 'break', 'continue',
            'try', 'catch', 'finally', 'throw', 'new', 'this', 'typeof',
            'instanceof', 'in', 'of', 'true', 'false', 'null', 'undefined',
            'class', 'extends', 'super', 'static', 'async', 'await', 'yield',
            'import', 'export', 'from', 'default'
        ]
        
        for keyword in js_keywords:
            pattern = QRegularExpression(r'\b' + keyword + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # JavaScript Strings
        string_format = QTextCharFormat()
        string_format.setForeground(self.colors['string'])
        
        # Çift tırnak strings
        pattern = QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"')
        self.highlighting_rules.append((pattern, string_format))
        
        # Tek tırnak strings
        pattern = QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'")
        self.highlighting_rules.append((pattern, string_format))
        
        # Template literals
        pattern = QRegularExpression(r'`[^`\\]*(\\.[^`\\]*)*`')
        self.highlighting_rules.append((pattern, string_format))
        
        # JavaScript Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(self.colors['comment'])
        comment_format.setFontItalic(True)
        
        # Tek satır yorum
        pattern = QRegularExpression(r'//[^\r\n]*')
        self.highlighting_rules.append((pattern, comment_format))
        
        # Çok satır yorum
        pattern = QRegularExpression(r'/\*.*?\*/')
        pattern.setPatternOptions(QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, comment_format))
    
    def highlightBlock(self, text):
        # Her kural için metni kontrol et
        for pattern, char_format in self.highlighting_rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), char_format)
