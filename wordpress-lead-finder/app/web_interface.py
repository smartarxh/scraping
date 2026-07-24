"""
Flask web interface for WordPress Lead Finder
"""

import os
import sys
from flask import Flask, render_template_string, request, jsonify

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import LeadFinder
from app.config import OUTPUT_DIR


app = Flask(__name__)

# Store current job state
current_job = {
    'status': 'idle',
    'keyword': '',
    'progress': 0,
    'message': '',
    'stats': {},
    'leads': [],
    'output_dir': ''
}


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WordPress Lead Finder</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        
        input[type="text"],
        input[type="number"] {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        
        .status-section.active {
            display: block;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 15px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            text-align: center;
        }
        
        .message.info {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .message.success {
            background: #e8f5e9;
            color: #388e3c;
        }
        
        .results-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        
        .results-section.active {
            display: block;
        }
        
        .download-links {
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }
        
        .download-btn {
            flex: 1;
            padding: 12px;
            background: #4caf50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            font-weight: 600;
        }
        
        .download-btn:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 WordPress Lead Finder</h1>
        <p class="subtitle">Find WordPress websites with contact information</p>
        
        <form id="searchForm">
            <div class="form-group">
                <label for="keyword">Keyword:</label>
                <input type="text" id="keyword" name="keyword" placeholder="plumber in new york" required>
            </div>
            
            <div class="form-group">
                <label for="max_websites">Maximum Websites:</label>
                <input type="number" id="max_websites" name="max_websites" value="100" min="10" max="500">
            </div>
            
            <button type="submit" class="btn" id="startBtn">🚀 START SEARCH</button>
        </form>
        
        <div class="status-section" id="statusSection">
            <h3>Status:</h3>
            <div class="message info" id="statusMessage">Initializing...</div>
            
            <div class="progress-bar">
                <div class="progress-fill" id="progressBar">0%</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="statWebsites">0</div>
                    <div class="stat-label">Websites Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statWordpress">0</div>
                    <div class="stat-label">WordPress Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statEmails">0</div>
                    <div class="stat-label">Emails Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="statPhones">0</div>
                    <div class="stat-label">Phones Found</div>
                </div>
            </div>
        </div>
        
        <div class="results-section" id="resultsSection">
            <h3>✅ Search Completed!</h3>
            <p>Found <strong id="resultCount">0</strong> WordPress leads.</p>
            <div class="download-links">
                <a href="#" class="download-btn" id="excelLink">📊 Download Excel</a>
                <a href="#" class="download-btn" id="csvLink">📄 Download CSV</a>
            </div>
        </div>
    </div>
    
    <script>
        let pollingInterval = null;
        
        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const keyword = document.getElementById('keyword').value;
            const maxWebsites = parseInt(document.getElementById('max_websites').value);
            
            // Start the search
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ keyword, max_websites: maxWebsites })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show status section
                document.getElementById('statusSection').classList.add('active');
                document.getElementById('startBtn').disabled = true;
                
                // Start polling for progress
                startPolling();
            } else {
                alert('Error: ' + result.error);
            }
        });
        
        function startPolling() {
            pollingInterval = setInterval(async () => {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update status
                document.getElementById('statusMessage').textContent = data.message;
                document.getElementById('progressBar').style.width = data.progress + '%';
                document.getElementById('progressBar').textContent = data.progress + '%';
                
                // Update stats
                document.getElementById('statWebsites').textContent = data.stats.websites_found || 0;
                document.getElementById('statWordpress').textContent = data.stats.wordpress_found || 0;
                document.getElementById('statEmails').textContent = data.stats.emails_found || 0;
                document.getElementById('statPhones').textContent = data.stats.phones_found || 0;
                
                // Check if complete
                if (data.status === 'completed') {
                    clearInterval(pollingInterval);
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('resultCount').textContent = data.leads.length;
                    
                    // Show download links
                    document.getElementById('resultsSection').classList.add('active');
                    document.getElementById('excelLink').href = '/download/' + encodeURIComponent(data.keyword) + '.xlsx';
                    document.getElementById('csvLink').href = '/download/' + encodeURIComponent(data.keyword) + '.csv';
                }
            }, 1000);
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/start', methods=['POST'])
def start_search():
    """Start a new lead search job."""
    global current_job
    
    data = request.get_json()
    keyword = data.get('keyword', '')
    max_websites = data.get('max_websites', 100)
    
    if not keyword:
        return jsonify({'success': False, 'error': 'Keyword is required'})
    
    # Reset job state
    current_job = {
        'status': 'running',
        'keyword': keyword,
        'progress': 0,
        'message': 'Starting search...',
        'stats': {},
        'leads': [],
        'output_dir': ''
    }
    
    # Create finder instance
    finder = LeadFinder(max_websites=max_websites)
    
    def progress_callback(message, progress):
        current_job['message'] = message
        current_job['progress'] = progress
        current_job['stats'] = finder.get_stats()
    
    # Run search in background
    def run_search():
        global current_job
        try:
            leads, output_dir = finder.find_leads(keyword, progress_callback)
            current_job['leads'] = leads
            current_job['output_dir'] = output_dir
            current_job['status'] = 'completed'
            current_job['progress'] = 100
            finder.close()
        except Exception as e:
            current_job['status'] = 'error'
            current_job['message'] = f'Error: {str(e)}'
            finder.close()
    
    import threading
    thread = threading.Thread(target=run_search)
    thread.start()
    
    return jsonify({'success': True})


@app.route('/api/status')
def get_status():
    """Get current job status."""
    global current_job
    return jsonify(current_job)


@app.route('/download/<filename>')
def download_file(filename):
    """Download a file from the output directory."""
    from flask import send_from_directory
    
    # Get the keyword from the current job or extract from filename
    keyword = current_job.get('keyword', '')
    safe_keyword = filename.replace('.xlsx', '').replace('.csv', '')
    
    output_dir = os.path.join(OUTPUT_DIR, safe_keyword)
    
    if os.path.exists(output_dir):
        return send_from_directory(output_dir, filename, as_attachment=True)
    
    return jsonify({'error': 'File not found'}), 404


if __name__ == '__main__':
    print("=" * 50)
    print("   WORDPRESS LEAD FINDER")
    print("=" * 50)
    print("\nStarting web interface...")
    print("Open http://localhost:5000 in your browser\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
