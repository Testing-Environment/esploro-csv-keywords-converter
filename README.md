# CSV Keywords Converter

Convert CSV files from @@ delimited keywords to multiple columns format.

## 🌐 Live Web App
Visit the live converter: **[CSV Keywords Converter](https://testing-environment.github.io/esploro-csv-keywords-converter/)**

## Features
- 📊 Convert @@ delimited keywords to separate columns
- 🌐 Web interface for easy file conversion (works offline!)
- 🖥️ Command line tool for batch processing
- ⚡ Client-side processing (no data uploaded to servers)
- 🔒 Privacy-focused (files processed in your browser)
- 📱 Mobile-friendly responsive design
- Support for both numbered and same-name columns

## How to Use
1. Visit the web app or open `index.html` locally
2. Upload your CSV file (or drag and drop)
3. Choose conversion type (same column names or numbered)
4. Click convert and download the result

## File Requirements
- CSV format with a column containing "keyword" in the name
- Keywords separated by @@ delimiter
- Maximum file size: 10MB

## Development
- `src/` - Original Flask application and Python processing logic
- `index.html` & `help.html` - Static web interface
- `static/` - CSS and JavaScript files
- `.github/workflows/` - Automated deployment to GitHub Pages

## Esploro Support Team | Copyright 2025
https://github.com/Testing-Environment/esploro-csv-keywords-converter
