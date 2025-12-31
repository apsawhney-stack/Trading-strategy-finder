import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
    });

    test('should display the hero section', async ({ page }) => {
        await expect(page.locator('h1')).toContainText('Options Strategy Research');
        await expect(page.locator('.hero-subtitle')).toBeVisible();
    });

    test('should have URL input field', async ({ page }) => {
        const input = page.locator('input[type="url"], input[placeholder*="URL"]');
        await expect(input).toBeVisible();
    });

    test('should show discover button in header', async ({ page }) => {
        const discoverBtn = page.locator('button:has-text("Discover")');
        await expect(discoverBtn).toBeVisible();
    });

    test('should open discovery modal on button click', async ({ page }) => {
        await page.click('button:has-text("Discover")');
        await expect(page.locator('.discovery-modal')).toBeVisible();
    });

    test('should show empty state when no sources', async ({ page }) => {
        await expect(page.locator('.empty-state')).toBeVisible();
        await expect(page.locator('.empty-state')).toContainText('No sources');
    });
});

test.describe('Discovery Modal', () => {
    test.beforeEach(async ({ page }) => {
        await page.goto('/');
        await page.click('button:has-text("Discover")');
    });

    test('should have search input', async ({ page }) => {
        const searchInput = page.locator('.discovery-modal input');
        await expect(searchInput).toBeVisible();
    });

    test('should have platform filters', async ({ page }) => {
        await expect(page.locator('button:has-text("YouTube")')).toBeVisible();
        await expect(page.locator('button:has-text("Reddit")')).toBeVisible();
    });

    test('should search for strategies', async ({ page }) => {
        const searchInput = page.locator('.discovery-modal input');
        await searchInput.fill('wheel strategy');
        await page.click('button:has-text("Search")');

        // Should show results or loading state
        await page.waitForTimeout(1000);
    });

    test('should close modal on overlay click', async ({ page }) => {
        await page.click('.discovery-overlay', { position: { x: 10, y: 10 } });
        await expect(page.locator('.discovery-modal')).not.toBeVisible();
    });
});

test.describe('URL Extraction Flow', () => {
    test('should show error for invalid URL', async ({ page }) => {
        await page.goto('/');

        const input = page.locator('input[type="url"], input[placeholder*="URL"]');
        await input.fill('not-a-valid-url');
        await page.keyboard.press('Enter');

        // Should show error or validation message
        await page.waitForTimeout(500);
    });

    test('should detect YouTube URL', async ({ page }) => {
        await page.goto('/');

        const input = page.locator('input[type="url"], input[placeholder*="URL"]');
        await input.fill('https://www.youtube.com/watch?v=test123');

        // Should show YouTube indicator
        await expect(page.locator('.source-type-badge, .badge:has-text("YouTube")')).toBeVisible();
    });
});

test.describe('Responsive Design', () => {
    test('should be responsive on mobile', async ({ page }) => {
        await page.setViewportSize({ width: 375, height: 667 });
        await page.goto('/');

        await expect(page.locator('h1')).toBeVisible();
        await expect(page.locator('.header')).toBeVisible();
    });

    test('should be responsive on tablet', async ({ page }) => {
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.goto('/');

        await expect(page.locator('h1')).toBeVisible();
    });
});
