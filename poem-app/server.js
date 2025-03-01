const express = require('express');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const ollamaService = require('./services/ollama-service');
const fetch = require('node-fetch');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Configure rate limiting
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 60000, // 1 minute
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: 'Too many requests, please try again later.'
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Apply rate limiting to API endpoints
app.use('/api/', limiter);

// Middleware for validating poem request
function validatePoemRequest(req, res, next) {
  const { latitude, longitude, time, date } = req.body;
  
  // Validate coordinates
  if (!latitude || !longitude || !validateCoordinates(latitude, longitude)) {
    return res.status(400).json({ error: 'Valid latitude and longitude are required' });
  }
  
  // Use current time and date if not provided or invalid
  const now = new Date();
  
  if (!time || !validateTime(time)) {
    req.body.time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  }
  
  if (!date || !validateDate(date)) {
    req.body.date = now.toISOString().slice(0, 10);
  }
  
  next();
}

// Validate coordinates
function validateCoordinates(lat, lon) {
  const latitude = parseFloat(lat);
  const longitude = parseFloat(lon);
  
  return !isNaN(latitude) && 
         !isNaN(longitude) && 
         latitude >= -90 && 
         latitude <= 90 && 
         longitude >= -180 && 
         longitude <= 180;
}

// Validate time format (HH:MM)
function validateTime(time) {
  return /^([01]\d|2[0-3]):([0-5]\d)$/.test(time);
}

// Validate date format (YYYY-MM-DD)
function validateDate(date) {
  return /^\d{4}-\d{2}-\d{2}$/.test(date);
}

// API endpoint to generate a poem
app.post('/api/poem', validatePoemRequest, async (req, res) => {
  try {
    const { latitude, longitude, time, date } = req.body;
    
    // Get location information
    let locationInfo = 'unknown location';
    try {
      const locationData = await getLocationInfo(latitude, longitude);
      locationInfo = formatLocationInfo(locationData);
      console.log('Location info:', locationInfo);
    } catch (error) {
      console.error('Error getting location info:', error);
      // Continue with unknown location
    }
    
    // Generate the poem
    console.log(`Generating poem for ${locationInfo} at ${time} on ${date}`);
    const poem = await ollamaService.generatePoem(locationInfo, time, date);
    
    // Check if we have a valid poem
    if (!poem) {
      console.error('No poem generated from Ollama service');
      return res.status(500).json({ error: 'Failed to generate poem' });
    }
    
    console.log('Generated poem:', poem);
    res.json({ poem });
  } catch (error) {
    console.error('Error generating poem:', error);
    res.status(500).json({ error: 'Failed to generate poem', details: error.message });
  }
});

// API endpoint to check server health
app.get('/api/health', async (req, res) => {
  try {
    // Check Ollama availability directly
    let ollamaAvailable = false;
    
    try {
      const response = await fetch(`${process.env.OLLAMA_API_URL || 'http://localhost:11434'}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: process.env.OLLAMA_MODEL || 'poem-generator',
          prompt: 'Hello',
          stream: false,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        ollamaAvailable = Boolean(data && data.response);
      }
    } catch (error) {
      console.error('Direct Ollama check error:', error);
    }
    
    res.json({
      status: 'ok',
      ollama: ollamaAvailable ? 'available' : 'unavailable',
      model: process.env.OLLAMA_MODEL || 'poem-generator'
    });
  } catch (error) {
    console.error('Health check error:', error);
    res.status(500).json({ status: 'error', message: error.message });
  }
});

// API endpoint to get location name from coordinates
app.get('/api/location', async (req, res) => {
  try {
    const { latitude, longitude } = req.query;
    
    // Validate coordinates
    if (!latitude || !longitude || !validateCoordinates(latitude, longitude)) {
      return res.status(400).json({ error: 'Valid latitude and longitude are required' });
    }
    
    // Get location information
    const locationData = await getLocationInfo(latitude, longitude);
    const locationName = formatLocationInfo(locationData);
    
    res.json({ locationName });
  } catch (error) {
    console.error('Error getting location name:', error);
    res.status(500).json({ error: 'Failed to get location name', details: error.message });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  
  // Check Ollama availability on startup
  ollamaService.checkOllamaHealth().then(available => {
    if (available) {
      console.log(`Ollama is available with model: ${process.env.OLLAMA_MODEL || 'poem-generator'}`);
    } else {
      console.warn(`Warning: Ollama is not available or the model is not loaded. Make sure Ollama is running with the ${process.env.OLLAMA_MODEL || 'poem-generator'} model.`);
    }
  });
});

// Helper function to format location information
function formatLocationInfo(locationData) {
  try {
    if (!locationData || !locationData.address) {
      return 'unknown location';
    }
    
    const address = locationData.address;
    const parts = [];
    
    if (address.city || address.town || address.village) {
      parts.push(address.city || address.town || address.village);
    }
    
    if (address.state || address.county) {
      parts.push(address.state || address.county);
    }
    
    if (address.country) {
      parts.push(address.country);
    }
    
    return parts.length > 0 ? parts.join(', ') : 'unknown location';
  } catch (error) {
    console.error('Error formatting location info:', error);
    return 'unknown location';
  }
}

// Helper function to get location information from coordinates
async function getLocationInfo(latitude, longitude) {
  try {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10`;
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'PoemGeneratorApp/1.0'
      }
    });
    
    if (!response.ok) {
      throw new Error(`OpenStreetMap API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting location info:', error);
    return null;
  }
} 