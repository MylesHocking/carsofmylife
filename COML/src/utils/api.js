import axios from 'axios';

export const fetchCars = async () => {
  try {
    console.log('Making API call');
    const response = await axios.get('http://localhost:5000/api/user_cars/1');
    console.log('API call successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('There was an error fetching car data:', error);
  }
};
