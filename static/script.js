// CSV Keywords Converter - Client-side processing
console.log('Keywords Converter loaded');

// CSV parsing functions
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = parseCSVLine(lines[0]);
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim()) {
            const row = parseCSVLine(lines[i]);
            if (row.length > 0) {
                const rowObj = {};
                headers.forEach((header, index) => {
                    rowObj[header] = row[index] || '';
                });
                data.push(rowObj);
            }
        }
    }
    
    return { headers, data };
}

function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current.trim());
    return result.map(item => item.replace(/^"|"$/g, ''));
}

function convertKeywordsNumbered(data, headers, keywordsCol) {
    // Split keywords by @@ delimiter and create a list for each row
    const keywordLists = [];
    let maxKeywords = 0;
    
    data.forEach(row => {
        const keywordsStr = row[keywordsCol] || '';
        const keywords = keywordsStr ? keywordsStr.split('@@').map(kw => kw.trim()).filter(kw => kw) : [];
        keywordLists.push(keywords);
        maxKeywords = Math.max(maxKeywords, keywords.length);
    });
    
    // Get columns to keep (excluding keywords column, Unnamed columns, and the first column since it becomes the empty column)
    const columnsToKeep = headers.filter((col, index) => 
        col !== keywordsCol && !col.toLowerCase().startsWith('unnamed') && index !== 0
    );
    
    // Create new headers with empty first column, then other columns, then numbered keyword columns
    const newHeaders = ['', ...columnsToKeep];
    for (let i = 0; i < maxKeywords; i++) {
        if (i === 0) {
            newHeaders.push(keywordsCol);
        } else {
            newHeaders.push(`${keywordsCol}_${i + 1}`);
        }
    }
    
    // Create new data rows
    const newData = data.map((row, index) => {
        const newRow = {};
        
        // First column value (from original first column)
        const firstColValue = row[headers[0]] || '';
        newRow[''] = firstColValue;
        
        // Copy other columns (excluding keywords and unnamed columns)
        columnsToKeep.forEach(header => {
            newRow[header] = row[header] || '';
        });
        
        // Add keyword columns with proper naming
        const keywords = keywordLists[index];
        for (let i = 0; i < maxKeywords; i++) {
            const keyHeader = i === 0 ? keywordsCol : `${keywordsCol}_${i + 1}`;
            newRow[keyHeader] = keywords[i] || '';
        }
        
        return newRow;
    });
    
    return { headers: newHeaders, data: newData, keywordCount: maxKeywords, isArray: false };
}

function convertKeywordsSameName(data, headers, keywordsCol) {
    // Split keywords by @@ delimiter and create a list for each row
    const keywordLists = [];
    let maxKeywords = 0;
    
    data.forEach(row => {
        const keywordsStr = row[keywordsCol] || '';
        const keywords = keywordsStr ? keywordsStr.split('@@').map(kw => kw.trim()).filter(kw => kw) : [];
        keywordLists.push(keywords);
        maxKeywords = Math.max(maxKeywords, keywords.length);
    });
    
    // Get other columns (excluding keywords column, Unnamed columns, and the first column since it becomes the empty column)
    const otherColumns = headers.filter((col, index) => 
        col !== keywordsCol && !col.toLowerCase().startsWith('unnamed') && index !== 0
    );
    
    // Create header row with empty first column, then other columns, then repeated keyword columns
    const newHeaders = ['', ...otherColumns, ...Array(maxKeywords).fill(keywordsCol)];
    
    // Create new data rows as arrays to handle duplicate column names
    const newData = data.map((row, rowIndex) => {
        const rowArray = [];
        
        // First column value (from original first column)
        const firstColValue = row[headers[0]] || '';
        rowArray.push(firstColValue);
        
        // Copy other columns (excluding keywords and unnamed columns)
        otherColumns.forEach(header => {
            rowArray.push(row[header] || '');
        });
        
        // Add keyword values
        const keywords = keywordLists[rowIndex];
        for (let i = 0; i < maxKeywords; i++) {
            rowArray.push(keywords[i] || '');
        }
        
        return rowArray;
    });
    
    return { headers: newHeaders, data: newData, keywordCount: maxKeywords, isArray: true };
}

function convertKeywords(data, headers, conversionType) {
    // Find keywords column (case insensitive)
    let keywordsCol = null;
    for (const header of headers) {
        if (header.toLowerCase().includes('asset_keywords')) {
            keywordsCol = header;
            break;
        }
    }
    
    if (!keywordsCol) {
        throw new Error('No asset_keywords column found. Please ensure your CSV has a column containing "asset_keywords" in its name.');
    }
    
    if (conversionType === 'numbered') {
        return convertKeywordsNumbered(data, headers, keywordsCol);
    } else {
        return convertKeywordsSameName(data, headers, keywordsCol);
    }
}

function arrayToCSV(headers, data, result) {
    const escapeCsvField = (field) => {
        if (field === null || field === undefined) field = '';
        field = String(field);
        if (field.includes(',') || field.includes('"') || field.includes('\n')) {
            field = '"' + field.replace(/"/g, '""') + '"';
        }
        return field;
    };
    
    // Write header
    let csv = headers.map(header => escapeCsvField(header)).join(',') + '\n';
    
    // Write data rows
    data.forEach(row => {
        let rowArray = [];
        
        if (result.isArray) {
            // Data is already in array format (for same-name columns)
            rowArray = row.map(field => escapeCsvField(field));
        } else {
            // Standard object-based data (for numbered columns)
            rowArray = headers.map(header => escapeCsvField(row[header] || ''));
        }
        
        csv += rowArray.join(',') + '\n';
    });
    
    return csv;
}

function downloadCSV(csvContent, filename) {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function showAlert(type, message) {
    const alertId = type === 'success' ? 'success-alert' : 'error-alert';
    const messageId = type === 'success' ? 'success-message' : 'error-message';
    
    document.getElementById(messageId).textContent = message;
    document.getElementById(alertId).style.display = 'block';
    
    // Auto-hide success alerts after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            document.getElementById(alertId).style.display = 'none';
        }, 5000);
    }
}

function hideAlerts() {
    document.getElementById('success-alert').style.display = 'none';
    document.getElementById('error-alert').style.display = 'none';
}

function showProgress(show) {
    const progressContainer = document.querySelector('.progress-container');
    if (show) {
        progressContainer.style.display = 'block';
        // Simulate progress
        const progressBar = progressContainer.querySelector('.progress-bar');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 100);
        
        return () => {
            clearInterval(interval);
            progressBar.style.width = '100%';
            setTimeout(() => {
                progressContainer.style.display = 'none';
                progressBar.style.width = '0%';
            }, 500);
        };
    } else {
        progressContainer.style.display = 'none';
    }
}

// DOM Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const convertBtn = document.getElementById('convert-btn');
    const uploadForm = document.getElementById('upload-form');
    const uploadText = document.getElementById('upload-text');
    const chooseFileBtn = document.getElementById('choose-file-btn');

    // File input change handler
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const fileName = this.files[0].name;
            uploadText.textContent = `Selected: ${fileName}`;
            convertBtn.disabled = false;
        }
    });

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].name.endsWith('.csv')) {
            fileInput.files = files;
            const fileName = files[0].name;
            uploadText.textContent = `Selected: ${fileName}`;
            convertBtn.disabled = false;
        } else {
            showAlert('error', 'Please drop a CSV file.');
        }
    });

    // Choose file button click handler
    chooseFileBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    });

    // Click to upload area (but not the button)
    uploadArea.addEventListener('click', function(e) {
        // Only trigger file input if the click wasn't on the button
        if (e.target !== chooseFileBtn && !chooseFileBtn.contains(e.target)) {
            fileInput.click();
        }
    });

    // Form submission handler
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showAlert('error', 'Please select a file.');
            return;
        }
        
        if (!file.name.endsWith('.csv')) {
            showAlert('error', 'Please select a CSV file.');
            return;
        }
        
        if (file.size > 10 * 1024 * 1024) {
            showAlert('error', 'File is too large. Maximum size is 10MB.');
            return;
        }
        
        hideAlerts();
        const finishProgress = showProgress(true);
        
        const conversionType = document.querySelector('input[name="conversion_type"]:checked').value;
        
        // Read file
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const csvText = e.target.result;
                const { headers, data } = parseCSV(csvText);
                
                if (data.length === 0) {
                    throw new Error('CSV file appears to be empty or invalid.');
                }
                
                const result = convertKeywords(data, headers, conversionType);
                const convertedCSV = arrayToCSV(result.headers, result.data, result);
                
                // Generate filename
                const originalName = file.name.replace('.csv', '');
                const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
                const newFilename = `${originalName}_converted_${timestamp}.csv`;
                
                // Download file
                downloadCSV(convertedCSV, newFilename);
                
                finishProgress();
                showAlert('success', 
                    `Conversion successful! Created ${result.keywordCount} keyword columns from ${data.length} rows.`
                );
                
            } catch (error) {
                finishProgress();
                showAlert('error', `Error processing file: ${error.message}`);
            }
        };
        
        reader.onerror = function() {
            finishProgress();
            showAlert('error', 'Error reading file. Please try again.');
        };
        
        reader.readAsText(file);
    });
});
