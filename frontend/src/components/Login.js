import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Container, Typography, Box } from '@mui/material';

const Login = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const handleGoogleLogin = () => {
    console.log('Initializing Google Sign-In...');
    try {
      const client_id = process.env.REACT_APP_GOOGLE_CLIENT_ID;
      console.log('Using client ID:', client_id);

      if (!client_id) {
        console.error('Google Client ID not found in environment variables');
        return;
      }

      window.google.accounts.id.initialize({
        client_id: client_id,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true,
        prompt_parent_id: 'google-signin-button',
      });

      window.google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        { 
          type: 'standard',
          theme: 'outline', 
          size: 'large',
          text: 'continue_with',
          shape: 'rectangular',
          logo_alignment: 'left'
        }
      );

      console.log('Google Sign-In initialized successfully');
    } catch (error) {
      console.error('Error initializing Google Sign-In:', error);
    }
  };

  const handleCredentialResponse = async (response) => {
    console.log('Received Google credential response');
    try {
      const backendUrl = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      console.log('Sending token to backend:', backendUrl);

      const res = await fetch(`${backendUrl}/auth/google`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: response.credential }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Backend authentication successful:', data);

      if (data.user_id) {
        localStorage.setItem('user', JSON.stringify(data));
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Authentication error:', error);
    }
  };

  useEffect(() => {
    handleGoogleLogin();
  }, []);

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 3,
        }}
      >
        <Typography variant="h3" component="h1" gutterBottom>
          Telepathy Test
        </Typography>
        
        <Typography variant="h6" component="h2" gutterBottom>
          Test your telepathic connection with friends!
        </Typography>

        <Box id="google-signin-button" sx={{ mt: 3 }} />

        {process.env.NODE_ENV === 'development' && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            API URL: {process.env.REACT_APP_API_URL || 'http://localhost:5000'}
          </Typography>
        )}
      </Box>
    </Container>
  );
};

export default Login;
