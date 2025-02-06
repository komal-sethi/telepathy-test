import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Grid, Paper, Typography, Box } from '@mui/material';
import { socket } from '../socket';

const shapes = [
  '◆', '★', '●', '▲', '■', '♥', '♠', '♣'
];

const Game = () => {
  const { gameId } = useParams();
  const [selectedCard, setSelectedCard] = useState(null);
  const [gameState, setGameState] = useState({
    currentRound: 0,
    score: 0,
    isFirstPlayer: false,
    waitingForSecondPlayer: false,
  });
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    socket.emit('join_game', { game_id: gameId, user_id: user.user_id });

    socket.on('game_joined', (data) => {
      setGameState(prev => ({
        ...prev,
        isFirstPlayer: data.first_player_id === user.user_id
      }));
    });

    socket.on('card_selected_update', (data) => {
      if (data.user_id !== user.user_id) {
        setGameState(prev => ({
          ...prev,
          waitingForSecondPlayer: false
        }));
      }
    });

    socket.on('card_check_result', (data) => {
      const isCorrect = data.is_correct;
      if (isCorrect) {
        setGameState(prev => ({
          ...prev,
          score: prev.score + 1
        }));
      }
      // Move to next round
      setTimeout(() => {
        setGameState(prev => ({
          ...prev,
          currentRound: prev.currentRound + 1,
          waitingForSecondPlayer: false
        }));
        setSelectedCard(null);
      }, 2000);
    });

    return () => {
      socket.off('game_joined');
      socket.off('card_selected_update');
      socket.off('card_check_result');
    };
  }, [gameId, user.user_id]);

  const handleCardSelect = (index) => {
    if (selectedCard !== null || 
        (gameState.waitingForSecondPlayer && gameState.isFirstPlayer)) {
      return;
    }

    setSelectedCard(index);
    socket.emit('card_selected', {
      game_id: gameId,
      card_index: index,
      user_id: user.user_id
    });

    if (gameState.isFirstPlayer) {
      setGameState(prev => ({
        ...prev,
        waitingForSecondPlayer: true
      }));
    } else {
      socket.emit('check_card', {
        game_id: gameId,
        card_index: index,
        is_correct: index === selectedCard
      });
    }
  };

  if (gameState.currentRound >= 10) {
    return (
      <Container>
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="h4">Game Over!</Typography>
          <Typography variant="h5">Final Score: {gameState.score}/10</Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Round {gameState.currentRound + 1}/10
        </Typography>
        <Typography variant="h6" gutterBottom>
          Score: {gameState.score}
        </Typography>
        {gameState.waitingForSecondPlayer && (
          <Typography variant="h6" color="primary">
            Waiting for other player...
          </Typography>
        )}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          {shapes.map((shape, index) => (
            <Grid item xs={3} key={index}>
              <Paper
                elevation={3}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  fontSize: '2rem',
                  backgroundColor: selectedCard === index ? '#e3f2fd' : 'white',
                  '&:hover': {
                    backgroundColor: '#f5f5f5'
                  }
                }}
                onClick={() => handleCardSelect(index)}
              >
                {shape}
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Container>
  );
};

export default Game;
