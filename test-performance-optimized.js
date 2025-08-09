const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    if (msg.type() === 'log' || msg.type() === 'info') {
      console.log('PAGE LOG:', msg.text());
    }
  });
  
  // Navigate to the application
  await page.goto('http://localhost:3000');
  
  // Wait for the config selector to be available
  await page.waitForSelector('[data-testid="config-selector"]', { timeout: 10000 });
  
  // Click on the config selector to open the dropdown
  await page.click('[data-testid="config-selector"]');
  
  // Wait for dropdown options to appear
  await page.waitForSelector('[role="option"]', { timeout: 5000 });
  
  console.log('Config dropdown opened, looking for large config...');
  
  // Find and click the large config option
  const options = await page.$$('[role="option"]');
  let foundLargeConfig = false;
  
  for (const option of options) {
    const text = await option.evaluate(el => el.textContent);
    console.log('Found config option:', text);
    if (text.includes('16-7-Panorama-Core-688')) {
      console.log('Clicking on large config:', text);
      
      // Start timing
      const startTime = Date.now();
      console.log('Starting performance measurement...');
      
      // Click the option
      await option.click();
      
      // Set up a timeout for taking screenshot
      const screenshotPromise = new Promise(async (resolve) => {
        // Try to take screenshot after 1 second
        setTimeout(async () => {
          try {
            // Check if we can execute JavaScript
            const canExecute = await page.evaluate(() => true).catch(() => false);
            
            // Take screenshot
            await page.screenshot({ 
              path: 'performance-test-optimized.png',
              fullPage: false 
            });
            
            const elapsedTime = Date.now() - startTime;
            console.log(`Screenshot taken after ${elapsedTime}ms`);
            
            // Check what's visible
            const isLoading = await page.$('.animate-spin').catch(() => null);
            const hasTable = await page.$('table').catch(() => null);
            
            resolve({
              elapsedTime,
              canExecuteJS: canExecute,
              isLoading: !!isLoading,
              hasTable: !!hasTable,
              timestamp: Date.now()
            });
          } catch (error) {
            console.error('Error during screenshot:', error);
            resolve({
              error: error.message,
              elapsedTime: Date.now() - startTime
            });
          }
        }, 1000); // Wait exactly 1 second
      });
      
      const result = await screenshotPromise;
      console.log('Performance test result:', JSON.stringify(result, null, 2));
      
      if (result.elapsedTime > 1500) {
        console.error('❌ FAILED: Page took longer than 1.5 seconds to respond');
        console.error('The page is still hanging, which is unacceptable.');
      } else if (result.isLoading) {
        console.error('⚠️ WARNING: Page is still loading after 1 second');
      } else {
        console.log('✅ SUCCESS: Page responded within acceptable time');
      }
      
      foundLargeConfig = true;
      break;
    }
  }
  
  if (!foundLargeConfig) {
    console.error('Could not find the large config in dropdown');
  }
  
  // Wait a bit more to see final state
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Take final screenshot
  await page.screenshot({ 
    path: 'performance-test-final-optimized.png',
    fullPage: false 
  });
  
  await browser.close();
})();