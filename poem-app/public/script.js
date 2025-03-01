/**
 * Location-Based Poem Generator
 * 
 * This script handles:
 * 1. Getting the user's location
 * 2. Sending location and time data to the server
 * 3. Displaying the generated poem
 * 4. Refreshing the poem every minute
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM elements
  const locationDisplay = document.getElementById('location-display');
  const timeDisplay = document.getElementById('time-display');
  const dateDisplay = document.getElementById('date-display');
  const loadingElement = document.getElementById('loading');
  const poemContent = document.getElementById('poem-content');
  const poemTitle = document.getElementById('poem-title');
  const poemText = document.getElementById('poem-text');
  const errorMessage = document.getElementById('error-message');
  const countdownElement = document.getElementById('countdown');
  const refreshLocationButton = document.getElementById('refresh-location');
  const retryButton = document.getElementById('retry-button');
  const aboutButton = document.getElementById('about-button');
  const closeModalButton = document.getElementById('close-modal');
  const aboutModal = document.getElementById('about-modal');
  
  // State variables
  let userLocation = null;
  let refreshInterval = null;
  let countdownInterval = null;
  let countdown = 60;
  
  // Initialize the application
  init();
  
  /**
   * Initialize the application
   */
  function init() {
    // Check if the server is available
    checkServerHealth();
    
    // Update time and date immediately
    updateTimeAndDate();
    
    // Request user's location
    requestLocation();
    
    // Update time and date every second
    setInterval(updateTimeAndDate, 1000);
    
    // Set up event listeners
    setupEventListeners();
  }
  
  /**
   * Set up event listeners
   */
  function setupEventListeners() {
    // Refresh location button
    refreshLocationButton.addEventListener('click', () => {
      requestLocation();
    });
    
    // Retry button
    retryButton.addEventListener('click', () => {
      generatePoem();
    });
    
    // About button
    aboutButton.addEventListener('click', () => {
      aboutModal.classList.remove('hidden');
    });
    
    // Close modal button
    closeModalButton.addEventListener('click', () => {
      aboutModal.classList.add('hidden');
    });
    
    // Close modal when clicking outside
    aboutModal.addEventListener('click', (event) => {
      if (event.target === aboutModal) {
        aboutModal.classList.add('hidden');
      }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !aboutModal.classList.contains('hidden')) {
        aboutModal.classList.add('hidden');
      }
    });
  }
  
  /**
   * Check if the server is available
   */
  async function checkServerHealth() {
    try {
      const response = await fetch('/api/health');
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.ollama === 'unavailable') {
        console.warn('Ollama is not available. Poems may not generate correctly.');
      }
    } catch (error) {
      console.error('Health check error:', error);
    }
  }
  
  /**
   * Request the user's location
   */
  function requestLocation() {
    if (navigator.geolocation) {
      locationDisplay.textContent = 'Requesting location...';
      
      navigator.geolocation.getCurrentPosition(
        // Success callback
        (position) => {
          userLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          
          locationDisplay.textContent = `${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)}`;
          
          // Generate the first poem
          generatePoem();
          
          // Set up refresh interval (every minute)
          setupRefreshInterval();
        },
        // Error callback
        (error) => {
          console.error('Geolocation error:', error);
          let errorMsg = 'Location access denied';
          
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMsg = 'Location access denied. Please allow location access to generate poems based on your location.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMsg = 'Location information is unavailable.';
              break;
            case error.TIMEOUT:
              errorMsg = 'The request to get location timed out.';
              break;
            case error.UNKNOWN_ERROR:
              errorMsg = 'An unknown error occurred while getting location.';
              break;
          }
          
          locationDisplay.textContent = 'Location unavailable';
          showError(errorMsg);
        },
        // Options
        {
          enableHighAccuracy: false,
          timeout: 10000,
          maximumAge: 0
        }
      );
    } else {
      locationDisplay.textContent = 'Geolocation not supported';
      showError('Your browser does not support geolocation.');
    }
  }
  
  /**
   * Update the time and date displays
   */
  function updateTimeAndDate() {
    const now = new Date();
    
    // Format time (HH:MM)
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const timeString = `${hours}:${minutes}`;
    
    // Format date (YYYY-MM-DD)
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const dateString = `${year}-${month}-${day}`;
    
    // Update displays
    timeDisplay.textContent = timeString;
    dateDisplay.textContent = dateString;
  }
  
  /**
   * Generate a poem based on location and current time
   */
  async function generatePoem() {
    if (!userLocation) {
      showError('Location is required to generate a poem.');
      return;
    }
    
    // Show loading state
    showLoading();
    
    try {
      const now = new Date();
      const timeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
      const dateString = now.toISOString().slice(0, 10);
      
      console.log('Sending request to server with location:', userLocation);
      
      const response = await fetch('/api/poem', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: userLocation.latitude,
          longitude: userLocation.longitude,
          time: timeString,
          date: dateString,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Server response:', data);
      
      // Check if we have a poem in the response
      if (data && typeof data === 'object') {
        if (data.poem) {
          displayPoem(data.poem);
        } else if (data.error) {
          showError(data.error);
        } else {
          throw new Error('Unexpected response format');
        }
      } else if (typeof data === 'string') {
        displayPoem(data);
      } else {
        throw new Error('No poem received from server');
      }
    } catch (error) {
      console.error('Error generating poem:', error);
      showError('Failed to generate poem. Please try again later.');
    }
  }
  
  /**
   * Display the generated poem
   * @param {string|object} poemContentData - The generated poem
   */
  function displayPoem(poemContentData) {
    try {
      if (!poemContentData) {
        showError('No poem content received.');
        return;
      }
      
      // Make sure poemContentData is a string
      let poemTextContent = '';
      if (typeof poemContentData === 'string') {
        poemTextContent = poemContentData;
      } else if (typeof poemContentData === 'object') {
        poemTextContent = poemContentData.poem || JSON.stringify(poemContentData);
      } else {
        poemTextContent = String(poemContentData);
      }
      
      // Check if the poem is an error message
      if (poemTextContent.includes('Sorry, the poem generation service is currently unavailable')) {
        showError('The poem generation service is currently unavailable. Please try again later.');
        return;
      }
      
      // Extract title if present (assuming title is in quotes on the first line)
      const lines = poemTextContent.trim().split('\n');
      let title = 'Poem of the Moment';
      let poemBody = poemTextContent;
      
      const titleMatch = lines[0].match(/"([^"]+)"/);
      if (titleMatch) {
        title = titleMatch[1];
        poemBody = lines.slice(1).join('\n').trim();
      }
      
      // Update the DOM
      poemTitle.textContent = title;
      poemText.textContent = poemBody;
      
      // Hide loading, show poem
      hideLoading();
      poemContent.classList.remove('hidden');
      errorMessage.classList.add('hidden');
    } catch (error) {
      console.error('Error displaying poem:', error);
      showError('Error displaying poem. Please try again.');
    }
  }
  
  /**
   * Set up the refresh interval for generating new poems
   */
  function setupRefreshInterval() {
    // Clear any existing intervals
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    if (countdownInterval) {
      clearInterval(countdownInterval);
    }
    
    // Reset countdown
    countdown = 60;
    countdownElement.textContent = countdown;
    
    // Set up new intervals
    refreshInterval = setInterval(generatePoem, 60000); // Generate new poem every minute
    
    countdownInterval = setInterval(() => {
      countdown -= 1;
      countdownElement.textContent = countdown;
      
      if (countdown <= 0) {
        countdown = 60;
      }
    }, 1000);
  }
  
  /**
   * Show loading state
   */
  function showLoading() {
    loadingElement.classList.remove('hidden');
    poemContent.classList.add('hidden');
    errorMessage.classList.add('hidden');
  }
  
  /**
   * Hide loading state
   */
  function hideLoading() {
    loadingElement.classList.add('hidden');
  }
  
  /**
   * Show error message
   * @param {string} message - Error message to display
   */
  function showError(message) {
    errorMessage.querySelector('p').textContent = message;
    errorMessage.classList.remove('hidden');
    loadingElement.classList.add('hidden');
    poemContent.classList.add('hidden');
  }
}); 