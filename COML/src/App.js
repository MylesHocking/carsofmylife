import React, { useEffect, useState } from 'react';
import { fetchCars } from './utils/api.js';
import CarCard from './components/CarCard';
import AddCar from './components/AddCar';
import { BrowserRouter as Router, Route, Routes,Link} from 'react-router-dom';


function App() {
  const [cars, setCars] = useState([]);

  useEffect(() => {
    const getCars = async () => {
      console.log('Fetching cars');
      const carData = await fetchCars();
      console.log('Received carData:', carData);
      setCars(carData);
    };

    getCars();

  }, []);

  return (
    <Router>
      <div className="App">
        <header>
          <h1>Cars of My Life</h1>
          <nav>
            <Link to="/">Home</Link> | <Link to="/add-car">Add Car</Link>
          </nav>
        </header>
        <Routes>
          <Route path="/" element={<>{cars.map((car, index) => <CarCard key={index} car={car} />)}</>} />
          <Route path="/add-car" element={<AddCar />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;