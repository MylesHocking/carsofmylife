import axios from 'axios';

export const fetchCars = async (userId) => {
  try {
    const apiUrl = process.env.REACT_APP_FLASK_API_URL;
    console.log('Making API call');
    const response = await axios.get(`${apiUrl}/api/user_cars/` + userId);
    console.log('API call successful:', response.data);
    return response.data;
  } catch (error) {
    console.error('There was an error fetching car data:', error);
  }
};
