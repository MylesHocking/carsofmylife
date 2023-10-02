import React from 'react';

const CarCard = ({ car }) => {
  return (
    <div className="card" style={{ width: '18rem' }}>
    <div className="card-body">
      <h5 className="card-title">{car.make} {car.model}</h5>
      
      <p className="card-text">Rating: {car.rating}</p>
      <p className="card-text">Year: {car.year_purchased}</p>
    </div>
  </div>
  
  );
};

export default CarCard;
