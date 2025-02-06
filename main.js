const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = require('electron-is-dev');
const http = require('http');

let mainWindow;
let flaskProcess;
let isQuitting = false;

function startFlaskServer() {
  // 在开发环境使用系统 Python，在生产环境使用打包的 Python
  const pythonPath = isDev 
    ? 'python/python.exe' 
    : path.join(process.resourcesPath, 'app/python/python.exe');
    
  // 在开发环境使用当前目录的 demo.py，在生产环境使用资源目录中的 demo.py
  const scriptPath = isDev 
    ? 'demo.py'
    : path.join(process.resourcesPath, 'app/demo.py');
  
  // 设置环境变量
  const env = {
    ...process.env,
    FLASK_ENV: isDev ? 'development' : 'production'
  };

  // 只在生产环境中配置 Python 环境
  if (!isDev) {
    env.PYTHONPATH = path.join(process.resourcesPath, 'app');
    env.PYTHONHOME = path.join(process.resourcesPath, 'app/python');
    env.PYTHONEXECUTABLE = path.join(process.resourcesPath, 'app/python/python.exe');
    const pythonDir = path.join(process.resourcesPath, 'app/python');
    const scriptsDir = path.join(process.resourcesPath, 'app/python/Scripts');
    env.PATH = `${pythonDir};${scriptsDir};${env.PATH || ''}`;
  }

  console.log('Starting Flask server with:');
  console.log('Python Path:', pythonPath);
  console.log('Script Path:', scriptPath);
  console.log('Environment:', env.FLASK_ENV);

  // 确保工作目录正确
  const cwd = isDev ? __dirname : path.join(process.resourcesPath, 'app');
  console.log('Working Directory:', cwd);

  flaskProcess = spawn(pythonPath, [scriptPath], {
    stdio: ['ignore', 'pipe', 'pipe'],
    env: env,
    cwd: cwd
  });

  let startupError = '';
  let isStarting = true;

  flaskProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`Flask: ${output}`);
    
    // 检查是否包含成功启动的标志
    if (output.includes('Running on http://')) {
      isStarting = false;
      console.log('Flask server started successfully');
    }
  });

  flaskProcess.stderr.on('data', (data) => {
    const error = data.toString();
    console.log(`Flask Error: ${error}`);
    
    if (isStarting) {
      startupError += error;
    }
  });

  flaskProcess.on('error', (error) => {
    console.error(`Flask Process Error: ${error.message}`);
    startupError += `\nProcess Error: ${error.message}`;
    // 只在生产环境显示错误
    if (!isDev) {
      dialog.showErrorBox('Python 环境错误', 
        `无法启动 Python 环境，请检查安装是否完整。\n\n` +
        `错误信息: ${error.message}`
      );
    }
  });

  flaskProcess.on('exit', (code, signal) => {
    if (code !== 0 && isStarting) {
      console.error(`Flask process exited with code ${code}`);
      console.error('Startup Error:', startupError);
      
      if (isDev) {
        // 开发环境保持原样
        dialog.showErrorBox('Flask 启动失败', 
          `启动错误 (退出码: ${code}):\n${startupError}\n\n` +
          `Python: ${pythonPath}\n` +
          `Script: ${scriptPath}\n` +
          `Working Dir: ${cwd}`
        );
      } else {
        // 生产环境显示友好的错误信息
        dialog.showErrorBox('服务启动失败', 
          `服务器启动失败，请检查:\n\n` +
          `1. 是否有其他程序占用了端口 5000\n` +
          `2. 是否有防火墙阻止\n` +
          `3. Python 环境是否完整\n\n` +
          `如果问题持续存在，请尝试重新安装程序。`
        );
      }
    }
  });

  // 等待服务器启动
  waitForServer();
}

function waitForServer() {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    const maxAttempts = 60;
    const interval = setInterval(() => {
      attempts++;
      const req = http.request({
        hostname: 'localhost',
        port: 5000,
        path: '/',
        method: 'GET'
      }, (res) => {
        clearInterval(interval);
        resolve();
      });

      req.on('error', (err) => {
        console.log(`Waiting for Flask server... (attempt ${attempts}/${maxAttempts})`);
        if (attempts >= maxAttempts) {
          clearInterval(interval);
          reject(new Error('Server did not start in time'));
        }
      });

      req.end();
    }, 1000);
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      webSecurity: false
    },
    show: false  // 初始不显示窗口
  });

  // 显示加载动画
  if (isDev) {
    // 开发环境
    await mainWindow.loadFile('./templates/loading.html');
  } else {
    // 生产环境 - 加载打包后 app/templates 目录下的文件
    await mainWindow.loadFile(path.join(process.resourcesPath, 'app/templates/loading.html'));
  }
  mainWindow.show();  // 显示窗口

  try {
    // 等待服务器启动
    await waitForServer();
    
    // 加载主页面
    await mainWindow.loadURL('http://localhost:5000');
    console.log('Page loaded successfully');
  } catch (error) {
    console.error('Error:', error);
    if (!isDev) {
      dialog.showErrorBox('连接错误',
        '无法连接到服务器，请检查:\n\n' +
        '1. 是否有其他程序占用了端口 5000\n' +
        '2. 是否有防火墙阻止\n' +
        '3. 程序是否完整安装\n\n' +
        '请尝试重启程序，如果问题持续存在，请重新安装。'
      );
    }
  }

  // 开发环境下打开开发者工具
  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', () => {
  startFlaskServer();
  createWindow();
});

app.on('window-all-closed', async () => {
  if (process.platform !== 'darwin') {
    isQuitting = true;
    await shutdownFlaskServer();
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

app.on('before-quit', async (e) => {
  if (!isQuitting) {
    e.preventDefault();
    isQuitting = true;
    await shutdownFlaskServer();
    app.quit();
  }
});

function shutdownFlaskServer() {
  return new Promise((resolve) => {
    if (flaskProcess && !flaskProcess.killed) {
      // 设置请求选项，包括必要的头部
      const options = {
        hostname: 'localhost',
        port: 5000,
        path: '/shutdown',
        method: 'GET',
        headers: {
          'Origin': 'http://localhost:5000',
          'Access-Control-Request-Method': 'GET',
          'Access-Control-Request-Headers': 'content-type'
        }
      };

      // 发送关闭请求到Flask服务器
      const req = http.request(options, (res) => {
        console.log('Shutdown request sent, status:', res.statusCode);
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          console.log('Response:', data);
          // 给服务器一些时间来完成清理和关闭
          setTimeout(() => {
            try {
              if (!flaskProcess.killed) {
                process.kill(flaskProcess.pid);
              }
            } catch (e) {
              console.log('Process already terminated');
            }
            resolve();
          }, 2000);
        });
      });

      req.on('error', (err) => {
        console.error('Error sending shutdown request:', err);
        try {
          process.kill(flaskProcess.pid);
        } catch (e) {
          console.log('Process already terminated');
        }
        resolve();
      });

      req.end();
    } else {
      resolve();
    }
  });
}
