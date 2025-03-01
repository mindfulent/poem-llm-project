# Location-Based Poem Generator

A web application that generates poems based on the user's location and the current time. The poems are generated using a fine-tuned language model that has been trained to create contextually relevant poetry.

## Features

- Automatically detects the user's location (with permission)
- Generates poems based on location, time of day, and date
- Refreshes the poem every minute
- Responsive design for mobile and desktop
- Accessibility features for screen readers and keyboard navigation
- Fallback mechanisms when model generation fails

## Prerequisites

- Node.js (v14 or higher)
- Ollama installed and running with the `poem-generator` model

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd poem-app
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Make sure Ollama is running with the poem-generator model:
   ```
   ollama run poem-generator
   ```

   If you need to create the model first:
   ```
   cd ../lora_model
   ollama create poem-generator -f Modelfile
   ```

4. Start the server:
   ```
   npm start
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

## Configuration

You can modify the following settings in the `.env` file:

```
# Server configuration
PORT=3000

# Ollama configuration
OLLAMA_API_URL=http://localhost:11434
MODEL_NAME=poem-generator

# Rate limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=60
```

## Development

For development with auto-restart on file changes:

```
npm run dev
```

## Project Structure

```
poem-app/
├── package.json        # Project dependencies and scripts
├── server.js           # Main Express server
├── .env                # Environment variables
├── services/
│   └── ollama-service.js  # Service for interacting with Ollama
└── public/             # Static files served to the client
    ├── index.html      # Main HTML file
    ├── styles.css      # CSS styles
    └── script.js       # Client-side JavaScript
```

## API Endpoints

- `POST /api/poem`: Generate a poem based on location and time
  - Request body: `{ latitude, longitude, time, date }`
  - Response: `{ poem, metadata }`

- `GET /api/health`: Check server and Ollama health
  - Response: `{ status, ollama, model }`

## Troubleshooting

### Common Issues and Solutions

1. **429 Too Many Requests Error**
   - This can occur if the rate limit is too restrictive
   - Increase the `RATE_LIMIT_MAX_REQUESTS` value in the `.env` file
   - Default is now set to 60 requests per minute (previously 10)

2. **Ollama Connection Issues**
   - Ensure Ollama is running: `ollama list`
   - Verify the correct API URL in `.env`: `OLLAMA_API_URL=http://localhost:11434`
   - Make sure the poem-generator model is available: `ollama run poem-generator`

3. **JavaScript Errors**
   - If you see "Cannot read properties of undefined (reading 'remove')" error, ensure you're using the latest version of script.js
   - This error was fixed by resolving a variable name conflict in the displayPoem function

### Recent Fixes

1. **API URL Configuration**
   - Fixed incorrect Ollama API URL in `.env` file
   - Changed from `http://localhost:11434/api/generate` to `http://localhost:11434`
   - This prevents malformed URL requests to Ollama

2. **Rate Limiting Adjustment**
   - Increased rate limit from 10 to 60 requests per minute
   - This accommodates multiple API calls made during each user request

3. **JavaScript Variable Name Conflict**
   - Fixed a variable name conflict in the `displayPoem` function
   - Renamed parameter from `poemContent` to `poemContentData` to avoid conflict with DOM element
   - This resolves the TypeError: "Cannot read properties of undefined (reading 'remove')"

## Accessibility Features

This application includes the following accessibility features:

- Proper ARIA attributes for screen readers
- Keyboard navigation support
- Focus management
- High contrast mode support
- Semantic HTML structure
- Screen reader announcements for dynamic content

## License

MIT 