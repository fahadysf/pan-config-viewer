// Simple script to check if the React app loads
const http = require('http');

// Make a request to the main page
http.get('http://localhost:8000/', (res) => {
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('HTML Response received:');
    console.log('Status:', res.statusCode);
    console.log('Headers:', res.headers);
    console.log('\nHTML Content (first 500 chars):');
    console.log(data.substring(0, 500));
    
    // Check if the HTML has the right structure
    if (data.includes('<div id="root"></div>')) {
      console.log('\n✓ Root div found');
    } else {
      console.log('\n✗ Root div NOT found');
    }
    
    if (data.includes('index-CcI4h4NB.js')) {
      console.log('✓ JavaScript bundle reference found');
    } else {
      console.log('✗ JavaScript bundle reference NOT found');
    }
    
    if (data.includes('index-CNCClZyS.css')) {
      console.log('✓ CSS bundle reference found');
    } else {
      console.log('✗ CSS bundle reference NOT found');
    }
  });
}).on('error', (err) => {
  console.error('Error:', err);
});

// Also check if the JS file is accessible
http.get('http://localhost:8000/assets/index-CcI4h4NB.js', (res) => {
  console.log('\n\nJavaScript Asset Check:');
  console.log('Status:', res.statusCode);
  console.log('Content-Type:', res.headers['content-type']);
  console.log('Content-Length:', res.headers['content-length']);
  
  if (res.statusCode === 200) {
    console.log('✓ JavaScript asset is accessible');
  } else {
    console.log('✗ JavaScript asset NOT accessible');
  }
}).on('error', (err) => {
  console.error('JS Asset Error:', err);
});