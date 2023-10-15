import React from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function App() {
  const navigate = useNavigate();
  const apiUrl = process.env.REACT_APP_FLASK_API_URL;
  const oauthRedirectUri = process.env.REACT_APP_OAUTH_REDIRECT_URI;
  
  return (
    <GoogleOAuthProvider
      clientId="1003699094925-sv0et1mp81ln28l24tccaosr60sbmuca.apps.googleusercontent.com"
      redirectUri={oauthRedirectUri}
    >
      <GoogleLogin
        onSuccess={credentialResponse => {
          console.log(credentialResponse);
          const { credential } = credentialResponse;
          // Save the Google ID token in the local state or local storage.
          localStorage.setItem("googleToken", credential);
          axios.post(`${apiUrl}/api/verify_google_token`, {
            token: credentialResponse.credential
          })
          .then(response => {
            //console.log("Server response:", response);
            const { user_info } = response.data;
            // Save user_info in the local state or local storage
            localStorage.setItem("user_id", user_info.id);  // <-- Store user ID here
            //console.log("User info:", user_info);
            localStorage.setItem("userInfo", JSON.stringify(user_info));
            
            //console.log("localstorage User info:", localStorage.getItem("userInfo"));
            // push to chart page
            navigate('/chart');
          })
          .catch(error => {
            console.log("Server error:", error);
            // Handle error
          });
        }}
        onError={() => {
          console.log('Google Login Failed');
        }}
      />
    </GoogleOAuthProvider>

  );
}

export default App;
