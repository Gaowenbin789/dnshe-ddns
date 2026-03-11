#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNSHE DDNS 后台管理系统
提供 Web 界面进行配置管理、日志查看和服务控制
"""

from flask import Flask, render_template_string, request, jsonify, Response
import os
import subprocess
import configparser
import time
from datetime import datetime
from pathlib import Path
import threading
import signal

app = Flask(__name__)

# 路径配置 - 使用正确的路径
CONFIG_PATH = '/mnt/data/ddns_config.ini'
LOG_FILE = '/mnt/data/ddns-dnshe/logs/ddns.log'
PID_FILE = '/home/admin/ddns_ddns.pid'  # 改到家目录
START_SCRIPT = '/home/admin/dnshe-ddns/app/ddns-dnshe/scripts/start.sh'
STOP_SCRIPT = '/home/admin/dnshe-ddns/app/ddns-dnshe/scripts/stop.sh'

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DNSHE DDNS 后台管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        header h1 { font-size: 2em; margin-bottom: 15px; }
        #status-bar {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
            font-size: 1.1em;
        }
        .status-label { margin-right: 10px; }
        .status-indicator {
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
        }
        .status-running {
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        .status-stopped { background: #f44336; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        .pid-info { margin-left: 15px; opacity: 0.9; }
        .control-panel {
            padding: 30px;
            background: #f5f5f5;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .btn-success { background: #4CAF50; color: white; }
        .btn-danger { background: #f44336; color: white; }
        .btn-warning { background: #ff9800; color: white; }
        .btn-info { background: #2196F3; color: white; }
        .btn-secondary { background: #757575; color: white; }
        section { padding: 30px; border-bottom: 1px solid #e0e0e0; }
        h2 { color: #333; margin-bottom: 20px; font-size: 1.5em; }
        h3 { color: #555; margin-bottom: 15px; font-size: 1.2em; }
        .config-group {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
        }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .form-group input[readonly] { background: #e0e0e0; cursor: not-allowed; }
        .form-actions { display: flex; gap: 10px; }
        .logs-section { background: #fafafa; }
        .log-controls {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .auto-refresh-label {
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }
        #log-container {
            background: #1e1e1e;
            border-radius: 8px;
            padding: 15px;
            max-height: 500px;
            overflow-y: auto;
        }
        #log-content {
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #757575;
        }
        .message {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s;
        }
        .message.success { background: #4CAF50; }
        .message.error { background: #f44336; }
        .message.info { background: #2196F3; }
        @keyframes slideIn {
            from { transform: translateX(400px); }
            to { transform: translateX(0); }
        }
        @media (max-width: 768px) {
            body { padding: 10px; }
            header h1 { font-size: 1.5em; }
            .control-panel { flex-direction: column; }
            .btn { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 DNSHE DDNS 后台管理系统</h1>
            <div id="status-bar">
                <span class="status-label">服务状态：</span>
                <span id="service-status" class="status-indicator">加载中...</span>
                <span id="pid-info" class="pid-info"></span>
            </div>
        </header>
        <section class="control-panel">
            <button class="btn btn-success" onclick="startService()">▶️ 启动</button>
            <button class="btn btn-danger" onclick="stopService()">⏹️ 停止</button>
            <button class="btn btn-warning" onclick="restartService()">🔄 重启</button>
            <button class="btn btn-info" onclick="checkStatus()">🔄 刷新状态</button>
        </section>
        <section class="config-section">
            <h2>⚙️ 配置管理</h2>
            <form id="config-form">
                <div class="config-group">
                    <h3>DNSHE API 配置</h3>
                    <div class="form-group">
                        <label for="api-key">API Key:</label>
                        <input type="text" id="api-key" name="api_key" required>
                    </div>
                    <div class="form-group">
                        <label for="api-secret">API Secret:</label>
                        <input type="text" id="api-secret" name="api_secret" required>
                    </div>
                    <div class="form-group">
                        <label for="subdomain-id">域名 ID (Subdomain ID):</label>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <input type="number" id="subdomain-id" name="subdomain_id" required style="flex: 1;">
                            <button type="button" class="btn btn-info" onclick="autoFetchSubdomains()" style="padding: 10px 20px; white-space: nowrap;">🔍 自动获取</button>
                        </div>
                        <small style="color: #757575; display: block; margin-top: 5px;">点击"自动获取"按钮，根据 API Key 和 API Secret 自动获取子域名列表</small>
                    </div>

                </div>
                <div class="config-group">
                    <h3>系统设置</h3>
                    <div class="form-group">
                        <label for="check-interval">检查间隔 (秒):</label>
                        <input type="number" id="check-interval" name="check_interval" value="30" required>
                    </div>
                    <div class="form-group">
                        <label for="dns-ttl">DNS TTL (秒):</label>
                        <input type="number" id="dns-ttl" name="dns_ttl" value="600" required>
                    </div>
                    <div class="form-group">
                        <label for="log-file">日志路径:</label>
                        <input type="text" id="log-file" name="log_file" readonly>
                    </div>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">💾 保存配置</button>
                    <button type="button" class="btn btn-secondary" onclick="loadConfig()">重新加载</button>
                </div>
            </form>
        </section>
        <section class="logs-section">
            <h2>📋 实时日志 <span id="log-lines-count">(0 行)</span></h2>
            <div class="log-controls">
                <button class="btn btn-sm btn-info" onclick="loadLogs()">🔄 刷新日志</button>
                <button class="btn btn-sm btn-danger" onclick="clearLogs()">🗑️ 清空日志</button>
                <label class="auto-refresh-label">
                    <input type="checkbox" id="auto-refresh" checked> 自动刷新
                </label>
            </div>
            <div id="log-container">
                <pre id="log-content">加载中...</pre>
            </div>
        </section>
        <footer><p>DNSHE DDNS 后台管理系统 &copy; 2026</p></footer>
    </div>
    <script src="/static/script.js"></script>
</body>
</html>'''


def fix_config():
    # 注意：实际使用时需要手动创建配置文件
    # 不要在代码中硬编码 API 密钥
    pass

def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH, encoding='utf-8')
    return config

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        config.write(f)

def get_service_status():
    """获取服务状态 - 通过 ps 命令查找"""
    try:
        # 使用 ps 查找 ddns_dnshe 进程（排除 ddns_web）
        result = subprocess.run(
            ['ps', 'aux'], 
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if 'ddns' in line and 'ddns_web' not in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = int(parts[1])
                        return {'status': 'running', 'pid': pid}
        return {'status': 'stopped', 'pid': None}
    except Exception as e:
        return {'status': 'error', 'pid': None, 'message': str(e)}

def execute_script(script_path):
    """执行脚本"""
    try:
        result = subprocess.run(['bash', script_path], capture_output=True, text=True, timeout=30)
        return {'success': result.returncode == 0, 'output': result.stdout, 'error': result.stderr}
    except subprocess.TimeoutExpired:
        return {'success': False, 'output': '', 'error': '脚本执行超时'}
    except Exception as e:
        return {'success': False, 'output': '', 'error': str(e)}

@app.route('/test_config.html')
def test_config():
    return render_template_string(TEST_CONFIG_HTML)

@app.route('/test_config2.html')
def test_config2():
    """测试页面 2 - 简化版"""
    html = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>配置测试</title>
<style>body{font-family:Arial;padding:20px}button{padding:10px;margin:5px;font-size:16px}.result{background:#f0f0f0;padding:15px;margin:10px 0;border-radius:5px}</style>
</head><body>
<h1>DNSHE DDNS 配置测试</h1>
<button onclick="testConfig()">🔄 测试获取配置</button>
<button onclick="testStatus()">📊 测试状态</button>
<div id="output"></div>
<script>
async function testConfig(){
    try{
        const r=await fetch('/api/config');
        const d=await r.json();
        document.getElementById('output').innerHTML='<div class="result"><h3>✅ 配置 API 正常</h3><pre>'+JSON.stringify(d,null,2)+'</pre></div>';
        if(d.success&&d.config){
            document.getElementById('output').innerHTML+='<div class="result"><b>API Key:</b> '+d.config.dnshe.api_key+'<br><b>Subdomain ID:</b> '+d.config.dnshe.subdomain_id+'<br><b>Check Interval:</b> '+d.config.settings.check_interval+'秒</div>';
        }
    }catch(e){
        document.getElementById('output').innerHTML='<div class="result" style="color:red">❌ 错误：'+e.message+'</div>';
    }
}
async function testStatus(){
    try{
        const r=await fetch('/api/status');
        const d=await r.json();
        document.getElementById('output').innerHTML='<div class="result"><h3>服务状态</h3><pre>'+JSON.stringify(d,null,2)+'</pre></div>';
    }catch(e){
        document.getElementById('output').innerHTML='<div class="result" style="color:red">❌ 错误：'+e.message+'</div>';
    }
}
window.addEventListener('load',testConfig);
</script></body></html>'''
    return html

@app.route("/")
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/status')
def api_status():
    """获取服务状态"""
    status = get_service_status()
    return jsonify(status)

@app.route('/api/start', methods=['POST'])
def api_start():
    """启动服务 - 直接启动 Python 脚本"""
    status = get_service_status()
    if status['status'] == 'running':
        return jsonify({'success': False, 'message': '服务已在运行中'})
    
    # 直接启动 DDNS服务
    try:
        # 确保日志目录存在
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        
        # 后台启动
        with open(LOG_FILE, 'a') as log:
            process = subprocess.Popen(
                ['python3', '/tmp/ddns_dnshe_fixed.py'],
                stdout=log,
                stderr=log,
                start_new_session=True
            )
        
        time.sleep(2)
        new_status = get_service_status()
        if new_status['status'] == 'running':
            return jsonify({'success': True, 'message': '服务启动成功', 'new_status': new_status})
        else:
            return jsonify({'success': False, 'message': '服务启动失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"启动失败：{str(e)}"})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """停止服务 - 直接 kill 进程"""
    status = get_service_status()
    if status['status'] == 'stopped':
        return jsonify({'success': False, 'message': '服务已停止'})
    
    try:
        # 使用 pkill 停止进程
        # 精确停止 DDNS 进程（不影响 Web 后台）
        result = subprocess.run(
            ['bash', '-c', "ps aux | grep '[d]dns' | grep -v 'web' | awk '{print $2}' | xargs kill 2>/dev/null"],
            capture_output=True, text=True
        )
        time.sleep(1)
        new_status = get_service_status()
        if new_status['status'] == 'stopped':
            return jsonify({'success': True, 'message': '服务停止成功', 'new_status': {'status': 'stopped', 'pid': None}})
        else:
            return jsonify({'success': False, 'message': '停止失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"停止失败：{str(e)}"})

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """重启服务"""
    # 先停止
    stop_result = api_stop()
    time.sleep(1)
    
    # 再启动
    start_result = api_start()
    return start_result

@app.route('/api/config', methods=['GET'])
def api_get_config():
    """获取配置"""
    try:
        config = load_config()
        dnshe_config = dict(config['DNSHE']) if 'DNSHE' in config else {}
        settings_config = dict(config['DDNS']) if 'DDNS' in config else {}
        return jsonify({'success': True, 'config': {'dnshe': dnshe_config, 'settings': settings_config}})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/config', methods=['POST'])
def api_save_config():
    """保存配置"""
    try:
        data = request.get_json()
        config = load_config()
        if 'dnshe' in data:
            if 'DNSHE' not in config:
                config['DNSHE'] = {}
            for key, value in data['dnshe'].items():
                config['DNSHE'][key] = str(value)
        if 'settings' in data:
            if 'DDNS' not in config:
                config['DDNS'] = {}
            for key, value in data['settings'].items():
                config['DDNS'][key] = str(value)
        save_config(config)
        status = get_service_status()
        need_restart = status['status'] == 'running'
        return jsonify({'success': True, 'message': '配置保存成功' + ('（需重启服务才能生效）' if need_restart else ''), 'need_restart': need_restart})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/logs', methods=['GET'])
def api_get_logs():
    """获取日志"""
    try:
        lines = int(request.args.get('lines', 100))
        if not os.path.exists(LOG_FILE):
            return jsonify({'success': True, 'logs': [], 'message': '日志文件不存在'})
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            logs = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return jsonify({'success': True, 'logs': ''.join(logs)})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})



@app.route('/api/auto_fetch_subdomains', methods=['POST'])
def api_auto_fetch_subdomains():
    """自动获取子域名列表"""
    import requests
    
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        api_secret = data.get('api_secret', '').strip()
        
        if not api_key or not api_secret:
            return jsonify({
                'success': False,
                'message': 'API Key 和 API Secret 不能为空'
            })
        
        # 调用 DNSHE API 获取子域名列表
        url = "https://api005.dnshe.com/index.php"
        params = {
            'm': 'domain_hub',
            'endpoint': 'subdomains',
            'action': 'list'
        }
        headers = {
            'X-API-Key': api_key,
            'X-API-Secret': api_secret,
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('success'):
            subdomains = result.get('subdomains', [])
            
            # 格式化返回数据
            subdomain_list = []
            for sub in subdomains:
                subdomain_list.append({
                    'id': sub['id'],
                    'name': sub['subdomain'],
                    'rootdomain': sub['rootdomain'],
                    'full_domain': sub['full_domain'],
                    'status': sub['status']
                })
            
            return jsonify({
                'success': True,
                'message': f'成功获取 {len(subdomain_list)} 个子域名',
                'subdomains': subdomain_list
            })
        else:
            return jsonify({
                'success': False,
                'message': f'API 请求失败：{result}'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'请求异常：{str(e)}'
        })

@app.route('/api/test_api', methods=['POST'])
def test_api_connection():
    """测试 API 连接"""
    import requests
    
    try:
        config = load_config()
        api_key = config['DNSHE']['api_key']
        api_secret = config['DNSHE']['api_secret']
        
        headers = {
            'X-API-Key': api_key,
            'X-API-Secret': api_secret,
            'User-Agent': 'Mozilla/5.0'
        }
        
        # 测试列出子域名
        test_url = "https://api005.dnshe.com/index.php"
        params = {
            'm': 'domain_hub',
            'endpoint': 'subdomains',
            'action': 'list'
        }
        
        response = requests.get(test_url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('success'):
            subdomains = data.get('subdomains', [])
            return jsonify({
                'success': True,
                'message': 'API 连接正常',
                'data': {
                    'subdomains_count': len(subdomains),
                    'subdomains': subdomains
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'API 返回失败',
                'data': data
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'测试失败：{str(e)}'
        })

@app.route('/api/logs/clear', methods=['POST'])
def api_clear_logs():
    """清空日志"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write('')
            return jsonify({'success': True, 'message': '日志已清空'})
        else:
            return jsonify({'success': True, 'message': '日志文件不存在'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/static/script.js')
def serve_script():
    with open('/home/admin/static_script.js', 'r') as f:
        return f.read(), {'Content-Type': 'application/javascript'}

# 启动时修复配置
fix_config()


@app.route('/api-test.html')
def api_test_page():
    with open('/home/admin/api_test_page.html', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
