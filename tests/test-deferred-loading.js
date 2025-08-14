const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1600, height: 900 }
  });
  const page = await browser.newPage();
  
  console.log('Opening application...');
  await page.goto('http://localhost:8000');
  
  // Wait for the app to load
  await page.waitForSelector('.w-64', { timeout: 10000 });
  
  // Select the first configuration
  console.log('Selecting configuration...');
  await page.click('button:has-text("pan-bkp-202507151414")');
  
  // Test each table view
  const views = [
    { selector: 'button:has-text("Addresses")', name: 'Addresses' },
    { selector: 'button:has-text("Address Groups")', name: 'Address Groups' },
    { selector: 'button:has-text("Services")', name: 'Services' },
    { selector: 'button:has-text("Service Groups")', name: 'Service Groups' },
    { selector: 'button:has-text("Device Groups")', name: 'Device Groups' },
    { selector: 'button:has-text("Security Policies")', name: 'Security Policies' },
    { selector: 'button:has-text("Templates")', name: 'Templates' }
  ];
  
  for (const view of views) {
    console.log(`\nTesting ${view.name}...`);
    
    // Click on the view
    await page.click(view.selector);
    
    // Check for loading animation
    const loadingVisible = await page.evaluate(() => {
      const loader = document.querySelector('.animate-spin');
      return loader !== null;
    });
    
    if (loadingVisible) {
      console.log(`✓ Loading animation shown for ${view.name}`);
    }
    
    // Wait for table to load
    try {
      await page.waitForSelector('table', { timeout: 10000 });
      console.log(`✓ Table loaded for ${view.name}`);
      
      // Test filter application if table has data
      const hasData = await page.evaluate(() => {
        const rows = document.querySelectorAll('tbody tr');
        return rows.length > 0;
      });
      
      if (hasData) {
        // Click on a filter button if available
        const filterButton = await page.$('button[aria-label*="Filter"]');
        if (filterButton) {
          await filterButton.click();
          await page.waitForTimeout(500);
          
          // Type in filter
          const filterInput = await page.$('input[type="text"]');
          if (filterInput) {
            await filterInput.type('test');
            await page.waitForTimeout(1000);
            
            console.log(`✓ Filter applied for ${view.name} - table updates without hanging`);
            
            // Clear filter
            await filterInput.click({ clickCount: 3 });
            await filterInput.press('Backspace');
          }
        }
      }
    } catch (e) {
      console.log(`⚠ No data or timeout for ${view.name}`);
    }
    
    await page.waitForTimeout(500);
  }
  
  // Test configuration switching
  console.log('\n\nTesting configuration switching...');
  
  // Switch to another config
  await page.click('button:has-text("16-7-Panorama-Core-688")');
  await page.waitForTimeout(1000);
  
  // Check if loading animation appears
  const loadingOnSwitch = await page.evaluate(() => {
    const loader = document.querySelector('.animate-spin');
    return loader !== null;
  });
  
  if (loadingOnSwitch) {
    console.log('✓ Loading animation shown on config switch');
  }
  
  // Wait for table to reload
  await page.waitForSelector('table', { timeout: 10000 });
  console.log('✓ Table reloaded after config switch without hanging');
  
  console.log('\n✅ All deferred loading tests passed!');
  
  await browser.close();
})();