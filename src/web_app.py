from flask import Flask, request, send_file, render_template, flash, redirect, url_for
import pandas as pd
import csv
import os
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Configuration
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'csv'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_keywords_format_same_name(input_file, output_file):
    """Convert CSV from @@ delimited keywords to multiple ASSET_KEYWORDS columns"""
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Find the keywords column (case insensitive)
    keywords_col = None
    for col in df.columns:
        if 'keyword' in col.lower():
            keywords_col = col
            break
    
    if keywords_col is None:
        raise ValueError("No keywords column found. Please ensure your CSV has a column containing 'keyword' in its name.")
    
    # Split keywords by @@ delimiter
    keyword_lists = []
    max_keywords = 0
    
    for keywords_str in df[keywords_col]:
        if pd.isna(keywords_str) or keywords_str == '':
            keywords = []
        else:
            keywords = [kw.strip() for kw in str(keywords_str).split('@@') if kw.strip()]
        
        keyword_lists.append(keywords)
        max_keywords = max(max_keywords, len(keywords))
    
    # Get columns without the original keywords column
    other_columns = [col for col in df.columns if col != keywords_col]
    
    # Create header row with repeated keywords columns
    header = other_columns + [keywords_col] * max_keywords
    
    # Write CSV manually to allow duplicate column names
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        
        for index, row in df.iterrows():
            row_data = [row[col] for col in other_columns]
            keywords = keyword_lists[index]
            
            for i in range(max_keywords):
                if i < len(keywords):
                    row_data.append(keywords[i])
                else:
                    row_data.append('')
            
            writer.writerow(row_data)
    
    return max_keywords, len(df)

def convert_keywords_format_numbered(input_file, output_file):
    """Convert CSV from @@ delimited keywords to numbered keyword columns"""
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Find the keywords column (case insensitive)
    keywords_col = None
    for col in df.columns:
        if 'keyword' in col.lower():
            keywords_col = col
            break
    
    if keywords_col is None:
        raise ValueError("No keywords column found. Please ensure your CSV has a column containing 'keyword' in its name.")
    
    # Split keywords by @@ delimiter
    keyword_lists = []
    max_keywords = 0
    
    for keywords_str in df[keywords_col]:
        if pd.isna(keywords_str) or keywords_str == '':
            keywords = []
        else:
            keywords = [kw.strip() for kw in str(keywords_str).split('@@') if kw.strip()]
        
        keyword_lists.append(keywords)
        max_keywords = max(max_keywords, len(keywords))
    
    # Create new dataframe without original keywords column
    new_df = df.drop(keywords_col, axis=1).copy()
    
    # Add numbered keyword columns
    for i in range(max_keywords):
        if i == 0:
            col_name = keywords_col
        else:
            col_name = f'{keywords_col}_{i+1}'
        
        new_df[col_name] = [kw_list[i] if i < len(kw_list) else '' for kw_list in keyword_lists]
    
    new_df.to_csv(output_file, index=False)
    return max_keywords, len(df)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    conversion_type = request.form.get('conversion_type', 'same_name')
    
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            input_path = os.path.join(UPLOAD_FOLDER, f"{timestamp}_{filename}")
            file.save(input_path)
            
            # Generate output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_converted_{timestamp}{ext}"
            output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)
            
            # Convert file
            if conversion_type == 'same_name':
                max_keywords, total_rows = convert_keywords_format_same_name(input_path, output_path)
            else:
                max_keywords, total_rows = convert_keywords_format_numbered(input_path, output_path)
            
            # Clean up input file
            os.remove(input_path)
            
            flash(f'Conversion successful! Created {max_keywords} keyword columns from {total_rows} rows.')
            return send_file(output_path, as_attachment=True, download_name=output_filename)
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a CSV file.')
    return redirect(url_for('index'))

@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True)