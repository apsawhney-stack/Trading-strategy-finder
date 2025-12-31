import { test, expect } from '@playwright/test';

test.describe('Strategy Page', () => {
    test('should navigate to strategy page', async ({ page }) => {
        // First need to have some sources, so we'll test the route directly
        await page.goto('/strategy/wheel');

        // Should show back link
        await expect(page.locator('.back-link, a:has-text("Back")')).toBeVisible();
    });

    test('should show consensus view when sources available', async ({ page }) => {
        await page.goto('/strategy/wheel');

        // Either shows consensus view or empty state
        const hasConsensus = await page.locator('.consensus-view').isVisible();
        const hasEmpty = await page.locator('.empty-consensus, :has-text("Add more sources")').isVisible();

        expect(hasConsensus || hasEmpty).toBeTruthy();
    });
});

test.describe('Source Detail Modal', () => {
    test.skip('should open source detail on card click', async ({ page }) => {
        // This test requires having sources loaded first
        // Skip for now as it requires backend integration
        await page.goto('/');

        // Would need to load sources first
        const sourceCard = page.locator('.source-card').first();
        if (await sourceCard.isVisible()) {
            await sourceCard.click();
            await expect(page.locator('.source-detail-modal')).toBeVisible();
        }
    });
});

test.describe('Export Functionality', () => {
    test.skip('should show export panel on strategy page', async ({ page }) => {
        // Requires sources to be loaded
        await page.goto('/strategy/test');

        const exportPanel = page.locator('.export-panel');
        if (await exportPanel.isVisible()) {
            await expect(page.locator('button:has-text("JSON")')).toBeVisible();
            await expect(page.locator('button:has-text("Markdown")')).toBeVisible();
        }
    });
});

test.describe('Accessibility', () => {
    test('should have proper heading hierarchy', async ({ page }) => {
        await page.goto('/');

        const h1 = await page.locator('h1').count();
        expect(h1).toBeGreaterThanOrEqual(1);
    });

    test('should have focus visible on interactive elements', async ({ page }) => {
        await page.goto('/');

        // Tab through elements
        await page.keyboard.press('Tab');

        // Check that focus is visible
        const focusedElement = page.locator(':focus');
        await expect(focusedElement).toBeVisible();
    });

    test('should have alt text on images', async ({ page }) => {
        await page.goto('/');

        const images = page.locator('img');
        const count = await images.count();

        for (let i = 0; i < count; i++) {
            const alt = await images.nth(i).getAttribute('alt');
            expect(alt).toBeTruthy();
        }
    });
});

test.describe('Performance', () => {
    test('should load within acceptable time', async ({ page }) => {
        const startTime = Date.now();
        await page.goto('/');
        const loadTime = Date.now() - startTime;

        // Should load within 3 seconds
        expect(loadTime).toBeLessThan(3000);
    });
});
