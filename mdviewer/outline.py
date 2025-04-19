import re
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QBrush
from PyQt6.QtWidgets import (
    QWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QLabel, QHeaderView
)

class DocumentOutline(QWidget):
    # Signal emitted when a heading is clicked
    heading_clicked = pyqtSignal(str, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
    
    def setup_ui(self):
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header label
        header_label = QLabel("Document Outline")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Tree widget for outline
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setAnimated(True)
        
        layout.addWidget(self.tree)
        
        # Connect signals
        self.tree.itemClicked.connect(self.on_item_clicked)
    
    def update_outline(self, markdown_text):
        """Extract headings from markdown and build the outline"""
        self.tree.clear()
        
        if not markdown_text:
            return
        
        # Extract headings (# Heading)
        headings = self.extract_headings(markdown_text)
        
        # Build the tree
        self.build_tree(headings)
        
        # Expand all items
        self.tree.expandAll()
    
    def extract_headings(self, markdown_text):
        """Extract all headings from markdown text with their levels"""
        headings = []
        
        # Split markdown into lines
        lines = markdown_text.split('\n')
        
        # Regex for headings (# Heading)
        heading_regex = re.compile(r'^(#{1,6})\s+(.+)$')
        
        for line in lines:
            match = heading_regex.match(line)
            if match:
                level = len(match.group(1))  # Number of # symbols
                text = match.group(2).strip()
                headings.append({
                    'level': level,
                    'text': text,
                })
        
        return headings
    
    def build_tree(self, headings):
        """Build the tree widget from the extracted headings"""
        if not headings:
            return
        
        # Stack to keep track of parent items at each level
        parent_stack = [None] * 7  # H1-H6 (0-indexed, so 7 elements)
        
        for heading in headings:
            level = heading['level']
            text = heading['text']
            
            # Create the item
            item = QTreeWidgetItem([text])
            item.setData(0, Qt.ItemDataRole.UserRole, level)  # Store level in user data
            
            # Find the parent
            if level == 1:
                # Top level heading - add to root
                self.tree.addTopLevelItem(item)
                parent_stack[1] = item
            else:
                # Find the closest parent level
                parent_level = level - 1
                # Search for the closest parent level that exists
                while parent_level > 0 and parent_stack[parent_level] is None:
                    parent_level -= 1
                
                if parent_level == 0:
                    # No parent found, add to root
                    self.tree.addTopLevelItem(item)
                else:
                    # Add as child of parent
                    parent_stack[parent_level].addChild(item)
            
            # Update the parent stack for this level
            parent_stack[level] = item
            
            # Clear all deeper levels from the stack
            for i in range(level + 1, 7):
                parent_stack[i] = None
    
    def on_item_clicked(self, item, column):
        """Handle click on a heading item"""
        level = item.data(0, Qt.ItemDataRole.UserRole)
        text = item.text(0)
        self.heading_clicked.emit(text, level)
    
    def set_dark_mode(self, dark_mode):
        """Apply dark mode to the outline widget"""
        palette = self.palette()
        
        if dark_mode:
            # Dark mode colors
            palette.setColor(QPalette.ColorRole.Base, QColor("#1E1E1E"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Window, QColor("#252526"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
        else:
            # Light mode colors
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Window, QColor("#F0F0F0"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        
        self.setPalette(palette)
        self.tree.setPalette(palette) 