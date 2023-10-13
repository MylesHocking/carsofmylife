import axios from 'axios';

export const fetchCars = async (userId) => {
  try {
    console.log('Making API call');
    const response = await axios.get('http://localhost:5000/api/user_cars/' + userId);
    console.log('API call successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('There was an error fetching car data:', error);
  }
};
