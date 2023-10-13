import React, { useEffect, useState } from 'react';
import { fetchCars } from './utils/api.js';
import AddCar from './components/AddCar';
import CarChart from './components/CarChart'; 
import LoginPage from './components/LoginPage';  
import LandingPage from './components/LandingPage'; 
import { BrowserRouter as Router, Route, Routes,Link} from 'react-router-dom';
import PrivacyPolicy from './components/PrivacyPolicy';
import TermsOfService from './components/TermsOfService';
import logo from './assets/images/COMLlogosmol.png';

function App() {
  const [userInfo, setUserInfo] = useState(null);
  const [userId, setUserId] = useState(null);
  const [cars, setCars] = useState([]);

  // First useEffect to set userId
  useEffect(() => {
    const storedUserInfo = localStorage.getItem('userInfo');
    const storedUserId = localStorage.getItem('user_id');
    //const storedFirstName = localStorage.getItem('user_info.first_name');
    if (storedUserId) {
      setUserId(storedUserId);
    }
    if (storedUserInfo) {
      setUserInfo(storedUserInfo);
    }
  }, []); // This will run once when the component mounts

  // Second useEffect to get cars when userId changes
  useEffect(() => {
    const getCars = async () => {
      if (!userId) return;

      console.log('Fetching cars');
      const carData = await fetchCars(userId);
      console.log('Received carData:', carData);
      setCars(carData);
    };

    getCars();
  }, [userId]); // This will run whenever userId changes

  
  console.log("Current userInfo state:", userInfo);

  return (
    <Router>
      <div className="App">
        <header>
          <nav className="nav-container">
            <div>
              <Link to="/">HOME</Link> | <Link to="/add-car">ADD CAR</Link> | <Link to="/chart">CHART</Link>
            </div>
            <div>
              {userInfo ? (
                <span>
                  Cars of {JSON.parse(userInfo).firstname}'s Life <Link to="/logout">(logout)</Link>
                </span>
              ) : (
                <Link to="/login">Login</Link>
              )}
            </div>
          </nav>
          <img src={logo} alt="Cars of My Life Logo" className="logo" />
          <div className="chrome-pipe"></div>
          <div className="chrome-pipe2"></div>
        </header>
 
        <div className="chrome-bar"></div>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/chart" element={
              <>
                <CarChart cars={cars} userId={userId} />  {/* Include the CarChart here */}
              </>
            } />
            <Route path="/add-car" element={<AddCar />} />          
            <Route path="/login" element={<LoginPage />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/terms-of-service" element={<TermsOfService />} />
          </Routes>
          <footer className="footer">
            <Link to="/privacy-policy">Privacy Policy</Link> | <Link to="/terms-of-service">Terms of Service</Link>
          </footer>
      </div>
    </Router>
  );
}

export default App;