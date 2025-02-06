import { io } from 'socket.io-client';

const BACKEND_URL = process.env.REACT_APP_API_URL || 'https://telepathy-test.onrender.com';

console.log('Connecting to backend at:', BACKEND_URL);

export const socket = io(BACKEND_URL, {
  autoConnect: true,
  transports: ['polling'],
  upgrade: false,
  path: '/socket.io',
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  withCredentials: false,
  forceNew: true,
  timeout: 20000
});

socket.on('connect', () => {
  console.log('Connected to Socket.IO server');
});

socket.on('connect_error', (error) => {
  console.error('Socket.IO connection error:', error);
});

socket.on('error', (error) => {
  console.error('Socket.IO error:', error);
});

socket.on('disconnect', (reason) => {
  console.log('Disconnected from Socket.IO server:', reason);
});
