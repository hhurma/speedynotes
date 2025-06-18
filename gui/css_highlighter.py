from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression, Qt

class CssSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        # Renk şeması
        self.colors = {
            'selector': QColor(0, 0, 255),           # Mavi - CSS seçiciler
            'property': QColor(128, 0, 128),         # Mor - CSS özellikleri
            'value': QColor(255, 0, 0),              # Kırmızı - CSS değerleri
            'string': QColor(0, 128, 0),             # Yeşil - String değerler
            'comment': QColor(128, 128, 128),        # Gri - Yorumlar
            'important': QColor(255, 0, 0),          # Kırmızı - !important
            'color_value': QColor(255, 165, 0),      # Turuncu - Renk değerleri
            'unit': QColor(0, 100, 0),               # Koyu yeşil - Birimler
            'pseudo': QColor(0, 150, 150),           # Teal - Pseudo seçiciler
            'at_rule': QColor(128, 0, 128),          # Mor - @media, @import vb.
        }
        
        self.setup_highlighting_rules()
    
    def setup_highlighting_rules(self):
        # CSS Yorumları
        comment_format = QTextCharFormat()
        comment_format.setForeground(self.colors['comment'])
        comment_format.setFontItalic(True)
        pattern = QRegularExpression(r'/\*.*?\*/')
        pattern.setPatternOptions(QRegularExpression.PatternOption.DotMatchesEverythingOption)
        self.highlighting_rules.append((pattern, comment_format))
        
        # At-rules (@media, @import, @keyframes, vb.)
        at_rule_format = QTextCharFormat()
        at_rule_format.setForeground(self.colors['at_rule'])
        at_rule_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression(r'@[a-zA-Z-]+')
        self.highlighting_rules.append((pattern, at_rule_format))
        
        # CSS Seçiciler (class, id, element, attribute)
        selector_format = QTextCharFormat()
        selector_format.setForeground(self.colors['selector'])
        selector_format.setFontWeight(QFont.Weight.Bold)
        
        # Class seçiciler (.class)
        pattern = QRegularExpression(r'\.[a-zA-Z_-][a-zA-Z0-9_-]*')
        self.highlighting_rules.append((pattern, selector_format))
        
        # ID seçiciler (#id)
        pattern = QRegularExpression(r'#[a-zA-Z_-][a-zA-Z0-9_-]*')
        self.highlighting_rules.append((pattern, selector_format))
        
        # Element seçiciler
        elements = [
            'html', 'head', 'body', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'a', 'img', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form', 'input', 'button',
            'header', 'nav', 'main', 'section', 'article', 'aside', 'footer', 'strong', 'em',
            'code', 'pre', 'blockquote', 'small', 'mark', 'del', 'ins', 'sub', 'sup'
        ]
        
        for element in elements:
            pattern = QRegularExpression(r'\b' + element + r'(?=\s*[{,.:>#\[])')
            self.highlighting_rules.append((pattern, selector_format))
        
        # Pseudo seçiciler (:hover, :focus, ::before, vb.)
        pseudo_format = QTextCharFormat()
        pseudo_format.setForeground(self.colors['pseudo'])
        pattern = QRegularExpression(r'::?[a-zA-Z-]+(?:\([^)]*\))?')
        self.highlighting_rules.append((pattern, pseudo_format))
        
        # CSS Properties
        property_format = QTextCharFormat()
        property_format.setForeground(self.colors['property'])
        
        css_properties = [
            # Layout
            'display', 'position', 'top', 'right', 'bottom', 'left', 'float', 'clear',
            'overflow', 'overflow-x', 'overflow-y', 'visibility', 'z-index',
            
            # Box Model
            'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
            'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
            'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
            
            # Border
            'border', 'border-width', 'border-style', 'border-color', 'border-radius',
            'border-top', 'border-right', 'border-bottom', 'border-left',
            'border-top-width', 'border-right-width', 'border-bottom-width', 'border-left-width',
            'border-top-style', 'border-right-style', 'border-bottom-style', 'border-left-style',
            'border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color',
            
            # Background
            'background', 'background-color', 'background-image', 'background-repeat',
            'background-position', 'background-size', 'background-attachment',
            
            # Text
            'color', 'font', 'font-family', 'font-size', 'font-weight', 'font-style',
            'line-height', 'text-align', 'text-decoration', 'text-transform', 'text-indent',
            'letter-spacing', 'word-spacing', 'white-space', 'text-shadow',
            
            # Flexbox
            'flex', 'flex-direction', 'flex-wrap', 'flex-flow', 'justify-content',
            'align-items', 'align-content', 'align-self', 'flex-grow', 'flex-shrink', 'flex-basis',
            
            # Grid
            'grid', 'grid-template', 'grid-template-rows', 'grid-template-columns',
            'grid-template-areas', 'grid-gap', 'grid-row-gap', 'grid-column-gap',
            
            # Animation & Transform
            'transform', 'transition', 'animation', 'opacity', 'cursor',
            'box-shadow', 'text-shadow', 'filter'
        ]
        
        for prop in css_properties:
            pattern = QRegularExpression(r'\b' + prop + r'(?=\s*:)')
            self.highlighting_rules.append((pattern, property_format))
        
        # !important
        important_format = QTextCharFormat()
        important_format.setForeground(self.colors['important'])
        important_format.setFontWeight(QFont.Weight.Bold)
        pattern = QRegularExpression(r'!important')
        self.highlighting_rules.append((pattern, important_format))
        
        # CSS String değerleri (tırnak içi)
        string_format = QTextCharFormat()
        string_format.setForeground(self.colors['string'])
        
        # Çift tırnak
        pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((pattern, string_format))
        
        # Tek tırnak
        pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((pattern, string_format))
        
        # URL fonksiyonu
        pattern = QRegularExpression(r'url\([^)]*\)')
        self.highlighting_rules.append((pattern, string_format))
        
        # Renk değerleri
        color_format = QTextCharFormat()
        color_format.setForeground(self.colors['color_value'])
        
        # Hex renkler
        pattern = QRegularExpression(r'#[0-9a-fA-F]{3,8}\b')
        self.highlighting_rules.append((pattern, color_format))
        
        # RGB/RGBA
        pattern = QRegularExpression(r'rgba?\s*\([^)]+\)')
        self.highlighting_rules.append((pattern, color_format))
        
        # HSL/HSLA
        pattern = QRegularExpression(r'hsla?\s*\([^)]+\)')
        self.highlighting_rules.append((pattern, color_format))
        
        # CSS renk isimleri
        color_names = [
            'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown',
            'black', 'white', 'gray', 'grey', 'silver', 'gold', 'cyan', 'magenta',
            'lime', 'olive', 'navy', 'teal', 'aqua', 'fuchsia', 'maroon', 'transparent'
        ]
        
        for color in color_names:
            pattern = QRegularExpression(r'\b' + color + r'\b')
            self.highlighting_rules.append((pattern, color_format))
        
        # CSS Değerleri ve birimler
        value_format = QTextCharFormat()
        value_format.setForeground(self.colors['value'])
        
        # Sayısal değerler
        pattern = QRegularExpression(r'\b\d+\.?\d*')
        self.highlighting_rules.append((pattern, value_format))
        
        # Birimler
        unit_format = QTextCharFormat()
        unit_format.setForeground(self.colors['unit'])
        
        units = [
            'px', 'em', 'rem', '%', 'vh', 'vw', 'vmin', 'vmax', 'pt', 'pc', 'in', 'mm', 'cm',
            'ex', 'ch', 'deg', 'rad', 'grad', 'turn', 's', 'ms', 'Hz', 'kHz', 'dpi', 'dpcm', 'dppx'
        ]
        
        for unit in units:
            pattern = QRegularExpression(r'\b\d*\.?\d+' + unit + r'\b')
            self.highlighting_rules.append((pattern, unit_format))
        
        # CSS anahtar kelimeler
        keyword_values = [
            'auto', 'none', 'normal', 'inherit', 'initial', 'unset', 'revert',
            'block', 'inline', 'inline-block', 'flex', 'grid', 'table', 'table-cell',
            'absolute', 'relative', 'fixed', 'static', 'sticky',
            'left', 'right', 'center', 'top', 'bottom', 'middle', 'justify',
            'bold', 'normal', 'lighter', 'bolder', 'italic', 'oblique',
            'solid', 'dashed', 'dotted', 'double', 'groove', 'ridge', 'inset', 'outset',
            'hidden', 'visible', 'scroll', 'clip', 'ellipsis',
            'uppercase', 'lowercase', 'capitalize',
            'underline', 'overline', 'line-through',
            'repeat', 'no-repeat', 'repeat-x', 'repeat-y',
            'cover', 'contain', 'border-box', 'content-box'
        ]
        
        for keyword in keyword_values:
            pattern = QRegularExpression(r'\b' + keyword + r'\b')
            self.highlighting_rules.append((pattern, value_format))
    
    def highlightBlock(self, text):
        # Her kural için metni kontrol et
        for pattern, char_format in self.highlighting_rules:
            expression = pattern
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), char_format)
