# steel-ai-agent.py - AI agent automation with Steel Browser
import asyncio
import logging
import os
import sys
import uuid
from pprint import pprint

import requests
from browser_use import Agent, Browser, BrowserConfig
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("playwright").setLevel(logging.WARNING)


class SteelBrowserSession:
    """Manages a Steel Browser session for AI agent automation"""
    
    def __init__(self, api_url="http://localhost:3000"):
        self.api_url = api_url
        self.session_id = None
        self.cdp_url = None
        self.session_data = None
        
    def create_session(self):
        """Create a new Steel browser session"""
        # Generate a UUID for the session
        self.session_id = str(uuid.uuid4())
        
        logger.info(f"Creating Steel session with ID: {self.session_id}")
        
        # Create session via Steel API
        response = requests.post(
            f"{self.api_url}/v1/sessions",
            json={"sessionId": self.session_id},
            timeout=30
        )
        response.raise_for_status()
        
        self.session_data = response.json()
        self.cdp_url = self.session_data.get("websocketUrl", f"ws://localhost:3000/")
        
        logger.info(f"""
╔══════════════════════════════════════════════════════════════════
║ STEEL SESSION CREATED
║ ID: {self.session_id}
║ CDP URL: {self.cdp_url}
║ Debug URL: {self.session_data.get('debugUrl')}
║ Session Viewer: {self.session_data.get('sessionViewerUrl')}
╚══════════════════════════════════════════════════════════════════
""")
        
        return self.cdp_url
    
    def get_session_details(self):
        """Get current session details"""
        response = requests.get(
            f"{self.api_url}/v1/sessions/{self.session_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    
    def release_session(self):
        """Release the browser session"""
        if not self.session_id:
            return
            
        try:
            response = requests.post(
                f"{self.api_url}/v1/sessions/{self.session_id}/release",
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Session {self.session_id} released successfully")
            else:
                logger.warning(f"⚠️ Session release returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Failed to release session: {e}")


async def run_ai_agent_task(api_url="http://localhost:3000"):
    """
    Run an AI agent task using Steel Browser
    """
    print("\n" + "="*80)
    print("🤖 STEEL BROWSER AI AGENT TEST")
    print("="*80)
    
    # Create Steel session
    steel_session = SteelBrowserSession(api_url)
    
    try:
        # Create a new browser session
        cdp_url = steel_session.create_session()
        
        # Initialize browser with Steel's CDP URL
        browser = Browser(
            config=BrowserConfig(
                headless=False,  # Set to False to see the browser
                cdp_url=cdp_url,
            )
        )
        
        logger.info("🌐 Browser connected to Steel CDP endpoint")
        
        # Define the task for the AI agent
        task = """
        1. Go to https://github.com/steel-dev/steel-browser
        2. Wait for the page to load
        3. Scroll down to see the README
        4. Click on the "Star" button if visible (you may need to be logged in)
        5. Navigate to the Issues tab
        6. Take a screenshot of the issues page
        7. Go back to the main repository page
        8. Find and report the number of stars, forks, and watchers
        """
        
        # Alternative simpler task for testing
        simple_task = """
        1. Go to https://example.com
        2. Take a screenshot
        3. Find and click on the "More information..." link
        4. Wait for the new page to load
        5. Go back to the previous page
        6. Report what you found
        """
        
        # Create the AI agent
        agent = Agent(
            task=simple_task,  # Use simple_task for basic testing
            llm=ChatAnthropic(
                model_name="claude-3-5-sonnet-20241022",
                api_key=os.getenv("ANTHROPIC_API_KEY")  # Make sure to set this
            ),
            browser=browser,
        )
        
        logger.info("🎯 Running AI agent with task...")
        print("-"*80)
        
        # Run the agent
        result = await agent.run()
        
        print("-"*80)
        logger.info("✅ Agent task completed successfully")
        
        # Print the result
        print("\n📊 AGENT RESULT:")
        print("="*80)
        pprint(result)
        print("="*80)
        
        # Get session details to see recording info
        session_details = steel_session.get_session_details()
        if session_details:
            print(f"\n📹 Session Recording Available:")
            print(f"   View at: {session_details.get('sessionViewerUrl')}")
            print(f"   Debug at: {session_details.get('debugUrl')}")
        
        # Wait a bit before closing
        logger.info("⏳ Waiting 5 seconds before cleanup...")
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"❌ Agent execution failed: {e}")
        logger.exception(e)
        
    finally:
        # Clean up
        try:
            await browser.close()
            logger.info("🔐 Browser closed")
        except Exception as e:
            logger.error(f"❌ Failed to close browser: {e}")
        
        # Release the session
        steel_session.release_session()
    
    print("\n" + "="*80)
    print("✨ TEST COMPLETE")
    print("="*80)


async def test_basic_connection(api_url="http://localhost:3000"):
    """Test basic connection without AI agent"""
    print("\n🧪 Testing basic Steel Browser connection...")
    
    steel_session = SteelBrowserSession(api_url)
    cdp_url = steel_session.create_session()
    
    print(f"✅ Session created successfully!")
    print(f"📺 View live session at: http://localhost:5173")
    print(f"🔍 Or debug at: http://localhost:3000/v1/sessions/debug")
    
    # Keep session alive for 30 seconds
    print("\n⏰ Session will stay active for 30 seconds...")
    await asyncio.sleep(30)
    
    steel_session.release_session()


async def main():
    """Main entry point"""
    # Steel Browser API endpoint (adjust if needed)
    api_url = os.getenv("STEEL_API_URL", "http://localhost:3000")
    
    # Check for Anthropic API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  No ANTHROPIC_API_KEY found in environment")
        print("   You can:")
        print("   1. Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("   2. Add it to a .env file")
        print("   3. Run the basic connection test instead")
        print("")
        
        choice = input("Run basic connection test? (y/n): ")
        if choice.lower() == 'y':
            await test_basic_connection(api_url)
        return
    
    # Run the AI agent task
    await run_ai_agent_task(api_url)


if __name__ == "__main__":
    asyncio.run(main())