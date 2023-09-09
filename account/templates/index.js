import React, { useState } from 'react';
import axios from 'axios';

const OnboardingPage = () => {
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [message, setMessage] = useState('');

  const handleCategoryClick = (category) => {
    if (selectedCategories.length < 3) {
      setSelectedCategories(prevSelected => [...prevSelected, category]);
    } else {
      setMessage('You can only select up to 3 categories.');
    }
  };

  const handleFinishClick = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/onboarding/',
        { selected_categories: selectedCategories }
      );
      setMessage(response.data.message); // Display success message from backend
    } catch (error) {
      setMessage('An error occurred while processing your request.');
      console.error(error);
    }
  };

  return (
    <div>
      <h2>Category Selection</h2>
      <div>
        {/* Replace with your actual category buttons */}
        <button onClick={() => handleCategoryClick('Category 1')}>Category 1</button>
        <button onClick={() => handleCategoryClick('Category 2')}>Category 2</button>
        <button onClick={() => handleCategoryClick('Category 3')}>Category 3</button>
        {/* Add more buttons for other categories */}
      </div>
      <button onClick={handleFinishClick}>Finish</button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default OnboardingPage;
