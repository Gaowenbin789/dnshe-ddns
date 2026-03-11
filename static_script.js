// DNSHE DDNS Web 后台 - JavaScript

function showMessage(message, type = 'info') {
    const existingMsg = document.querySelector('.message');
    if (existingMsg) {
        existingMsg.remove();
    }
    
    const messageEl = document.createElement('div');
    messageEl.className = 'message ' + type;
    messageEl.textContent = message;
    document.body.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        const statusEl = document.getElementById('service-status');
        const pidEl = document.getElementById('pid-info');
        
        if (data.status === 'running') {
            statusEl.textContent = '✅ 运行中';
            statusEl.className = 'status-indicator status-running';
            pidEl.textContent = '(PID: ' + data.pid + ')';
        } else {
            statusEl.textContent = '⏹️ 已停止';
            statusEl.className = 'status-indicator status-stopped';
            pidEl.textContent = '';
        }
    } catch (error) {
        showMessage('检查状态失败：' + error.message, 'error');
    }
}

async function startService() {
    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const data = await response.json();
        
        showMessage(data.message, data.success ? 'success' : 'error');
        if (data.success) {
            checkStatus();
        }
    } catch (error) {
        showMessage('启动失败：' + error.message, 'error');
    }
}

async function stopService() {
    if (!confirm('确定要停止 DDNS服务吗？')) return;
    
    try {
        const response = await fetch('/api/stop', { method: 'POST' });
        const data = await response.json();
        
        showMessage(data.message, data.success ? 'success' : 'error');
        if (data.success) {
            checkStatus();
        }
    } catch (error) {
        showMessage('停止失败：' + error.message, 'error');
    }
}

async function restartService() {
    if (!confirm('确定要重启 DDNS服务吗？')) return;
    
    try {
        const response = await fetch('/api/restart', { method: 'POST' });
        const data = await response.json();
        
        showMessage(data.message, data.success ? 'success' : 'error');
        if (data.success) {
            checkStatus();
        }
    } catch (error) {
        showMessage('重启失败：' + error.message, 'error');
    }
}

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.success) {
            const config = data.config;
            
            document.getElementById('api-key').value = config.dnshe.api_key || '';
            document.getElementById('api-secret').value = config.dnshe.api_secret || '';
            document.getElementById('subdomain-id').value = config.dnshe.subdomain_id || '0';

            document.getElementById('check-interval').value = config.settings.check_interval || '600';
            document.getElementById('dns-ttl').value = config.settings.dns_ttl || '600';

            
            showMessage('配置加载成功', 'success');
        } else {
            showMessage('加载配置失败：' + data.message, 'error');
        }
    } catch (error) {
        showMessage('加载配置失败：' + error.message, 'error');
    }
}

document.getElementById('config-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        dnshe: {
            api_key: document.getElementById('api-key').value,
            api_secret: document.getElementById('api-secret').value,
            subdomain_id: document.getElementById('subdomain-id').value,

        },
        settings: {
            check_interval: document.getElementById('check-interval').value,
            dns_ttl: document.getElementById('dns-ttl').value,

        }
    };
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const data = await response.json();
        
        showMessage(data.message, data.success ? 'success' : 'error');
    } catch (error) {
        showMessage('保存配置失败：' + error.message, 'error');
    }
});

async function loadLogs() {
    try {
        const response = await fetch('/api/logs?lines=100');
        const data = await response.json();
        
        const logContent = document.getElementById('log-content');
        const logLinesCount = document.getElementById('log-lines-count');
        
        if (data.success) {
            logContent.textContent = data.logs || '暂无日志';
            const lineCount = data.logs ? data.logs.split('\n').length : 0;
            logLinesCount.textContent = '(' + lineCount + '行)';
            
            const logContainer = document.getElementById('log-container');
            logContainer.scrollTop = logContainer.scrollHeight;
        } else {
            logContent.textContent = '加载失败：' + data.message;
        }
    } catch (error) {
        document.getElementById('log-content').textContent = '加载失败：' + error.message;
    }
}

async function clearLogs() {
    if (!confirm('确定要清空日志吗？')) return;
    
    try {
        const response = await fetch('/api/logs/clear', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showMessage(data.message, 'success');
            loadLogs();
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('清空日志失败：' + error.message, 'error');
    }
}

let autoRefreshInterval;
document.getElementById('auto-refresh').addEventListener('change', (e) => {
    if (e.target.checked) {
        autoRefreshInterval = setInterval(loadLogs, 5000);
    } else {
        clearInterval(autoRefreshInterval);
    }
});

window.addEventListener('load', () => {
    checkStatus();
    loadConfig();
    loadLogs();
    
    document.getElementById('auto-refresh').checked = true;
    autoRefreshInterval = setInterval(loadLogs, 5000);
});

// API 测试功能
async function testAPI() {
    const output = document.getElementById('api-test-output');
    if (output) {
        output.innerHTML = '<div class="result">正在测试 API 连接...</div>';
    }
    
    try {
        const response = await fetch('/api/test_api', { method: 'POST' });
        const data = await response.json();
        
        if (output) {
            if (data.success) {
                let html = '<div class="result" style="background:#d4edda;">';
                html += '<h3>✅ API 连接正常</h3>';
                html += '<p><strong>子域名数量:</strong> ' + data.data.subdomains_count + '</p>';
                
                if (data.data.subdomains && data.data.subdomains.length > 0) {
                    html += '<table style="width:100%;margin-top:10px;border-collapse:collapse;">';
                    html += '<tr style="background:#28a745;color:white;">';
                    html += '<th style="padding:8px;text-align:left;">ID</th>';
                    html += '<th style="padding:8px;">子域名</th>';
                    html += '<th style="padding:8px;">根域名</th>';
                    html += '<th style="padding:8px;">状态</th>';
                    html += '</tr>';
                    
                    for (let sub of data.data.subdomains) {
                        html += '<tr style="background:#f8f9fa;">';
                        html += '<td style="padding:8px;">' + sub.id + '</td>';
                        html += '<td style="padding:8px;">' + sub.subdomain + '</td>';
                        html += '<td style="padding:8px;">' + sub.rootdomain + '</td>';
                        html += '<td style="padding:8px;">' + sub.status + '</td>';
                        html += '</tr>';
                    }
                    html += '</table>';
                }
                html += '</div>';
                output.innerHTML = html;
            } else {
                output.innerHTML = '<div class="result" style="background:#f8d7da;"><h3>❌ API 测试失败</h3><p>' + data.message + '</p></div>';
            }
        }
    } catch (error) {
        if (output) {
            output.innerHTML = '<div class="result" style="background:#f8d7da;"><h3>❌ 错误</h3><p>' + error.message + '</p></div>';
        }
    }
}
