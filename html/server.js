const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const port = 3000;
const server = http.createServer(app);
const io = socketIo(server);

let chatProcess = null;
let encryptionKey = '';
let targetIP = '';
let targetPort = '';

app.use(express.static(path.join(__dirname)));
app.use(bodyParser.json());

// Route to start the chat
app.post('/start-chat', (req, res) => {
    const { password, ip, port, useEncryptionKey } = req.body;

    // Verify the password
    if (password !== 'cookie10') {
        return res.json({ success: false, message: 'Incorrect password' });
    }

    targetIP = ip;
    targetPort = port;

    if (useEncryptionKey) {
        encryptionKey = generateRandomKey(16);
    } else {
        encryptionKey = '';  // No encryption
    }

    // Start the listener
    const listenerArgs = [
        ...(encryptionKey ? [`-k ${encryptionKey}`] : []),
        '-l',
        '-p', targetPort
    ];

    if (chatProcess) {
        chatProcess.kill();
    }

    chatProcess = spawn('cryptcat', listenerArgs, { shell: true });

    chatProcess.stdout.on('data', (data) => {
        console.log(`Received: ${data}`);
        io.emit('message', data.toString()); // Send data to WebSocket clients
    });

    chatProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });

    chatProcess.on('error', (err) => {
        console.error(`Failed to start chat process: ${err}`);
    });

    res.json({
        success: true,
        encryptionKey: useEncryptionKey ? encryptionKey : null
    });
});

// Route to send messages
app.post('/send-message', (req, res) => {
    const { message } = req.body;

    if (!chatProcess) {
        return res.status(400).json({ success: false, message: 'Chat not started' });
    }

    const sendArgs = [
        ...(encryptionKey ? [`-k ${encryptionKey}`] : []),
        targetIP,
        targetPort
    ];

    const sendProcess = spawn('cryptcat', sendArgs, {
        shell: true,
        stdio: ['pipe', 'inherit', 'inherit']
    });

    sendProcess.stdin.write(`${message}\n`);
    sendProcess.stdin.end();

    sendProcess.on('error', (error) => {
        console.error(`Error sending message: ${error.message}`);
        res.status(500).json({ success: false, message: 'Error sending message' });
    });

    sendProcess.on('close', () => {
        res.json({ success: true });
    });
});

// Function to generate a random key
function generateRandomKey(length) {
    const characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let key = '';
    for (let i = 0; i < length; i++) {
        key += characters[Math.floor(Math.random() * characters.length)];
    }
    return key;
}

server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
