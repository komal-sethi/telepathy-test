import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Container, Typography, Box } from '@mui/material';

const Login = () => {
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      // Initialize Google Sign-In
      window.google.accounts.id.initialize({
        client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
      });

      window.google.accounts.id.prompt((notification) => {
        if (notification.isNotDisplayed()) {
          console.error('Google Sign-In failed to display');
        }
      });
    } catch (error) {
      console.error('Google Sign-In error:', error);
    }
  };

  const handleCredentialResponse = async (response) => {
    try {
      // Send token to backend
      const res = await fetch('http://localhost:5000/auth/google', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: response.credential }),
      });

      const data = await res.json();
      if (data.user_id) {
        localStorage.setItem('user', JSON.stringify(data));
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Authentication error:', error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom>
          Telepathy Test
        </Typography>
        <Typography variant="h6" component="h2" gutterBottom>
          Test your telepathic connection with friends!
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleGoogleLogin}
          sx={{ mt: 3 }}
        >
          Sign in with Google
        </Button>
      </Box>
    </Container>
  );
};

export default Login;
