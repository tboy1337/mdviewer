import os
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

class MarkdownPreview(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.zoom_factor = 1.0
        self.is_dark_mode = False
        
        # Set up web engine settings
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        
        # Apply default styles
        self.default_css = self._get_default_css()
        self.current_css = self.default_css
        
        # Initialize with empty content
        self.set_markdown("")
    
    def _get_default_css(self):
        """Get the default CSS for the preview"""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 980px;
            margin: 0 auto;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: 0.875em; }
        h6 { font-size: 0.85em; }
        
        code, pre {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            background-color: #f6f8fa;
            border-radius: 3px;
        }
        
        code {
            padding: 0.2em 0.4em;
            font-size: 85%;
        }
        
        pre {
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
        }
        
        pre code {
            padding: 0;
            background-color: transparent;
        }
        
        blockquote {
            margin-left: 0;
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        
        table th, table td {
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
        }
        
        table tr:nth-child(2n) {
            background-color: #f6f8fa;
        }
        
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }
        
        img {
            max-width: 100%;
            box-sizing: content-box;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        """
    
    def _get_dark_css(self):
        """Get the dark mode CSS for the preview"""
        return """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 980px;
            margin: 0 auto;
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
            color: #e6edf3;
        }
        
        h1 { font-size: 2em; }
        h2 { font-size: 1.5em; }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: 0.875em; }
        h6 { font-size: 0.85em; }
        
        code, pre {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            background-color: #161b22;
            border-radius: 3px;
        }
        
        code {
            padding: 0.2em 0.4em;
            font-size: 85%;
        }
        
        pre {
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
        }
        
        pre code {
            padding: 0;
            background-color: transparent;
        }
        
        blockquote {
            margin-left: 0;
            padding: 0 1em;
            color: #8b949e;
            border-left: 0.25em solid #30363d;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }
        
        table th, table td {
            padding: 6px 13px;
            border: 1px solid #30363d;
        }
        
        table tr:nth-child(2n) {
            background-color: #161b22;
        }
        
        hr {
            height: 0.25em;
            padding: 0;
            margin: 24px 0;
            background-color: #30363d;
            border: 0;
        }
        
        img {
            max-width: 100%;
            box-sizing: content-box;
        }
        
        a {
            color: #58a6ff;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        """
    
    def set_markdown(self, text):
        """Set the markdown content to be displayed"""
        # Process markdown to HTML
        extensions = [
            FencedCodeExtension(),
            CodeHiliteExtension(linenums=False, css_class='highlight'),
            TableExtension(),
            'nl2br',  # newline to break
            'sane_lists',
            'toc'  # table of contents
        ]
        
        html = markdown.markdown(text, extensions=extensions)
        
        # Wrap the HTML content
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                {self.current_css}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Set the content
        self.setHtml(full_html, QUrl("file://"))
    
    def set_dark_mode(self, dark_mode):
        """Switch between light and dark mode"""
        self.is_dark_mode = dark_mode
        
        # Update the CSS based on the mode
        if dark_mode:
            self.current_css = self._get_dark_css()
        else:
            self.current_css = self._get_default_css()
        
        # Re-render the current content
        current_content = self.page().toHtml(lambda content: self.set_markdown(content))
    
    def set_zoom_factor(self, factor):
        """Set the zoom factor for the preview"""
        self.zoom_factor = factor
        super().setZoomFactor(factor)
    
    def print_(self, printer, html_content=None):
        """Print the current preview content"""
        if html_content:
            # Create a temporary QWebEngineView for printing
            print_view = QWebEngineView()
            print_view.setHtml(html_content)
            print_view.page().print(printer, lambda success: None)
        else:
            self.page().print(printer, lambda success: None) 