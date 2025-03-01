const fetch = require('node-fetch');
require('dotenv').config();

const OLLAMA_API_URL = process.env.OLLAMA_API_URL || 'http://localhost:11434';
const MODEL_NAME = process.env.OLLAMA_MODEL || 'poem-generator';
const CACHE_TTL = parseInt(process.env.CACHE_TTL || '3600000', 10); // Default: 1 hour

// Cache for location-based poems to reduce model calls
const poemCache = new Map();

/**
 * Check if Ollama is available and the model is loaded
 * @returns {Promise<boolean>} True if Ollama is available and the model is loaded
 */
async function isOllamaAvailable() {
  try {
    console.log('Checking Ollama availability...');
    
    // Simple test to see if we can generate a response
    const response = await fetch(`${OLLAMA_API_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL_NAME,
        prompt: 'Hello',
        stream: false,
      }),
    });
    
    if (!response.ok) {
      console.error(`Ollama API returned status: ${response.status}`);
      return false;
    }
    
    const data = await response.json();
    const isAvailable = Boolean(data && data.response);
    
    if (isAvailable) {
      console.log(`Model ${MODEL_NAME} is available in Ollama`);
    } else {
      console.error(`Model ${MODEL_NAME} is not available in Ollama`);
    }
    
    return isAvailable;
  } catch (error) {
    console.error('Error checking Ollama availability:', error);
    return false;
  }
}

/**
 * Generate a poem based on location, time, and date
 * @param {string} location - The user's location
 * @param {string} time - The current time (HH:MM)
 * @param {string} date - The current date (YYYY-MM-DD)
 * @returns {Promise<string>} The generated poem
 */
async function generatePoem(location, time, date) {
  // Check if Ollama is available
  const ollamaAvailable = await isOllamaAvailable();
  if (!ollamaAvailable) {
    console.error('Ollama is not available, cannot generate poem');
    return 'Sorry, the poem generation service is currently unavailable. Please try again later.';
  }
  
  // Create a cache key
  const cacheKey = `${location}-${time}-${date}`;
  
  // Check if we have a cached response
  if (poemCache.has(cacheKey)) {
    console.log('Returning cached poem for:', cacheKey);
    return poemCache.get(cacheKey);
  }
  
  try {
    console.log(`Generating poem for ${location} at ${time} on ${date}`);
    
    // Construct the prompt
    const prompt = `Write a poem about ${location} at ${time} on ${date}. The poem should be evocative and reflect the mood of the time and place.`;
    
    console.log('Sending request to Ollama API with prompt:', prompt);
    
    // Make the API request
    const response = await fetch(`${OLLAMA_API_URL}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: MODEL_NAME,
        prompt: prompt,
        stream: false,
      }),
    });
    
    if (!response.ok) {
      console.error(`Ollama API returned status: ${response.status}`);
      throw new Error(`Ollama API returned status: ${response.status}`);
    }
    
    // Get the response text first
    const text = await response.text();
    console.log('Raw Ollama API response:', text);
    
    // Try to parse as JSON
    let data;
    try {
      data = JSON.parse(text);
    } catch (error) {
      console.error('Failed to parse Ollama API response:', error);
      throw new Error('Failed to parse Ollama API response');
    }
    
    // Extract the poem from the response
    if (!data || !data.response) {
      console.error('Unexpected Ollama API response format:', data);
      throw new Error('Unexpected Ollama API response format');
    }
    
    const poem = data.response.trim();
    
    // Cache the response
    poemCache.set(cacheKey, poem);
    
    return poem;
  } catch (error) {
    console.error('Error generating poem:', error);
    throw error;
  }
}

/**
 * Generate a fallback poem when the model fails
 * @param {string} time - Time in HH:MM format
 * @param {string} date - Date in YYYY-MM-DD format
 * @param {string} location - Location name
 * @param {Object} contextInfo - Context information
 * @returns {string} - Fallback poem
 */
function generateFallbackPoem(time, date, location, contextInfo) {
  const timeOfDay = contextInfo?.timeOfDay || 'moment';
  const season = contextInfo?.season || 'season';
  
  return `"A ${timeOfDay} in ${location}"

In this ${timeOfDay} hour, at ${time},
The world unfolds in ${season}'s prime.
${location}'s beauty, a sight to behold,
As ${date}'s story begins to unfold.

The rhythm of time, a gentle beat,
In this moment, our hearts complete.
A poem awaits, in future's hand,
When systems align, as we planned.`;
}

/**
 * Get additional context information about the time and date
 * @param {string} timeStr - Time in HH:MM format
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @returns {Object} - Context information
 */
function getContextInfo(timeStr, dateStr) {
  try {
    // Parse time and date
    const [hour, minute] = timeStr.split(':').map(Number);
    const [year, month, day] = dateStr.split('-').map(Number);
    
    // Determine time of day
    let timeOfDay;
    if (hour >= 5 && hour < 12) {
      timeOfDay = 'morning';
    } else if (hour >= 12 && hour < 17) {
      timeOfDay = 'afternoon';
    } else if (hour >= 17 && hour < 21) {
      timeOfDay = 'evening';
    } else {
      timeOfDay = 'night';
    }
    
    // Determine season (Northern Hemisphere)
    let season;
    if (month >= 3 && month <= 5) {
      season = 'spring';
    } else if (month >= 6 && month <= 8) {
      season = 'summer';
    } else if (month >= 9 && month <= 11) {
      season = 'autumn';
    } else {
      season = 'winter';
    }
    
    return {
      timeOfDay,
      season,
      datetime: new Date(year, month - 1, day, hour, minute).toISOString(),
    };
  } catch (error) {
    console.warn('Could not get context information:', error);
    return null;
  }
}

/**
 * Simple cache for location names
 */
const locationNameCache = new Map();

/**
 * Get a human-readable location name from coordinates
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<string>} - Location name
 */
async function getLocationName(lat, lon) {
  const cacheKey = `${lat.toFixed(2)},${lon.toFixed(2)}`;
  
  // Check cache first
  if (locationNameCache.has(cacheKey)) {
    return locationNameCache.get(cacheKey);
  }
  
  try {
    // Use a free reverse geocoding API
    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10`);
    
    if (!response.ok) {
      throw new Error(`Geocoding API error: ${response.status}`);
    }
    
    const data = await response.json();
    let locationName = '';
    
    if (data.address) {
      // Try to get city or town name
      if (data.address.city) {
        locationName = data.address.city;
      } else if (data.address.town) {
        locationName = data.address.town;
      } else if (data.address.village) {
        locationName = data.address.village;
      } else if (data.address.county) {
        locationName = data.address.county;
      }
      
      // Add state/country for context
      if (data.address.state && locationName) {
        locationName += `, ${data.address.state}`;
      } else if (data.address.country && locationName) {
        locationName += `, ${data.address.country}`;
      }
    }
    
    // Cache the result
    if (locationName) {
      locationNameCache.set(cacheKey, locationName);
    }
    
    return locationName || null;
  } catch (error) {
    console.warn('Error getting location name:', error);
    return null;
  }
}

module.exports = {
  generatePoem,
  checkOllamaHealth: isOllamaAvailable
}; 