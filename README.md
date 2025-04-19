# MDViewer

A cross-platform Markdown viewer application built with Python.

## Features

- Standard Markdown + GitHub Flavored Markdown support
- Dual view with adjustable split panes (editor/preview)
- Real-time preview with syntax highlighting
- Document outline navigation
- File operations:
  - Open local files
  - Open markdown from URLs
  - Recent files list
  - Drag-and-drop file opening
- Theming:
  - Light/dark mode toggle
  - Syntax highlighting
- Export options:
  - HTML export
  - PDF export
  - Printing
- Advanced editing:
  - Search functionality
  - Adjustable font size
  - Keyboard shortcuts
- Cross-platform compatibility (Windows, macOS, Linux)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/tboy1337/MDViewer.git
   cd MDViewer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## Usage

- **Open a file**: Use the File menu or press `Ctrl+O`
- **Open from URL**: Use the File menu or press `Ctrl+U`
- **Toggle theme**: Click the theme button in the toolbar or use the View menu
- **Change view mode**: Use the editor/split/preview buttons or View menu
- **Adjust font size**: Use the `A+`/`A-` buttons or `Ctrl+/Ctrl-` keys
- **Toggle outline**: Click the outline button or press `Ctrl+L`
- **Search**: Enter text in the search box and use the navigation arrows 