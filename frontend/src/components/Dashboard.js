import React, { useState } from 'react';
import { Container, Button, TextField, Typography, Box, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { socket } from '../socket';

const Dashboard = () => {
  const [inviteEmail, setInviteEmail] = useState('');
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));

  const handleCreateGame = () => {
    socket.emit('create_game', { sender_id: user.user_id });
    socket.on('game_created', (data) => {
      handleInvitePlayer(data.game_id);
    });
  };

  const handleInvitePlayer = (gameId) => {
    socket.emit('invite_player', {
      email: inviteEmail,
      game_id: gameId,
      sender_email: user.email
    });
    navigate(`/game/${gameId}`);
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome, {user.name}!
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Start a New Telepathy Test
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <TextField
              fullWidth
              label="Invite Player (Email)"
              variant="outlined"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreateGame}
              disabled={!inviteEmail}
            >
              Start Game
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Dashboard;
