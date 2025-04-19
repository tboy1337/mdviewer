import os
import sys
import json
import webbrowser
from pathlib import Path
from urllib.parse import urlparse
import requests

from PyQt6.QtCore import (
    Qt, QUrl, QSettings, QSize, pyqtSlot, QTimer, QFileInfo, QMimeData
)
from PyQt6.QtGui import (
    QIcon, QTextCursor, QAction, QKeySequence, QFont, 
    QFontDatabase, QDesktopServices, QDragEnterEvent, QDropEvent
)
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QSplitter, QWidget, QVBoxLayout, 
    QHBoxLayout, QToolBar, QFileDialog, QInputDialog, QMessageBox,
    QLineEdit, QPushButton, QMenu, QStatusBar, QToolButton,
    QLabel, QComboBox, QSlider
)
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

from mdviewer.editor import MarkdownEditor
from mdviewer.preview import MarkdownPreview
from mdviewer.outline import DocumentOutline
from mdviewer.exporter import HTMLExporter, PDFExporter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MDViewer")
        self.setMinimumSize(800, 600)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        self.current_file = None
        self.recent_files = []
        self.max_recent_files = 5
        
        self.settings = QSettings("MDViewer", "MDViewer")
        self.load_settings()
        
        self.setup_ui()
        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.create_statusbar()
        self.setup_connections()
        self.update_recent_files_menu()
        
        # Check for command-line arguments
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            self.open_file(file_path)
    
    def setup_ui(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create editor and preview widgets
        self.editor = MarkdownEditor()
        self.preview = MarkdownPreview()
        
        # Create outline widget
        self.outline = DocumentOutline()
        
        # Set up splitters
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.h_splitter.addWidget(self.editor)
        self.h_splitter.addWidget(self.preview)
        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 1)
        
        self.v_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.v_splitter.addWidget(self.outline)
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.setStretchFactor(0, 0)
        self.v_splitter.setStretchFactor(1, 3)
        
        self.main_layout.addWidget(self.v_splitter)
        
        # Initially hide the outline
        self.outline.hide()
    
    def create_actions(self):
        # File actions
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        
        self.open_action = QAction("Open...", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        
        self.open_url_action = QAction("Open from URL...", self)
        self.open_url_action.setShortcut(QKeySequence("Ctrl+U"))
        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        
        self.save_as_action = QAction("Save As...", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        
        self.export_html_action = QAction("Export as HTML...", self)
        self.export_pdf_action = QAction("Export as PDF...", self)
        self.print_action = QAction("Print...", self)
        self.print_action.setShortcut(QKeySequence.StandardKey.Print)
        
        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        
        # Edit actions
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        
        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        
        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        
        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        
        self.find_action = QAction("Find...", self)
        self.find_action.setShortcut(QKeySequence.StandardKey.Find)
        
        # View actions
        self.increase_font_action = QAction("Increase Font Size", self)
        self.increase_font_action.setShortcut(QKeySequence("Ctrl++"))
        
        self.decrease_font_action = QAction("Decrease Font Size", self)
        self.decrease_font_action.setShortcut(QKeySequence("Ctrl+-"))
        
        self.toggle_outline_action = QAction("Toggle Outline", self)
        self.toggle_outline_action.setShortcut(QKeySequence("Ctrl+L"))
        self.toggle_outline_action.setCheckable(True)
        
        self.dark_mode_action = QAction("Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.settings.value("dark_mode", False, type=bool))
        
        # View mode actions
        self.editor_only_action = QAction("Editor Only", self)
        self.editor_only_action.setCheckable(True)
        
        self.split_view_action = QAction("Split View", self)
        self.split_view_action.setCheckable(True)
        self.split_view_action.setChecked(True)
        
        self.preview_only_action = QAction("Preview Only", self)
        self.preview_only_action.setCheckable(True)
        
        view_mode_group = QActionGroup(self)
        view_mode_group.addAction(self.editor_only_action)
        view_mode_group.addAction(self.split_view_action)
        view_mode_group.addAction(self.preview_only_action)
        view_mode_group.setExclusive(True)
        
        # Help actions
        self.about_action = QAction("About", self)
    
    def create_menus(self):
        # Main menu bar
        menu_bar = self.menuBar()
        
        # File menu
        self.file_menu = menu_bar.addMenu("File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.open_url_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        
        # Export submenu
        self.export_menu = self.file_menu.addMenu("Export")
        self.export_menu.addAction(self.export_html_action)
        self.export_menu.addAction(self.export_pdf_action)
        self.file_menu.addAction(self.print_action)
        self.file_menu.addSeparator()
        
        # Recent files submenu
        self.recent_files_menu = self.file_menu.addMenu("Recent Files")
        self.file_menu.addSeparator()
        
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = menu_bar.addMenu("Edit")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.cut_action)
        self.edit_menu.addAction(self.copy_action)
        self.edit_menu.addAction(self.paste_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.find_action)
        
        # View menu
        self.view_menu = menu_bar.addMenu("View")
        
        # View mode submenu
        self.view_mode_menu = self.view_menu.addMenu("View Mode")
        self.view_mode_menu.addAction(self.editor_only_action)
        self.view_mode_menu.addAction(self.split_view_action)
        self.view_mode_menu.addAction(self.preview_only_action)
        
        self.view_menu.addAction(self.toggle_outline_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.increase_font_action)
        self.view_menu.addAction(self.decrease_font_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.dark_mode_action)
        
        # Help menu
        self.help_menu = menu_bar.addMenu("Help")
        self.help_menu.addAction(self.about_action)
    
    def create_toolbar(self):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.addToolBar(self.toolbar)
        
        # File operations
        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addSeparator()
        
        # View mode buttons
        self.toolbar.addAction(self.editor_only_action)
        self.toolbar.addAction(self.split_view_action)
        self.toolbar.addAction(self.preview_only_action)
        self.toolbar.addSeparator()
        
        # Font size controls
        self.toolbar.addAction(self.decrease_font_action)
        self.toolbar.addAction(self.increase_font_action)
        self.toolbar.addSeparator()
        
        # Outline toggle
        self.toolbar.addAction(self.toggle_outline_action)
        
        # Theme toggle
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.dark_mode_action)
    
    def create_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)
    
    def setup_connections(self):
        # Connect file actions
        self.new_action.triggered.connect(self.new_file)
        self.open_action.triggered.connect(self.show_open_dialog)
        self.open_url_action.triggered.connect(self.show_open_url_dialog)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.export_html_action.triggered.connect(self.export_html)
        self.export_pdf_action.triggered.connect(self.export_pdf)
        self.print_action.triggered.connect(self.print_document)
        self.exit_action.triggered.connect(self.close)
        
        # Connect edit actions
        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)
        self.cut_action.triggered.connect(self.editor.cut)
        self.copy_action.triggered.connect(self.editor.copy)
        self.paste_action.triggered.connect(self.editor.paste)
        self.find_action.triggered.connect(self.editor.show_find_dialog)
        
        # Connect view actions
        self.increase_font_action.triggered.connect(self.increase_font_size)
        self.decrease_font_action.triggered.connect(self.decrease_font_size)
        self.toggle_outline_action.triggered.connect(self.toggle_outline)
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        
        # Connect view mode actions
        self.editor_only_action.triggered.connect(self.set_editor_only)
        self.split_view_action.triggered.connect(self.set_split_view)
        self.preview_only_action.triggered.connect(self.set_preview_only)
        
        # Connect editor and preview
        self.editor.textChanged.connect(self.update_preview)
        
        # Connect outline to editor
        self.outline.heading_clicked.connect(self.editor.scroll_to_heading)
        
        # Connect help actions
        self.about_action.triggered.connect(self.show_about_dialog)
    
    def new_file(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("MDViewer - Untitled")
            self.status_label.setText("New document created")
    
    def show_open_dialog(self):
        if self.maybe_save():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open Markdown File", "",
                "Markdown Files (*.md *.markdown);;All Files (*)"
            )
            if file_path:
                self.open_file(file_path)
    
    def open_file(self, file_path):
        if not os.path.exists(file_path):
            QMessageBox.warning(
                self, "File Not Found",
                f"The file {file_path} does not exist."
            )
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.editor.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"MDViewer - {os.path.basename(file_path)}")
            self.status_label.setText(f"Opened {file_path}")
            
            # Add to recent files
            self.add_recent_file(file_path)
            
        except Exception as e:
            QMessageBox.warning(
                self, "Error Opening File",
                f"Could not open file: {str(e)}"
            )
    
    def show_open_url_dialog(self):
        url, ok = QInputDialog.getText(
            self, "Open from URL",
            "Enter URL of Markdown file:"
        )
        
        if ok and url:
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                content = response.text
                self.editor.setPlainText(content)
                self.current_file = None  # No local file
                self.setWindowTitle(f"MDViewer - {url}")
                self.status_label.setText(f"Opened from URL: {url}")
                
            except Exception as e:
                QMessageBox.warning(
                    self, "Error Opening URL",
                    f"Could not open URL: {str(e)}"
                )
    
    def save_file(self):
        if self.current_file:
            return self.save_to_file(self.current_file)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Markdown File", "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        
        if file_path:
            return self.save_to_file(file_path)
        return False
    
    def save_to_file(self, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.editor.toPlainText())
            
            self.current_file = file_path
            self.setWindowTitle(f"MDViewer - {os.path.basename(file_path)}")
            self.status_label.setText(f"Saved to {file_path}")
            
            # Add to recent files
            self.add_recent_file(file_path)
            
            return True
            
        except Exception as e:
            QMessageBox.warning(
                self, "Error Saving File",
                f"Could not save file: {str(e)}"
            )
            return False
    
    def export_html(self):
        if not self.editor.toPlainText():
            QMessageBox.warning(self, "Empty Document", "Nothing to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export HTML", "",
            "HTML Files (*.html *.htm);;All Files (*)"
        )
        
        if file_path:
            exporter = HTMLExporter()
            try:
                html_content = exporter.export(self.editor.toPlainText())
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(html_content)
                
                self.status_label.setText(f"Exported HTML to {file_path}")
                
            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error",
                    f"Could not export to HTML: {str(e)}"
                )
    
    def export_pdf(self):
        if not self.editor.toPlainText():
            QMessageBox.warning(self, "Empty Document", "Nothing to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            exporter = PDFExporter()
            try:
                exporter.export(self.editor.toPlainText(), file_path)
                self.status_label.setText(f"Exported PDF to {file_path}")
                
            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error",
                    f"Could not export to PDF: {str(e)}"
                )
    
    def print_document(self):
        if not self.editor.toPlainText():
            QMessageBox.warning(self, "Empty Document", "Nothing to print.")
            return
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            exporter = PDFExporter()
            try:
                html_content = exporter.markdown_to_html(self.editor.toPlainText())
                self.preview.print_(printer, html_content)
                self.status_label.setText("Document sent to printer")
                
            except Exception as e:
                QMessageBox.warning(
                    self, "Print Error",
                    f"Could not print document: {str(e)}"
                )
    
    def maybe_save(self):
        if not self.editor.document().isModified():
            return True
        
        ret = QMessageBox.warning(
            self, "MDViewer",
            "The document has been modified.\nDo you want to save your changes?",
            QMessageBox.StandardButton.Save | 
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )
        
        if ret == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif ret == QMessageBox.StandardButton.Cancel:
            return False
        
        return True  # Discard
    
    def increase_font_size(self):
        current_font = self.editor.font()
        size = current_font.pointSize()
        if size < 30:  # Max size
            current_font.setPointSize(size + 1)
            self.editor.setFont(current_font)
            self.preview.set_zoom_factor(self.preview.zoom_factor * 1.1)
    
    def decrease_font_size(self):
        current_font = self.editor.font()
        size = current_font.pointSize()
        if size > 8:  # Min size
            current_font.setPointSize(size - 1)
            self.editor.setFont(current_font)
            self.preview.set_zoom_factor(self.preview.zoom_factor * 0.9)
    
    def toggle_outline(self):
        if self.outline.isVisible():
            self.outline.hide()
            self.toggle_outline_action.setChecked(False)
        else:
            self.outline.show()
            self.toggle_outline_action.setChecked(True)
            self.update_outline()
    
    def toggle_dark_mode(self):
        is_dark = self.dark_mode_action.isChecked()
        self.settings.setValue("dark_mode", is_dark)
        
        # Apply dark mode to components
        self.editor.set_dark_mode(is_dark)
        self.preview.set_dark_mode(is_dark)
        self.outline.set_dark_mode(is_dark)
        
        # Update the window
        self.status_label.setText(f"Theme: {'Dark' if is_dark else 'Light'}")
    
    def set_editor_only(self):
        self.preview.hide()
        self.editor.show()
    
    def set_split_view(self):
        self.editor.show()
        self.preview.show()
        # Reset splitter sizes
        self.h_splitter.setSizes([int(self.width() / 2), int(self.width() / 2)])
    
    def set_preview_only(self):
        self.editor.hide()
        self.preview.show()
    
    def update_preview(self):
        # Update markdown preview
        markdown_text = self.editor.toPlainText()
        self.preview.set_markdown(markdown_text)
        
        # Update outline
        self.update_outline()
    
    def update_outline(self):
        markdown_text = self.editor.toPlainText()
        self.outline.update_outline(markdown_text)
    
    def add_recent_file(self, file_path):
        # Normalize path
        file_path = os.path.normpath(file_path)
        
        # Remove if already in list
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        # Add to front of list
        self.recent_files.insert(0, file_path)
        
        # Keep only max_recent_files
        self.recent_files = self.recent_files[:self.max_recent_files]
        
        # Update menu
        self.update_recent_files_menu()
        
        # Save to settings
        self.settings.setValue("recent_files", self.recent_files)
    
    def update_recent_files_menu(self):
        self.recent_files_menu.clear()
        
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setData(file_path)
                action.setStatusTip(file_path)
                action.triggered.connect(self.open_recent_file)
                self.recent_files_menu.addAction(action)
        
        if self.recent_files:
            self.recent_files_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
    
    def open_recent_file(self):
        action = self.sender()
        if action and self.maybe_save():
            file_path = action.data()
            self.open_file(file_path)
    
    def clear_recent_files(self):
        self.recent_files.clear()
        self.update_recent_files_menu()
        self.settings.setValue("recent_files", self.recent_files)
    
    def show_about_dialog(self):
        QMessageBox.about(
            self, "About MDViewer",
            "MDViewer - A cross-platform Markdown viewer\n\n"
            "Version 0.1.0\n\n"
            "A modern, feature-rich Markdown editor and previewer."
        )
    
    def load_settings(self):
        # Load recent files
        recent_files = self.settings.value("recent_files", [])
        if recent_files:
            self.recent_files = recent_files
        
        # Load window state if exists
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def save_settings(self):
        # Save window state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Save recent files
        self.settings.setValue("recent_files", self.recent_files)
        
        # Save dark mode
        self.settings.setValue("dark_mode", self.dark_mode_action.isChecked())
    
    def closeEvent(self, event):
        if self.maybe_save():
            self.save_settings()
            event.accept()
        else:
            event.ignore()
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events."""
        # Check if the event has URLs (files)
        if event.mimeData().hasUrls():
            # Check for markdown files
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    # Check if it's a markdown file
                    if file_path.lower().endswith(('.md', '.markdown')):
                        event.acceptProposedAction()
                        return
        
        # If we get here, we didn't find a valid markdown file
        event.ignore()
    
    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events."""
        if event.mimeData().hasUrls():
            # Get the first URL (we'll only open one file)
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    # Check if it's a markdown file
                    if file_path.lower().endswith(('.md', '.markdown')):
                        # Check if we need to save the current file
                        if self.maybe_save():
                            self.open_file(file_path)
                            event.acceptProposedAction()
                            return
                        break
        
        event.ignore() 