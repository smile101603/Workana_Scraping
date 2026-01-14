"""
Test script for Slack notifications
Run this to verify your Slack webhook is working
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import SLACK_WEBHOOK_URL, ENABLE_SLACK_NOTIFICATIONS
from utils.slack_notifier import SlackNotifier
from utils.translator import DeepLTranslator

def test_slack():
    """Test Slack webhook connection"""
    print("=" * 60)
    print("Slack Notification Test")
    print("=" * 60)
    
    # Check configuration
    print(f"\n1. Checking configuration...")
    print(f"   SLACK_WEBHOOK_URL set: {bool(SLACK_WEBHOOK_URL)}")
    print(f"   ENABLE_SLACK_NOTIFICATIONS: {ENABLE_SLACK_NOTIFICATIONS}")
    
    if SLACK_WEBHOOK_URL:
        print(f"   Webhook URL: {SLACK_WEBHOOK_URL[:50]}...")
    else:
        print("   ❌ No webhook URL configured!")
        print("\n   To set webhook URL:")
        print("   - Set environment variable: SLACK_WEBHOOK_URL")
        print("   - Or edit config/settings.py")
        return
    
    # Initialize translator
    print(f"\n2. Initializing DeepL translator...")
    translator = DeepLTranslator()
    if translator.is_available():
        print("   ✅ DeepL translator available")
    else:
        print("   ⚠️  DeepL translator not available (no API key)")
        translator = None
    
    # Initialize notifier
    print(f"\n3. Initializing Slack notifier...")
    notifier = SlackNotifier(SLACK_WEBHOOK_URL, translator=translator)
    
    # Test simple message
    print(f"\n4. Sending test message...")
    success = notifier.send_message("🧪 Test message from Workana Scraper!")
    
    if success:
        print("\n✅ SUCCESS! Check your Slack channel for the test message.")
        print("   If you see it, your Slack integration is working!")
    else:
        print("\n❌ FAILED! Check the error messages above.")
        print("\n   Common issues:")
        print("   - Invalid webhook URL")
        print("   - Webhook URL expired or revoked")
        print("   - No internet connection")
        print("   - Slack service temporarily unavailable")
    
    # Test job notification format
    if success:
        print(f"\n5. Testing job notification format...")
        test_job = {
            'id': 'test-job-123',
            'title': 'Test Job - Web Developer Needed',
            'url': 'https://www.workana.com/job/test-job',
            'posted_date_relative': 'Just now',
            'budget': 'USD 100 - 250',
            'bids_count': 5,
            'client_country': 'United States',
            'client_rating': 4.5,
            'skills': ['Python', 'JavaScript', 'React'],
            'description': 'We are looking for an experienced web developer to build a modern web application. The project requires expertise in Python backend development and React frontend. Must have experience with REST APIs and database design.'
        }
        
        success2 = notifier.send_new_jobs([test_job], total_scraped=1)
        if success2:
            print("✅ Job notification format test successful!")
        else:
            print("❌ Job notification format test failed")

if __name__ == "__main__":
    test_slack()

