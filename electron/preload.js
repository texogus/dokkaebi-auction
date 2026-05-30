const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('auctionApp', {
  loadSettings: () => ipcRenderer.invoke('load-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  chooseMemberFile: () => ipcRenderer.invoke('choose-member-file'),
  chooseBlockedFile: () => ipcRenderer.invoke('choose-blocked-file'),
  chooseOutputDir: () => ipcRenderer.invoke('choose-output-dir'),
  saveExtraMember: (payload) => ipcRenderer.invoke('save-extra-member', payload),
  startMonitor: (config) => ipcRenderer.invoke('start-monitor', config),
  stopMonitor: () => ipcRenderer.invoke('stop-monitor'),
  onLog: (callback) => ipcRenderer.on('monitor-log', (_event, message) => callback(message)),
  onStopped: (callback) => ipcRenderer.on('monitor-stopped', callback),
});
