import { app, BrowserWindow } from 'electron';
import path from 'path';

// Fix for windows installer behavior
if (require('electron-squirrel-startup')) {
    app.quit();
}

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true, // Recommended for security
            preload: path.join(__dirname, 'preload.js'),
        },
    });

    // Check if we are in dev mode
    const isDev = process.env.NODE_ENV === 'development' || process.env.DEBUG_PROD === 'true';

    if (isDev || process.argv.includes('--dev')) {
        win.loadURL('http://localhost:5173');
        win.webContents.openDevTools();
    } else {
        win.loadFile(path.join(__dirname, '../dist/index.html'));
    }
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
