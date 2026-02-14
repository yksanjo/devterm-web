"""DevTerm Web - Flask web application."""

from flask import Flask, render_template_string, request, jsonify
import json
import base64
import urllib.parse
import html
import hashlib
import uuid
import re
import socket
import time
import io
import qrcode
import yaml
import xmltodict
import requests

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevTerm Web - Developer Tools</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #e6edf3; min-height: 100vh; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #58a6ff; margin-bottom: 30px; font-size: 2rem; }
        .tools-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 40px; }
        .tool-card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 20px; cursor: pointer; transition: all 0.2s; }
        .tool-card:hover { border-color: #58a6ff; transform: translateY(-2px); }
        .tool-card h3 { color: #58a6ff; margin-bottom: 8px; }
        .tool-card p { color: #8b949e; font-size: 0.9rem; }
        .tool-section { display: none; margin-top: 30px; }
        .tool-section.active { display: block; }
        .tool-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .tool-header h2 { color: #58a6ff; }
        .back-btn { background: #21262d; color: #e6edf3; border: 1px solid #30363d; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
        .back-btn:hover { background: #30363d; }
        textarea, input, select { width: 100%; background: #0d1117; border: 1px solid #30363d; color: #e6edf3; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 14px; margin-bottom: 16px; }
        textarea:focus, input:focus, select:focus { outline: none; border-color: #58a6ff; }
        textarea { min-height: 150px; resize: vertical; }
        .btn { background: #238636; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 600; }
        .btn:hover { background: #2ea043; }
        .btn-secondary { background: #21262d; }
        .btn-secondary:hover { background: #30363d; }
        .output { background: #161b22; border: 1px solid #30363d; padding: 16px; border-radius: 6px; min-height: 100px; white-space: pre-wrap; font-family: monospace; overflow-x: auto; }
        .error { color: #f85149; }
        .success { color: #7ee787; }
        .row { display: flex; gap: 16px; }
        .col { flex: 1; }
        label { display: block; margin-bottom: 8px; color: #8b949e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DevTerm Web - Developer Tools</h1>
        
        <div id="tools-grid" class="tools-grid">
            <!-- JSON Tools -->
            <div class="tool-card" onclick="showTool('json-formatter')">
                <h3>📄 JSON Formatter</h3>
                <p>Format, validate, minify JSON</p>
            </div>
            <div class="tool-card" onclick="showTool('base64')">
                <h3>🔐 Base64</h3>
                <p>Encode/decode Base64</p>
            </div>
            <div class="tool-card" onclick="showTool('url')">
                <h3>🔗 URL Encode</h3>
                <p>URL encode/decode</p>
            </div>
            <div class="tool-card" onclick="showTool('hash')">
                <h3>🔒 Hash Generator</h3>
                <p>MD5, SHA-256, SHA-512</p>
            </div>
            <div class="tool-card" onclick="showTool('uuid')">
                <h3>🆔 UUID Generator</h3>
                <p>Generate UUIDs</p>
            </div>
            <div class="tool-card" onclick="showTool('password')">
                <h3>🔑 Password</h3>
                <p>Generate secure passwords</p>
            </div>
            <div class="tool-card" onclick="showTool('qrcode')">
                <h3>📱 QR Code</h3>
                <p>Generate QR codes</p>
            </div>
            <div class="tool-card" onclick="showTool('http')">
                <h3>🌐 HTTP Client</h3>
                <p>Make HTTP requests</p>
            </div>
            <div class="tool-card" onclick="showTool('case')">
                <h3>Aa Case Converter</h3>
                <p>Convert text case</p>
            </div>
            <div class="tool-card" onclick="showTool('timestamp')">
                <h3>⏰ Timestamp</h3>
                <p>Unix timestamp converter</p>
            </div>
        </div>

        <!-- JSON Formatter -->
        <div id="json-formatter" class="tool-section">
            <div class="tool-header">
                <h2>JSON Formatter</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <textarea id="json-input" placeholder="Paste your JSON here..."></textarea>
            <div>
                <button class="btn" onclick="formatJson()">Format</button>
                <button class="btn btn-secondary" onclick="minifyJson()">Minify</button>
            </div>
            <div id="json-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- Base64 -->
        <div id="base64" class="tool-section">
            <div class="tool-header">
                <h2>Base64 Encoder/Decoder</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <textarea id="base64-input" placeholder="Enter text..."></textarea>
            <div>
                <button class="btn" onclick="base64Encode()">Encode</button>
                <button class="btn btn-secondary" onclick="base64Decode()">Decode</button>
            </div>
            <div id="base64-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- URL Encode -->
        <div id="url" class="tool-section">
            <div class="tool-header">
                <h2>URL Encoder/Decoder</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <textarea id="url-input" placeholder="Enter text..."></textarea>
            <div>
                <button class="btn" onclick="urlEncode()">Encode</button>
                <button class="btn btn-secondary" onclick="urlDecode()">Decode</button>
            </div>
            <div id="url-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- Hash -->
        <div id="hash" class="tool-section">
            <div class="tool-header">
                <h2>Hash Generator</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <textarea id="hash-input" placeholder="Enter text to hash..."></textarea>
            <button class="btn" onclick="generateHash()">Generate Hashes</button>
            <div id="hash-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- UUID -->
        <div id="uuid" class="tool-section">
            <div class="tool-header">
                <h2>UUID Generator</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <button class="btn" onclick="generateUuid()">Generate UUID</button>
            <div id="uuid-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- Password -->
        <div id="password" class="tool-section">
            <div class="tool-header">
                <h2>Password Generator</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <label>Length: <input type="number" id="pw-length" value="16" min="4" max="128"></label>
            <label><input type="checkbox" id="pw-upper" checked> Uppercase (A-Z)</label>
            <label><input type="checkbox" id="pw-lower" checked> Lowercase (a-z)</label>
            <label><input type="checkbox" id="pw-digits" checked> Digits (0-9)</label>
            <label><input type="checkbox" id="pw-special" checked> Special (!@#$...)</label>
            <button class="btn" onclick="generatePassword()">Generate</button>
            <div id="password-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- QR Code -->
        <div id="qrcode" class="tool-section">
            <div class="tool-header">
                <h2>QR Code Generator</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <textarea id="qr-input" placeholder="Enter text or URL..."></textarea>
            <button class="btn" onclick="generateQr()">Generate QR Code</button>
            <div id="qr-output" style="margin-top: 16px;"></div>
        </div>

        <!-- HTTP Client -->
        <div id="http" class="tool-section">
            <div class="tool-header">
                <h2>HTTP Client</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <input type="text" id="http-url" placeholder="https://api.example.com">
            <select id="http-method">
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="PUT">PUT</option>
                <option value="DELETE">DELETE</option>
            </select>
            <textarea id="http-body" placeholder="Request body (optional)"></textarea>
            <button class="btn" onclick="makeRequest()">Send Request</button>
            <div id="http-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- Case Converter -->
        <div id="case" class="tool-section">
            <div class="tool-header">
                <h2>Case Converter</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <textarea id="case-input" placeholder="Enter text..."></textarea>
            <select id="case-type">
                <option value="upper">UPPERCASE</option>
                <option value="lower">lowercase</option>
                <option value="title">Title Case</option>
                <option value="camel">camelCase</option>
                <option value="snake">snake_case</option>
                <option value="kebab">kebab-case</option>
            </select>
            <button class="btn" onclick="convertCase()">Convert</button>
            <div id="case-output" class="output" style="margin-top: 16px;"></div>
        </div>

        <!-- Timestamp -->
        <div id="timestamp" class="tool-section">
            <div class="tool-header">
                <h2>Timestamp Converter</h2>
                <button class="back-btn" onclick="showTool('')">← Back</button>
            </div>
            <button class="btn" onclick="showTimestamp()">Show Current Time</button>
            <div id="timestamp-output" class="output" style="margin-top: 16px;"></div>
        </div>
    </div>

    <script>
        function showTool(tool) {
            document.querySelectorAll('.tool-section').forEach(el => el.classList.remove('active'));
            document.getElementById('tools-grid').style.display = tool ? 'none' : 'grid';
            if (tool) document.getElementById(tool).classList.add('active');
        }

        async function formatJson() {
            const input = document.getElementById('json-input').value;
            const response = await fetch('/api/json/format', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({data: input, mode: 'format'})
            });
            const result = await response.json();
            document.getElementById('json-output').textContent = result.output || result.error;
            document.getElementById('json-output').className = 'output ' + (result.success ? 'success' : 'error');
        }

        async function minifyJson() {
            const input = document.getElementById('json-input').value;
            const response = await fetch('/api/json/format', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({data: input, mode: 'minify'})
            });
            const result = await response.json();
            document.getElementById('json-output').textContent = result.output || result.error;
            document.getElementById('json-output').className = 'output ' + (result.success ? 'success' : 'error');
        }

        async function base64Encode() {
            const input = document.getElementById('base64-input').value;
            const response = await fetch('/api/base64/encode', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input})});
            const result = await response.json();
            document.getElementById('base64-output').textContent = result.output || result.error;
        }

        async function base64Decode() {
            const input = document.getElementById('base64-input').value;
            const response = await fetch('/api/base64/decode', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input})});
            const result = await response.json();
            document.getElementById('base64-output').textContent = result.output || result.error;
        }

        async function urlEncode() {
            const input = document.getElementById('url-input').value;
            const response = await fetch('/api/url/encode', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input})});
            const result = await response.json();
            document.getElementById('url-output').textContent = result.output || result.error;
        }

        async function urlDecode() {
            const input = document.getElementById('url-input').value;
            const response = await fetch('/api/url/decode', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input})});
            const result = await response.json();
            document.getElementById('url-output').textContent = result.output || result.error;
        }

        async function generateHash() {
            const input = document.getElementById('hash-input').value;
            const response = await fetch('/api/hash', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input})});
            const result = await response.json();
            document.getElementById('hash-output').textContent = result.output || result.error;
        }

        function generateUuid() {
            document.getElementById('uuid-output').textContent = crypto.randomUUID();
            document.getElementById('uuid-output').className = 'output success';
        }

        async function generatePassword() {
            const length = document.getElementById('pw-length').value;
            const upper = document.getElementById('pw-upper').checked;
            const lower = document.getElementById('pw-lower').checked;
            const digits = document.getElementById('pw-digits').checked;
            const special = document.getElementById('pw-special').checked;
            
            const response = await fetch('/api/password', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({length, uppercase: upper, lowercase: lower, digits: digits, special: special})
            });
            const result = await response.json();
            document.getElementById('password-output').textContent = result.output || result.error;
        }

        async function generateQr() {
            const input = document.getElementById('qr-input').value;
            const response = await fetch('/api/qrcode', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input})});
            const result = await response.json();
            if (result.success) {
                document.getElementById('qr-output').innerHTML = '<img src="' + result.image + '" alt="QR Code">';
            } else {
                document.getElementById('qr-output').textContent = result.error;
            }
        }

        async function makeRequest() {
            const url = document.getElementById('http-url').value;
            const method = document.getElementById('http-method').value;
            const body = document.getElementById('http-body').value;
            
            const response = await fetch('/api/http', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url, method, body})
            });
            const result = await response.json();
            document.getElementById('http-output').textContent = result.output || result.error;
        }

        async function convertCase() {
            const input = document.getElementById('case-input').value;
            const caseType = document.getElementById('case-type').value;
            const response = await fetch('/api/case', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: input, type: caseType})});
            const result = await response.json();
            document.getElementById('case-output').textContent = result.output || result.error;
        }

        function showTimestamp() {
            const now = new Date();
            document.getElementById('timestamp-output').innerHTML = 
                'Unix: ' + Math.floor(now.getTime() / 1000) + '<br>' +
                'ISO: ' + now.toISOString() + '<br>' +
                'Local: ' + now.toString();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# API Routes
@app.route('/api/json/format', methods=['POST'])
def json_format():
    data = request.json.get('data', '')
    mode = request.json.get('mode', 'format')
    try:
        parsed = json.loads(data)
        if mode == 'minify':
            return jsonify({'success': True, 'output': json.dumps(parsed, separators=(',', ':'))})
        return jsonify({'success': True, 'output': json.dumps(parsed, indent=2)})
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/base64/encode', methods=['POST'])
def base64_encode():
    data = request.json.get('data', '')
    return jsonify({'success': True, 'output': base64.b64encode(data.encode()).decode()})

@app.route('/api/base64/decode', methods=['POST'])
def base64_decode():
    data = request.json.get('data', '')
    try:
        return jsonify({'success': True, 'output': base64.b64decode(data.encode()).decode()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/url/encode', methods=['POST'])
def url_encode():
    data = request.json.get('data', '')
    return jsonify({'success': True, 'output': urllib.parse.quote(data, safe='')})

@app.route('/api/url/decode', methods=['POST'])
def url_decode():
    data = request.json.get('data', '')
    return jsonify({'success': True, 'output': urllib.parse.unquote(data)})

@app.route('/api/hash', methods=['POST'])
def hash_data():
    data = request.json.get('data', '')
    output = f'MD5: {hashlib.md5(data.encode()).hexdigest()}\n'
    output += f'SHA-256: {hashlib.sha256(data.encode()).hexdigest()}\n'
    output += f'SHA-512: {hashlib.sha512(data.encode()).hexdigest()}'
    return jsonify({'success': True, 'output': output})

@app.route('/api/password', methods=['POST'])
def password_gen():
    import secrets
    length = int(request.json.get('length', 16))
    chars = ''
    if request.json.get('uppercase'): chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if request.json.get('lowercase'): chars += 'abcdefghijklmnopqrstuvwxyz'
    if request.json.get('digits'): chars += '0123456789'
    if request.json.get('special'): chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    if not chars:
        return jsonify({'success': False, 'error': 'Select at least one character type'})
    
    password = ''.join(secrets.choice(chars) for _ in range(length))
    return jsonify({'success': True, 'output': password})

@app.route('/api/qrcode', methods=['POST'])
def qr_code():
    data = request.json.get('data', '')
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({'success': True, 'image': f'data:image/png;base64,{img_str}'})

@app.route('/api/http', methods=['POST'])
def http_request():
    url = request.json.get('url', '')
    method = request.json.get('method', 'GET')
    body = request.json.get('body', '')
    
    try:
        kwargs = {'method': method, 'url': url, 'timeout': 30}
        if body and method in ['POST', 'PUT']:
            kwargs['data'] = body
        
        response = requests.request(**kwargs)
        output = f'Status: {response.status_code}\n\nHeaders:\n'
        for k, v in response.headers.items():
            output += f'{k}: {v}\n'
        output += f'\nBody:\n{response.text[:2000]}'
        return jsonify({'success': True, 'output': output})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/case', methods=['POST'])
def case_convert():
    data = request.json.get('data', '')
    case_type = request.json.get('type', 'lower')
    
    if case_type == 'upper':
        output = data.upper()
    elif case_type == 'lower':
        output = data.lower()
    elif case_type == 'title':
        output = data.title()
    elif case_type == 'camel':
        words = re.findall(r'[A-Za-z]+', data)
        output = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    elif case_type == 'snake':
        output = re.sub(r'[\W]+', '_', data).lower().strip('_')
    elif case_type == 'kebab':
        output = re.sub(r'[\W]+', '-', data).lower().strip('-')
    else:
        output = data
    
    return jsonify({'success': True, 'output': output})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
