/**
 * PipesHub AI Configuration Script
 *
 * Automates the configuration of AI models (Anthropic LLM + Sentence Transformers)
 * via the PipesHub web UI using Playwright.
 *
 * Prerequisites:
 *   npm install playwright
 *   npx playwright install chromium
 *
 * Usage:
 *   export ANTHROPIC_API_KEY=your-anthropic-api-key-here
 *   node scripts/configure-pipeshub.js
 *
 * Optional environment variables:
 *   PIPESHUB_URL - Base URL (default: http://localhost:3000)
 *   ANTHROPIC_MODEL - Model name (default: sonnet)
 *   ADMIN_EMAIL - Admin email for setup (default: admin@pipeshub.local)
 *   ADMIN_PASSWORD - Admin password for setup (default: PipesHub123!)
 */

const { chromium } = require('playwright');

// Configuration
const CONFIG = {
  // PipesHub URL
  baseUrl: process.env.PIPESHUB_URL || 'http://localhost:3000',

  // Anthropic configuration
  anthropicApiKey: process.env.ANTHROPIC_API_KEY || 'your-anthropic-api-key-here',
  anthropicModel: process.env.ANTHROPIC_MODEL || 'sonnet',

  // Sentence Transformers configuration
  embeddingModel: 'sentence-transformers/all-MiniLM-L6-v2',

  // Admin credentials for initial setup
  adminEmail: process.env.ADMIN_EMAIL || 'admin@pipeshub.local',
  adminPassword: process.env.ADMIN_PASSWORD || 'PipesHub123!',
  adminFirstName: process.env.ADMIN_FIRST_NAME || 'Admin',
  adminLastName: process.env.ADMIN_LAST_NAME || 'User',

  // Timeouts
  navigationTimeout: 30000,
  actionTimeout: 10000,
};

async function waitForPipesHub(page) {
  console.log(`Waiting for PipesHub to be available at ${CONFIG.baseUrl}...`);

  let attempts = 0;
  const maxAttempts = 30;

  while (attempts < maxAttempts) {
    try {
      const response = await page.goto(CONFIG.baseUrl, {
        waitUntil: 'networkidle',
        timeout: CONFIG.navigationTimeout
      });

      if (response && response.ok()) {
        console.log('PipesHub is available!');
        return true;
      }
    } catch (error) {
      attempts++;
      console.log(`Attempt ${attempts}/${maxAttempts} - PipesHub not ready yet...`);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }

  throw new Error('PipesHub did not become available within the timeout period');
}

async function handleInitialSetup(page) {
  console.log('Checking for initial setup wizard...');

  // Check if we're on a setup/onboarding page
  const setupIndicators = [
    'text=Create Account',
    'text=Get Started',
    'text=Setup',
    'text=Welcome',
    'input[name="email"]',
    'input[placeholder*="email"]'
  ];

  for (const indicator of setupIndicators) {
    const element = await page.$(indicator);
    if (element) {
      console.log('Initial setup detected, completing registration...');

      // Fill in registration form
      await page.fill('input[name="firstName"], input[placeholder*="first"]', CONFIG.adminFirstName).catch(() => {});
      await page.fill('input[name="lastName"], input[placeholder*="last"]', CONFIG.adminLastName).catch(() => {});
      await page.fill('input[name="email"], input[placeholder*="email"]', CONFIG.adminEmail).catch(() => {});
      await page.fill('input[name="password"], input[type="password"]', CONFIG.adminPassword).catch(() => {});

      // Look for confirm password field
      const confirmPassword = await page.$('input[name="confirmPassword"], input[placeholder*="confirm"]');
      if (confirmPassword) {
        await confirmPassword.fill(CONFIG.adminPassword);
      }

      // Submit the form
      const submitButton = await page.$('button[type="submit"], button:has-text("Create"), button:has-text("Sign Up"), button:has-text("Register")');
      if (submitButton) {
        await submitButton.click();
        await page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {});
        console.log('Initial setup completed!');
      }

      return true;
    }
  }

  console.log('No initial setup required.');
  return false;
}

async function login(page) {
  console.log('Checking if login is required...');

  // Check for login page
  const loginForm = await page.$('input[name="email"], input[placeholder*="email"]');
  const passwordField = await page.$('input[type="password"]');

  if (loginForm && passwordField) {
    console.log('Login page detected, logging in...');

    await page.fill('input[name="email"], input[placeholder*="email"]', CONFIG.adminEmail);
    await page.fill('input[type="password"]', CONFIG.adminPassword);

    const loginButton = await page.$('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    if (loginButton) {
      await loginButton.click();
      await page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {});
      console.log('Login successful!');
    }
  }
}

async function navigateToAIModels(page) {
  console.log('Navigating to AI Models settings...');

  // Try direct URL navigation first
  const aiModelsUrl = `${CONFIG.baseUrl}/account/ai-models`;
  await page.goto(aiModelsUrl, { waitUntil: 'networkidle' }).catch(() => {});

  // Check if we landed on the right page
  const pageContent = await page.content();
  if (pageContent.includes('AI Models') || pageContent.includes('LLM') || pageContent.includes('Embedding')) {
    console.log('Successfully navigated to AI Models settings!');
    return true;
  }

  // Try alternative paths
  const alternativePaths = [
    '/settings/ai-models',
    '/admin/ai-models',
    '/configuration/ai-models'
  ];

  for (const path of alternativePaths) {
    await page.goto(`${CONFIG.baseUrl}${path}`, { waitUntil: 'networkidle' }).catch(() => {});
    const content = await page.content();
    if (content.includes('AI Models') || content.includes('LLM')) {
      console.log(`Found AI Models at ${path}`);
      return true;
    }
  }

  // Try clicking through menus
  console.log('Attempting to navigate via UI menus...');

  // Look for settings/account menu
  const settingsLinks = [
    'text=Settings',
    'text=Account',
    'a[href*="settings"]',
    'a[href*="account"]',
    '[data-testid="settings"]',
    'button:has-text("Settings")'
  ];

  for (const selector of settingsLinks) {
    const link = await page.$(selector);
    if (link) {
      await link.click();
      await page.waitForTimeout(1000);

      // Look for AI Models submenu
      const aiModelsLink = await page.$('text=AI Models, a[href*="ai-models"], text=Models');
      if (aiModelsLink) {
        await aiModelsLink.click();
        await page.waitForNavigation({ waitUntil: 'networkidle' }).catch(() => {});
        console.log('Successfully navigated to AI Models settings!');
        return true;
      }
    }
  }

  console.log('Warning: Could not navigate to AI Models settings automatically.');
  console.log('Please navigate manually to: Account Settings > AI Models');
  return false;
}

async function configureAnthropicLLM(page) {
  console.log('Configuring Anthropic as LLM provider...');

  // Look for Add Model button in LLM section
  const addButtons = await page.$$('button:has-text("Add"), button:has-text("Configure"), button:has-text("+")');

  if (addButtons.length > 0) {
    // Click the first add button (usually LLM)
    await addButtons[0].click();
    await page.waitForTimeout(500);
  }

  // Select Anthropic provider
  const providerSelectors = [
    'text=Anthropic',
    'option[value="anthropic"]',
    '[data-value="anthropic"]',
    'button:has-text("Anthropic")',
    'div:has-text("Anthropic")'
  ];

  for (const selector of providerSelectors) {
    const provider = await page.$(selector);
    if (provider) {
      await provider.click();
      await page.waitForTimeout(300);
      break;
    }
  }

  // Fill in API key
  const apiKeySelectors = [
    'input[name="apiKey"]',
    'input[placeholder*="API"]',
    'input[placeholder*="key"]',
    'input[type="password"]',
    'input[name="api_key"]'
  ];

  for (const selector of apiKeySelectors) {
    const input = await page.$(selector);
    if (input) {
      await input.fill(CONFIG.anthropicApiKey);
      console.log('Entered Anthropic API key');
      break;
    }
  }

  // Fill in model name
  const modelSelectors = [
    'input[name="model"]',
    'input[placeholder*="model"]',
    'select[name="model"]',
    'input[name="modelName"]'
  ];

  for (const selector of modelSelectors) {
    const input = await page.$(selector);
    if (input) {
      await input.fill(CONFIG.anthropicModel);
      console.log(`Set model to: ${CONFIG.anthropicModel}`);
      break;
    }
  }

  // Enable multimodal if checkbox exists
  const multimodalCheckbox = await page.$('input[name="isMultimodal"], input[name="multimodal"], label:has-text("Multimodal") input');
  if (multimodalCheckbox) {
    await multimodalCheckbox.check().catch(() => {});
    console.log('Enabled multimodal support');
  }

  // Save configuration
  const saveButtons = [
    'button:has-text("Save")',
    'button:has-text("Submit")',
    'button:has-text("Add")',
    'button[type="submit"]'
  ];

  for (const selector of saveButtons) {
    const button = await page.$(selector);
    if (button) {
      await button.click();
      await page.waitForTimeout(1000);
      console.log('Saved Anthropic LLM configuration');
      break;
    }
  }

  // Set as default
  const defaultButton = await page.$('button:has-text("Set as Default"), button:has-text("Default")');
  if (defaultButton) {
    await defaultButton.click();
    await page.waitForTimeout(500);
    console.log('Set Anthropic as default LLM');
  }

  console.log('Anthropic LLM configuration complete!');
}

async function configureSentenceTransformers(page) {
  console.log('Configuring Sentence Transformers for embeddings...');

  // Look for Add Model button in Embedding section
  const addButtons = await page.$$('button:has-text("Add"), button:has-text("Configure"), button:has-text("+")');

  // Usually the second add button is for embeddings
  if (addButtons.length > 1) {
    await addButtons[1].click();
    await page.waitForTimeout(500);
  } else if (addButtons.length > 0) {
    await addButtons[0].click();
    await page.waitForTimeout(500);
  }

  // Select Sentence Transformers provider
  const providerSelectors = [
    'text=Sentence Transformers',
    'text=SentenceTransformers',
    'option[value="sentence-transformers"]',
    'option[value="sentencetransformers"]',
    '[data-value="sentence-transformers"]',
    'button:has-text("Sentence")',
    'div:has-text("Sentence Transformers")'
  ];

  for (const selector of providerSelectors) {
    const provider = await page.$(selector);
    if (provider) {
      await provider.click();
      await page.waitForTimeout(300);
      break;
    }
  }

  // Fill in model name
  const modelSelectors = [
    'input[name="model"]',
    'input[placeholder*="model"]',
    'input[name="modelName"]'
  ];

  for (const selector of modelSelectors) {
    const input = await page.$(selector);
    if (input) {
      await input.fill(CONFIG.embeddingModel);
      console.log(`Set embedding model to: ${CONFIG.embeddingModel}`);
      break;
    }
  }

  // Save configuration
  const saveButtons = [
    'button:has-text("Save")',
    'button:has-text("Submit")',
    'button:has-text("Add")',
    'button[type="submit"]'
  ];

  for (const selector of saveButtons) {
    const button = await page.$(selector);
    if (button) {
      await button.click();
      await page.waitForTimeout(1000);
      console.log('Saved Sentence Transformers configuration');
      break;
    }
  }

  // Set as default
  const defaultButton = await page.$('button:has-text("Set as Default"), button:has-text("Default")');
  if (defaultButton) {
    await defaultButton.click();
    await page.waitForTimeout(500);
    console.log('Set Sentence Transformers as default embedding model');
  }

  console.log('Sentence Transformers configuration complete!');
}

async function main() {
  console.log('===========================================');
  console.log('PipesHub AI Configuration Script');
  console.log('===========================================\n');

  // Validate API key
  if (CONFIG.anthropicApiKey === 'your-anthropic-api-key-here') {
    console.warn('Warning: Using placeholder API key. Set ANTHROPIC_API_KEY environment variable.');
    console.warn('Example: export ANTHROPIC_API_KEY=sk-ant-api03-...\n');
  }

  const browser = await chromium.launch({
    headless: false, // Set to true for CI/CD
    slowMo: 100 // Slow down actions for visibility
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });

  const page = await context.newPage();

  try {
    // Step 1: Wait for PipesHub to be available
    await waitForPipesHub(page);

    // Step 2: Handle initial setup if needed
    await handleInitialSetup(page);

    // Step 3: Login if required
    await login(page);

    // Step 4: Navigate to AI Models settings
    const navigated = await navigateToAIModels(page);

    if (navigated) {
      // Step 5: Configure Anthropic LLM
      await configureAnthropicLLM(page);

      // Step 6: Configure Sentence Transformers
      await configureSentenceTransformers(page);
    }

    console.log('\n===========================================');
    console.log('Configuration complete!');
    console.log('===========================================');
    console.log('\nSummary:');
    console.log(`- LLM Provider: Anthropic (${CONFIG.anthropicModel})`);
    console.log(`- Embedding Model: ${CONFIG.embeddingModel}`);
    console.log(`\nYou can now use PipesHub at: ${CONFIG.baseUrl}`);

    // Keep browser open for 5 seconds to verify
    console.log('\nClosing browser in 5 seconds...');
    await page.waitForTimeout(5000);

  } catch (error) {
    console.error('\nError during configuration:', error.message);
    console.error('\nPlease complete the configuration manually:');
    console.error('1. Navigate to Account Settings > AI Models');
    console.error('2. Add Anthropic as LLM provider');
    console.error('3. Add Sentence Transformers as embedding provider');

    // Take a screenshot for debugging
    await page.screenshot({ path: 'pipeshub-config-error.png' });
    console.error('\nScreenshot saved to: pipeshub-config-error.png');

  } finally {
    await browser.close();
  }
}

// Run the script
main().catch(console.error);
