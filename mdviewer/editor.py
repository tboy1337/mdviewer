import re
from PyQt6.QtCore import Qt, pyqtSignal, QRegularExpression
from PyQt6.QtGui import (
    QColor, QTextCharFormat, QFont, QSyntaxHighlighter,
    QTextCursor, QPalette, QTextDocument, QTextOption
)
from PyQt6.QtWidgets import (
    QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout,
    QDialog, QLineEdit, QPushButton, QLabel
)

class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, dark_mode=False):
        super().__init__(parent)
        self.dark_mode = dark_mode
        self.setup_formats()
    
    def setup_formats(self):
        # Heading format (# Heading)
        self.heading_format = QTextCharFormat()
        self.heading_format.setFontWeight(QFont.Weight.Bold)
        self.heading_format.setForeground(QColor("#0000FF") if not self.dark_mode else QColor("#42A5F5"))
        
        # Bold format (**bold**)
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)
        
        # Italic format (*italic*)
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        
        # Code format (`code`)
        self.code_format = QTextCharFormat()
        self.code_format.setFontFamily("Courier New")
        self.code_format.setBackground(QColor("#F0F0F0") if not self.dark_mode else QColor("#2D2D2D"))
        
        # Link format ([text](url))
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#0000FF") if not self.dark_mode else QColor("#42A5F5"))
        self.link_format.setFontUnderline(True)
        
        # List item format (- item)
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#008000") if not self.dark_mode else QColor("#66BB6A"))
    
    def set_dark_mode(self, dark_mode):
        self.dark_mode = dark_mode
        self.setup_formats()
        self.rehighlight()
    
    def highlightBlock(self, text):
        # Heading patterns
        for i in range(6, 0, -1):
            pattern = f"^{'#' * i}\\s+.*$"
            self.apply_format(text, QRegularExpression(pattern), self.heading_format)
        
        # Bold pattern
        self.apply_format(text, QRegularExpression("\\*\\*.*?\\*\\*"), self.bold_format)
        self.apply_format(text, QRegularExpression("__.*?__"), self.bold_format)
        
        # Italic pattern
        self.apply_format(text, QRegularExpression("\\*[^\\*]*?\\*"), self.italic_format)
        self.apply_format(text, QRegularExpression("_[^_]*?_"), self.italic_format)
        
        # Code pattern
        self.apply_format(text, QRegularExpression("`[^`]*?`"), self.code_format)
        
        # Link pattern
        self.apply_format(text, QRegularExpression("\\[.*?\\]\\(.*?\\)"), self.link_format)
        
        # List item pattern
        self.apply_format(text, QRegularExpression("^[\\*\\-\\+]\\s+.*$"), self.list_format)
        self.apply_format(text, QRegularExpression("^\\d+\\.\\s+.*$"), self.list_format)
    
    def apply_format(self, text, pattern, fmt):
        regex = pattern
        match = regex.match(text)
        while match.hasMatch():
            start = match.capturedStart()
            length = match.capturedLength()
            self.setFormat(start, length, fmt)
            match = regex.match(text, start + length)


class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Find")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # Search input field
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text...")
        self.search_button = QPushButton("Find")
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        
        # Navigation buttons
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.status_label = QLabel("")
        self.nav_layout.addWidget(self.prev_button)
        self.nav_layout.addWidget(self.next_button)
        self.nav_layout.addWidget(self.status_label)
        
        layout.addLayout(self.search_layout)
        layout.addLayout(self.nav_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.search_button.clicked.connect(self.find_first)
        self.next_button.clicked.connect(self.find_next)
        self.prev_button.clicked.connect(self.find_prev)
        self.search_input.returnPressed.connect(self.find_first)
    
    def find_first(self):
        text = self.search_input.text()
        if not text:
            return
        
        self.cursor_position = 0
        self.find_next()
    
    def find_next(self):
        text = self.search_input.text()
        if not text:
            return
        
        cursor = self.parent.textCursor()
        document = self.parent.document()
        
        # Start from current position
        cursor.setPosition(self.cursor_position)
        
        # Find next occurrence
        find_cursor = document.find(text, cursor)
        
        if not find_cursor.isNull():
            self.parent.setTextCursor(find_cursor)
            self.cursor_position = find_cursor.position() + 1
            self.update_status(True)
        else:
            # Wrap around to the beginning
            cursor.setPosition(0)
            find_cursor = document.find(text, cursor)
            if not find_cursor.isNull():
                self.parent.setTextCursor(find_cursor)
                self.cursor_position = find_cursor.position() + 1
                self.update_status(True, True)
            else:
                self.update_status(False)
    
    def find_prev(self):
        text = self.search_input.text()
        if not text:
            return
        
        cursor = self.parent.textCursor()
        document = self.parent.document()
        
        # Start from current position
        if cursor.position() > 0:
            cursor.setPosition(cursor.position() - 1)
        
        # Find previous occurrence
        find_cursor = document.find(text, cursor, QTextDocument.FindFlag.FindBackward)
        
        if not find_cursor.isNull():
            self.parent.setTextCursor(find_cursor)
            self.cursor_position = find_cursor.position()
            self.update_status(True)
        else:
            # Wrap around to the end
            cursor.setPosition(document.characterCount() - 1)
            find_cursor = document.find(text, cursor, QTextDocument.FindFlag.FindBackward)
            if not find_cursor.isNull():
                self.parent.setTextCursor(find_cursor)
                self.cursor_position = find_cursor.position()
                self.update_status(True, True)
            else:
                self.update_status(False)
    
    def update_status(self, found, wrapped=False):
        if found:
            msg = "Found"
            if wrapped:
                msg += " (wrapped)"
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("color: green")
        else:
            self.status_label.setText("Not found")
            self.status_label.setStyleSheet("color: red")


class MarkdownEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_editor()
        self.highlighter = MarkdownHighlighter(self.document())
        self.find_dialog = None
    
    def setup_editor(self):
        # Use a monospaced font
        font = QFont("Courier New", 10)
        self.setFont(font)
        
        # Word wrap
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        
        # Line numbers would go here (with custom implementation)
        
        # Tab settings
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
    
    def set_dark_mode(self, dark_mode):
        # Set dark mode for the editor
        palette = self.palette()
        if dark_mode:
            palette.setColor(QPalette.ColorRole.Base, QColor("#1E1E1E"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
        else:
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
        
        self.setPalette(palette)
        
        # Update highlighter
        self.highlighter.set_dark_mode(dark_mode)
    
    def show_find_dialog(self):
        if not self.find_dialog:
            self.find_dialog = FindDialog(self)
        
        # Position the dialog
        cursor_rect = self.cursorRect()
        pos = self.mapToGlobal(cursor_rect.bottomRight())
        self.find_dialog.move(pos)
        
        self.find_dialog.show()
        self.find_dialog.search_input.setFocus()
        
        # If text is selected, use it as the search term
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.find_dialog.search_input.setText(cursor.selectedText())
            self.find_dialog.cursor_position = cursor.position() - len(cursor.selectedText())
        else:
            self.find_dialog.cursor_position = cursor.position()
    
    def scroll_to_heading(self, heading_text, level):
        """Scroll to the heading with the given text and level"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        # Create pattern for the heading
        pattern = f"^{'#' * level}\\s+{re.escape(heading_text)}$"
        regex = QRegularExpression(pattern)
        
        # Search for the heading
        document = self.document()
        find_cursor = document.find(regex, cursor)
        
        if not find_cursor.isNull():
            self.setTextCursor(find_cursor)
            # Ensure the heading is visible
            self.ensureCursorVisible() 