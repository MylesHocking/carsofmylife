import React, { useEffect, useState } from 'react';
import '../index.css';
import axios from 'axios';
import html2canvas from 'html2canvas';

const CarChart = ({ cars }) => {  
  const apiUrl = process.env.REACT_APP_FLASK_API_URL;
  console.log("Cars in CarChart:", cars);
  const [points, setPoints] = useState([]);
  const [xLabels, setXLabels] = useState([]);
  const [yLabels, setYLabels] = useState([]);

  const chartWidth = 750;
  const chartHeight = 400;

  const [selectedCar, setSelectedCar] = useState(null);

  const handlePointClick = (car, imageUrl) => {
    console.log("Clicked on:", car, imageUrl);
    setSelectedCar({...car, imageUrl});
  };

  useEffect(() => {
    const yAxisLabels = [0, 2, 4, 6, 8, 10];
    if (cars && cars.length > 0) {
      const earliestYear = cars.length ? Math.min(...cars.map(car => car.year_purchased || 0)) : 0;
      const latestYear = cars.length ? Math.max(...cars.map(car => car.year_purchased || 0)) : 0;
      const rangeOfYears = latestYear - earliestYear;

      const newPoints = cars.map(car => ({
        left: ((car.year_purchased - earliestYear) / rangeOfYears) * chartWidth,
        bottom: (car.rating / 10) * chartHeight,
      }));

      setPoints(newPoints);
      const uniqueYears = Array.from(new Set(cars.map(car => car.year_purchased))).sort((a, b) => a - b);
      const newLabels = uniqueYears.map(year => ({
        year,
        left: ((year - earliestYear) / rangeOfYears) * chartWidth,
      }));

      setXLabels(newLabels);

      setYLabels(yAxisLabels.map(label => ({
        label,
        bottom: (label / 10) * chartHeight,
      })));  

      const fetchImages = async () => {
        const newPointsWithImages = [];
    
        for (const car of cars) {
          const left = ((car.year_purchased - earliestYear) / rangeOfYears) * chartWidth;
          const bottom = (car.rating / 10) * chartHeight;
          let imageUrl = null;
    
          try {
            const response = await axios.get(`${apiUrl}/api/get_first_image/${car.model_id}`);
            imageUrl = response.data.image_url; // assuming the URL comes in response.data
          } catch (error) {
            if (error.response && error.response.status === 404) {
              // Handle 'No images found' scenario. We'll leave imageUrl as null.
            }
          }
          
          newPointsWithImages.push({
            left,
            bottom,
            imageUrl,
          });
        }
    
        setPoints(newPointsWithImages);
      };
    
      fetchImages();
    }
  }, [cars, apiUrl]);

  const downloadChart = () => {
    const chartElement = document.getElementsByClassName('chart-container')[0];

    html2canvas(chartElement).then((canvas) => {
      const pngUrl = canvas.toDataURL("image/png");
      let downloadLink = document.createElement('a');
      downloadLink.href = pngUrl;
      downloadLink.download = 'chart.png';
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    });
  }

  return (
    <>
    
  
    <div className="chart-container">
      <button className="download-button" onClick={downloadChart}>Download Chart</button>
      {(!cars || cars.length === 0) ? (
          <div className="no-cars-message">
            <a href="/add-car">Please Add Your First Car!</a>
          </div>
        ) : (
      <div id="chart" className="chart">
        <div className="axis" id="x-axis"></div>
        <div className="axis" id="y-axis"></div>
        <svg className="line-container" width={chartWidth} height={chartHeight}>
          {points.map((point, index, arr) => {
            if (index === 0) return null;  // Skip the first point
            return (
              <line 
                key={index} 
                x1={arr[index - 1].left+25} y1={chartHeight - arr[index - 1].bottom} 
                x2={point.left+25} y2={chartHeight - point.bottom} 
                stroke="black"
              />
            );
          })}
        </svg>

        {xLabels.map((xLabel, index) => (
          <div key={index} className="x-label" style={{ left: `${xLabel.left}px` }}>
            {xLabel.year}
          </div>
        ))}
        {yLabels.map((yLabel, index) => (
          <div key={index} className="y-label" style={{ bottom: `${yLabel.bottom}px` }}>
            {yLabel.label}
          </div>
        ))}
        {points.map((point, index) => {
          const car = cars[index];
          return (
            <React.Fragment key={index}>
              <div 
                key={`${index}-point`} 
                onClick={() => handlePointClick(car, point.imageUrl)}
                className={`point ${!point.imageUrl ? 'grey-placeholder' : ''}`}
                style={{ 
                  left: `${point.left}px`, 
                  bottom: `${point.bottom - (point.imageUrl ? -25 : 25)}px` // Conditional bottom positioning
                }}
              >
                {point.imageUrl ? <img src={point.imageUrl} alt="car" /> : null}
              </div>
              <div 
                key={`${index}-label`} 
                className="car-label"
                style={{ 
                  left: `${point.left -5}px`, 
                  bottom: `${car.rating < 2 ? point.bottom + 30 : point.bottom - 50}px`
                }}
              >
                <span className="make">{car.make}</span><br />
                <span className="model">{car.model}</span>
              </div>
            </React.Fragment>
          );
        })}
        {selectedCar && (
          <div className="modal">
            <div className="modal-content">          
              <span className="close" onClick={() => setSelectedCar(null)}>&times;</span>
              <h1>{selectedCar.make} {selectedCar.model}</h1>
              {selectedCar.imageUrl ? <img src={selectedCar.imageUrl} alt={`${selectedCar.make} ${selectedCar.model}`} /> : <p>No image available</p>}
              <p>Memories: {selectedCar.memories}</p>
              <p>Trim: {selectedCar.model_trim || 'n/a'}</p>
              <p>Made: {selectedCar.model_year || 'n/a'}</p>
              <div class="smaller-font">
                <p>Made: {selectedCar.model_year || 'n/a'}</p>
                <p>Engine CC: {selectedCar.model_engine_cc || 'n/a'}</p>
                <p>Sold in US: {selectedCar.model_sold_in_us ? 'Yes' : 'No' || 'n/a'}</p>
                <p>Engine Type: {selectedCar.model_engine_type || 'n/a'}</p>
                <p>Engine Position: {selectedCar.model_engine_position || 'n/a'}</p>
                <p>Engine Cylinders: {selectedCar.model_engine_cyl || 'n/a'}</p>
                <p>Drive: {selectedCar.model_drive || 'n/a'}</p>
                <p>Engine Power (PS): {selectedCar.model_engine_power_ps || 'n/a'}</p>
                <p>Engine Torque (Nm): {selectedCar.model_engine_torque_nm || 'n/a'}</p>
                <p>Engine Fuel: {selectedCar.model_engine_fuel || 'n/a'}</p>
                <p>Weight (kg): {selectedCar.model_weight_kg || 'n/a'}</p>
                <p>Transmission Type: {selectedCar.model_transmission_type || 'n/a'}</p>
                <p>Doors: {selectedCar.model_doors || 'n/a'}</p>
                <p>Trim: {selectedCar.model_trim || 'n/a'}</p>
                <p>Body: {selectedCar.model_body || 'n/a'}</p>
                <p>Engine Valves Per Cylinder: {selectedCar.model_engine_valves_per_cyl || 'n/a'}</p>
                <p>Engine Power RPM: {selectedCar.model_engine_power_rpm || 'n/a'}</p>
                <p>Engine Torque RPM: {selectedCar.model_engine_torque_rpm || 'n/a'}</p>
                <p>Engine Bore (mm): {selectedCar.model_engine_bore_mm || 'n/a'}</p>
                <p>Engine Stroke (mm): {selectedCar.model_engine_stroke_mm || 'n/a'}</p>
                <p>Engine Compression: {selectedCar.model_engine_compression || 'n/a'}</p>
                <p>Seats: {selectedCar.model_seats || 'n/a'}</p>
                <p>Engine Torque RPM: {selectedCar.model_engine_torque_rpm || 'n/a'}</p>
                <p>Mixed L/KM: {selectedCar.model_lkm_mixed || 'n/a'}</p>
                <p>Engine Bore (mm): {selectedCar.model_engine_bore_mm || 'n/a'}</p>
                <p>Engine Stroke (mm): {selectedCar.model_engine_stroke_mm || 'n/a'}</p>
                <p>Highway L/KM: {selectedCar.model_lkm_hwy || 'n/a'}</p>
                <p>City L/KM: {selectedCar.model_lkm_city || 'n/a'}</p>
                <p>Top Speed (KPH): {selectedCar.model_top_speed_kph || 'n/a'}</p>
                <p>0 to 100 KPH: {selectedCar.model_0_to_100_kph || 'n/a'}</p>
                <p>CO2: {selectedCar.model_co2 || 'n/a'}</p>
              </div>

            </div>
          </div>
        )}
      </div>      
      )}
    </div>   

    </>
  );
};

export default CarChart;
