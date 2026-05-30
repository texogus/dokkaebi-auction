const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let monitorProcess = null;

const settingsPath = path.join(app.getPath('userData'), 'settings.json');

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 760,
    minWidth: 940,
    minHeight: 660,
    title: '도깨비 경매',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
}

function readSettings() {
  try {
    return JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
  } catch {
    return {};
  }
}

function writeSettings(settings) {
  fs.mkdirSync(path.dirname(settingsPath), { recursive: true });
  fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2), 'utf8');
}

function emitLog(message) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('monitor-log', message);
  }
}

function normalizeConfig(config) {
  const videoText = String(config.video_id || '').trim();
  let videoId = videoText;
  if (videoText.includes('watch?v=')) {
    videoId = videoText.split('watch?v=')[1].split('&')[0];
  } else if (videoText.includes('youtu.be/')) {
    videoId = videoText.split('youtu.be/')[1].split('?')[0];
  }

  return {
    api_key: String(config.api_key || '').trim(),
    video_id: videoId,
    member_file: String(config.member_file || '').trim(),
    blocked_file: String(config.blocked_file || '').trim(),
    output_dir: String(config.output_dir || '').trim() || path.join(os.homedir(), 'Documents'),
    host_keyword: String(config.host_keyword || '만물도깨비').trim(),
    poll_sec: Math.max(Number(config.poll_sec || 15), 15),
    sort_by_name: true,
    extra_members: Array.isArray(config.extra_members) ? config.extra_members : [],
  };
}

function bundledMonitorPath() {
  const executable = process.platform === 'win32' ? 'auction-monitor.exe' : 'auction-monitor';
  const candidates = [
    path.join(process.resourcesPath || '', 'auction-monitor', executable),
    path.join(__dirname, '..', 'dist-monitor', process.platform, executable),
  ];
  return candidates.find((candidate) => candidate && fs.existsSync(candidate));
}

function monitorCommand(configPath) {
  const bundled = bundledMonitorPath();
  if (bundled) {
    return {
      command: bundled,
      args: [configPath],
      cwd: path.dirname(bundled),
    };
  }

  const projectRoot = path.resolve(__dirname, '..');
  return {
    command: process.platform === 'win32' ? 'python' : 'python3',
    args: ['-m', 'auction.run_monitor', configPath],
    cwd: projectRoot,
  };
}

function memberWriterCommand(configPath) {
  const bundled = bundledMonitorPath();
  if (bundled) {
    return {
      command: bundled,
      args: ['append-member', configPath],
      cwd: path.dirname(bundled),
    };
  }

  const projectRoot = path.resolve(__dirname, '..');
  return {
    command: process.platform === 'win32' ? 'python' : 'python3',
    args: ['-m', 'auction.member_writer', configPath],
    cwd: projectRoot,
  };
}

function runHelper(commandSpec) {
  return new Promise((resolve, reject) => {
    const child = spawn(commandSpec.command, commandSpec.args, {
      cwd: commandSpec.cwd,
      env: { ...process.env, PYTHONUNBUFFERED: '1' },
    });
    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error((stderr || stdout || `helper exited with code=${code}`).trim()));
      }
    });
  });
}

async function saveExtraMemberToWorkbook(memberFile, member) {
  const payload = {
    member_file: String(memberFile || '').trim(),
    display_id: String(member.display_id || '').trim(),
    customer_name: String(member.customer_name || '').trim(),
    phone: String(member.phone || '').trim(),
    address: String(member.address || '').trim(),
    col_id: '아이디',
    col_name: '고객명',
    col_phone: '연락처',
    col_address: '주소',
  };

  if (!payload.member_file) {
    throw new Error('회원명단 엑셀 파일을 먼저 선택하세요.');
  }
  if (!payload.display_id) {
    throw new Error('추가 회원 아이디를 입력하세요.');
  }

  const suffix = Math.random().toString(16).slice(2);
  const configPath = path.join(app.getPath('temp'), `auction-member-${Date.now()}-${suffix}.json`);
  fs.writeFileSync(configPath, JSON.stringify(payload, null, 2), 'utf8');
  const result = await runHelper(memberWriterCommand(configPath));
  try {
    return JSON.parse(result.stdout.trim().split(/\r?\n/).pop() || '{}');
  } catch {
    return { action: 'saved' };
  }
}

async function syncExtraMembersToWorkbook(config) {
  const extraMembers = Array.isArray(config.extra_members) ? config.extra_members : [];
  if (!extraMembers.length) return;

  for (const member of extraMembers) {
    await saveExtraMemberToWorkbook(config.member_file, member);
  }
  emitLog(`추가 회원 ${extraMembers.length}명 회원명단 엑셀 동기화 완료`);
}

ipcMain.handle('load-settings', () => readSettings());
ipcMain.handle('save-settings', (_event, settings) => {
  writeSettings(settings);
  return true;
});

ipcMain.handle('choose-member-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'Excel', extensions: ['xlsx', 'xlsm'] }],
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('choose-blocked-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'Excel', extensions: ['xlsx', 'xlsm'] }],
  });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('choose-output-dir', async () => {
  const result = await dialog.showOpenDialog(mainWindow, { properties: ['openDirectory'] });
  return result.canceled ? null : result.filePaths[0];
});

ipcMain.handle('save-extra-member', async (_event, rawPayload) => {
  return saveExtraMemberToWorkbook(rawPayload.member_file, rawPayload);
});

ipcMain.handle('start-monitor', async (_event, rawConfig) => {
  if (monitorProcess) {
    throw new Error('이미 실행 중입니다.');
  }

  const config = normalizeConfig(rawConfig);
  if (!config.api_key) {
    throw new Error('YouTube API 키를 입력하세요.');
  }
  if (!config.video_id) {
    throw new Error('영상 ID 또는 URL을 입력하세요.');
  }

  writeSettings(rawConfig);
  await syncExtraMembersToWorkbook(config);
  const configPath = path.join(app.getPath('temp'), `auction-config-${Date.now()}.json`);
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');

  const runner = monitorCommand(configPath);
  monitorProcess = spawn(runner.command, runner.args, {
    cwd: runner.cwd,
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
  });

  emitLog('모니터링을 시작했습니다.');
  monitorProcess.stdout.on('data', (data) => emitLog(data.toString().trimEnd()));
  monitorProcess.stderr.on('data', (data) => emitLog(data.toString().trimEnd()));
  monitorProcess.on('close', (code) => {
    emitLog(`모니터링이 종료되었습니다. code=${code}`);
    monitorProcess = null;
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('monitor-stopped');
    }
  });

  return true;
});

ipcMain.handle('stop-monitor', () => {
  if (monitorProcess) {
    monitorProcess.kill('SIGINT');
  }
  return true;
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (monitorProcess) {
    monitorProcess.kill('SIGINT');
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
