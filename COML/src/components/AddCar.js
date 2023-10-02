import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AddCar = () => {
    const [makes, setMakes] = useState([]);
    const [models, setModels] = useState([]);
    const [modelVariants, setModelVariants] = useState([]);
    const [formData, setFormData] = useState({
      make: '',
      model: '',
      year: '',
      variant: '',
    });
    const { Storage } = require('@google-cloud/storage');
    const storage = new Storage();  // Add your GCP credentials here if needed
    const [imageURL, setImageURL] = useState(null);

    const fetchFirstImage = async (modelId) => {
        const bucketName = 'cars-of-my-life-images';
        const folderName = `photos/${modelId}/`;
      
        // Lists all the files in the folder
        const [files] = await storage.bucket(bucketName).getFiles({ prefix: folderName });
        
        if (files.length === 0) {
          console.log('No files found.');
          return;
        }
      
        // Get the first file name
        const firstFileName = files[0].name;
        
        // Fetch or download the file (this part depends on what you want to do with the image)
        // For now, let's just log the first file name
        console.log('First File:', firstFileName);
        const url = `https://storage.googleapis.com/${bucketName}/${firstFileName}`;
        setImageURL(url);
      };
      

    const years = Array.from({ length: new Date().getFullYear() - 1944 }, (_, i) => 1945 + i);

    // Load makes when the component mounts
    useEffect(() => {
      const fetchMakes = async () => {
        try {
          const response = await axios.get('http://localhost:5000/api/car_makes');     
          setMakes(response.data);
        } catch (error) {
          console.error('Error fetching makes:', error);
        }
      };
  
      fetchMakes();
    }, []);
  
    // Load models whenever a make is selected
    useEffect(() => {
    const fetchModels = async () => {
        if (formData.make) {
            try {
            // Use the correct API endpoint for fetching models
            const response = await axios.get(`http://localhost:5000/api/car_models/${formData.make}`);
            setModels(response.data);
            } catch (error) {
            console.error('Error fetching models:', error);
            }
        }
    };
    fetchModels();
  }, [formData.make]);
  
      // Load model variants whenever a model is selected
      useEffect(() => {
        if (formData.model) {
          const fetchModelVariants = async () => {
            try {
              const response = await axios.get(`http://localhost:5000/api/car_years_and_trims/${formData.model}`);
              console.log("URL:", `http://localhost:5000/api/car_years_and_trims/${formData.model}`);
              setModelVariants(response.data);
              console.log("Model Variants:", response.data);
            } catch (error) {
              console.error('Error fetching model variants:', error);
            }
          };
        
          fetchModelVariants();
        }
      }, [formData.model]);
      

  const handleInputChange = async (e) => {
    const { name, value } = e.target;
    console.log("Field Changed:", name, "Value:", value);  // Log the name and value of the changed field
    setFormData({
      ...formData,
      [name]: value,
    });
    // If the year & trim dropdown is selected, fetch the first image
    if (name === 'variant') {
        const variantData = JSON.parse(value);
        const { model_id } = variantData;
        if (model_id) {
            await fetchFirstImage(model_id);
        }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Make API call to add car
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
      <label>
        Make:
        <select
            name="make"
            value={formData.make}
            onChange={handleInputChange}
        >
            <option value="" disabled>Select make</option>
            {makes.map((make, index) => (
            <option key={index} value={make}>{make}</option>
            ))}
        </select>
        </label>
        <label>
            Model:
            <select
                name="model"
                value={formData.model}
                onChange={handleInputChange}
            >
                <option value="" disabled>Select model</option>
                {models.map((model, index) => (
                <option key={index} value={model.name}>{model.name}</option>
                ))}
            </select>
        </label>
        <label>
            Year and Trim:
            <select
                name="variant"
                value={formData.variant}
                onChange={handleInputChange}
            >
                <option value="" disabled>Select Year and Trim</option>
                {modelVariants.map((variant, index) => (
                <option key={index} value={variant.model_id}>
                    {variant.year} {variant.trim ? `- ${variant.trim}` : ''}
                </option>
                ))}
            </select>
        </label>
        <label>
            Year Purchased:
            <select
            name="year"
            value={formData.year}
            onChange={handleInputChange}
            >
            <option value="" disabled>Select Year</option>
            {years.map((year, index) => (
                <option key={index} value={year}>{year}</option>
            ))}
            </select>
        </label>

        <button type="submit">Add Car</button>
      </form>
      <div className="image-preview">        
            {imageURL && <img src={imageURL} alt="Car" />}
      </div>
      {/* Image upload section */}
      <div className="image-section">
        <h3>Add a Photo</h3>
        <label>
          Upload from Device:
          <input type="file" accept="image/*" />
        </label>
        <button onClick={() => {}}>Capture from Camera</button>
      </div>
    </div>
  );
};

export default AddCar;
