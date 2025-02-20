import { app, BrowserWindow } from 'electron';

function createWindow() {
    const mainWindow: BrowserWindow = new BrowserWindow({
        width: 1600,
        height: 900,
    });
    mainWindow.loadFile('index.html');
}
app.whenReady().then(createWindow);
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
