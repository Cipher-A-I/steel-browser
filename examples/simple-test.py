# steel-cdp-test.py - Simple CDP connection test without AI
import asyncio
import uuid
import requests
from playwright.async_api import async_playwright

async def test_steel_cdp():
    """Test Steel Browser CDP connection with Playwright"""
    
    # Create a session
    session_id = str(uuid.uuid4())
    api_url = "http://localhost:3000"
    
    print(f"Creating session: {session_id}")
    
    # Create session
    response = requests.post(
        f"{api_url}/v1/sessions",
        json={"sessionId": session_id}
    )
    response.raise_for_status()
    session_data = response.json()
    
    print(f"Session created!")
    print(f"CDP URL: {session_data['websocketUrl']}")
    print(f"View at: {session_data['sessionViewerUrl']}")
    
    # Connect with Playwright
    async with async_playwright() as p:
        # Connect to the CDP endpoint
        browser = await p.chromium.connect_over_cdp(session_data['websocketUrl'])
        
        # Get the default context and page
        contexts = browser.contexts
        if contexts:
            page = contexts[0].pages[0]
        else:
            context = await browser.new_context()
            page = await context.new_page()
        
        # Navigate to a page
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        
        # Take a screenshot
        await page.screenshot(path="steel-screenshot.png")
        print("Screenshot saved as steel-screenshot.png")
        
        # Get page title
        title = await page.title()
        print(f"Page title: {title}")
        
        # Wait a bit so you can see it in the viewer
        print("Waiting 10 seconds... Check the session viewer!")
        await asyncio.sleep(10)
        
        # Close the browser
        await browser.close()
    
    # Release the session
    requests.post(f"{api_url}/v1/sessions/{session_id}/release")
    print("Session released!")

if __name__ == "__main__":
    asyncio.run(test_steel_cdp())