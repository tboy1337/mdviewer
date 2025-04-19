import os
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension

from PyQt6.QtCore import QUrl, QMarginsF, QSize, QEventLoop
from PyQt6.QtGui import QPainter, QPageLayout, QPageSize
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

class HTMLExporter:
    """Exports Markdown content to HTML"""
    
    def __init__(self):
        pass
    
    def export(self, markdown_text):
        """Convert markdown to HTML and return it"""
        html_content = self.markdown_to_html(markdown_text)
        return html_content
    
    def markdown_to_html(self, markdown_text):
        """Convert markdown to HTML with full styling"""
        # Process markdown to HTML
        extensions = [
            FencedCodeExtension(),
            CodeHiliteExtension(linenums=False, css_class='highlight'),
            TableExtension(),
            'nl2br',  # newline to break
            'sane_lists',
            'toc'  # table of contents
        ]
        
        html = markdown.markdown(markdown_text, extensions=extensions)
        
        # Add CSS styling
        css = self._get_css()
        
        # Wrap with HTML document structure
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Markdown Export</title>
            <style>
                {css}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return full_html
    
    def _get_css(self):
        """Get the CSS to style the exported HTML"""
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


class PDFExporter:
    """Exports Markdown content to PDF"""
    
    def __init__(self):
        self.html_exporter = HTMLExporter()
    
    def export(self, markdown_text, output_path):
        """Convert markdown to PDF and save to file"""
        html_content = self.markdown_to_html(markdown_text)
        
        # Create a printer object
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(output_path)
        
        # Set page layout
        layout = QPageLayout()
        layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        margins = QMarginsF(20, 20, 20, 20)  # left, top, right, bottom
        layout.setMargins(margins)
        printer.setPageLayout(layout)
        
        # Create a web view to render the HTML
        view = QWebEngineView()
        view.setHtml(html_content, QUrl("file://"))
        
        # Create event loop to wait for page load
        loop = QEventLoop()
        
        # Print to PDF when page is loaded
        view.loadFinished.connect(lambda ok: self._on_load_finished(ok, view, printer, loop))
        
        # Run the event loop until the page is loaded and printed
        loop.exec()
        
        return True
    
    def markdown_to_html(self, markdown_text):
        """Convert markdown to HTML using the HTML exporter"""
        return self.html_exporter.markdown_to_html(markdown_text)
    
    def _on_load_finished(self, ok, view, printer, loop):
        """Called when the page has finished loading"""
        if ok:
            view.page().print(printer, lambda success: loop.quit())
        else:
            loop.quit() 