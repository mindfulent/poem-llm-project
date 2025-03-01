const fetch = require('node-fetch');

const OLLAMA_API_URL = 'http://localhost:11434';
const MODEL_NAME = 'poem-generator';

async function testOllama() {
  try {
    console.log('Testing Ollama API...');
    
    // Test the /api/tags endpoint
    console.log('\nTesting /api/tags endpoint:');
    try {
      const tagsResponse = await fetch(`${OLLAMA_API_URL}/api/tags`);
      console.log('Status:', tagsResponse.status);
      
      if (tagsResponse.ok) {
        const tagsData = await tagsResponse.json();
        console.log('Response:', JSON.stringify(tagsData, null, 2).substring(0, 500) + '...');
        
        if (tagsData && tagsData.models) {
          const modelAvailable = tagsData.models.some(model => 
            model.name.includes(MODEL_NAME) || model.model.includes(MODEL_NAME)
          );
          
          console.log(`Model ${MODEL_NAME} available:`, modelAvailable);
          if (modelAvailable) {
            const model = tagsData.models.find(m => 
              m.name.includes(MODEL_NAME) || m.model.includes(MODEL_NAME)
            );
            console.log('Model details:', model);
          } else {
            console.log('Available models:', tagsData.models.map(m => m.name).join(', '));
          }
        }
      }
    } catch (error) {
      console.error('Error testing /api/tags:', error);
    }
    
    // Test the /api/generate endpoint
    console.log('\nTesting /api/generate endpoint:');
    try {
      const generateResponse = await fetch(`${OLLAMA_API_URL}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: MODEL_NAME,
          prompt: 'Write a short poem about testing',
          stream: false,
        }),
      });
      
      console.log('Status:', generateResponse.status);
      
      if (generateResponse.ok) {
        const generateData = await generateResponse.json();
        console.log('Response:', JSON.stringify(generateData, null, 2).substring(0, 500) + '...');
      }
    } catch (error) {
      console.error('Error testing /api/generate:', error);
    }
    
  } catch (error) {
    console.error('Error testing Ollama:', error);
  }
}

testOllama(); 