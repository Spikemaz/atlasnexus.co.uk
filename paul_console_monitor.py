"""
Paul Console Error Monitor - Detects and reports JavaScript console errors
"""

import json
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] PAUL CONSOLE: %(message)s',
    handlers=[
        logging.FileHandler('paul_developer.log'),
        logging.StreamHandler()
    ]
)

class PaulConsoleMonitor:
    def __init__(self):
        self.site_url = "https://atlasnexus.co.uk"
        self.errors_found = []

    def setup_driver(self):
        """Setup Chrome driver to capture console logs"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

        driver = webdriver.Chrome(options=options)
        return driver

    def check_console_errors(self, page_url):
        """Check for console errors on a page"""
        driver = self.setup_driver()
        errors = []

        try:
            logging.info(f"🔍 Checking {page_url} for console errors...")
            driver.get(page_url)
            time.sleep(3)  # Wait for page to load

            # Get browser logs
            logs = driver.get_log('browser')

            for log in logs:
                if 'SEVERE' in log['level'] or 'ERROR' in log['message']:
                    errors.append({
                        'level': log['level'],
                        'message': log['message'],
                        'timestamp': log['timestamp']
                    })

            return errors

        finally:
            driver.quit()

    def analyze_errors(self, errors):
        """Analyze errors and create fix recommendations"""
        fixes = []

        for error in errors:
            msg = error['message']

            if 'toFixed is not a function' in msg:
                fixes.append({
                    'error': 'FRED data formatting error',
                    'cause': 'Value is not a number when calling toFixed()',
                    'fix': 'Add type checking before formatting',
                    'file': 'dashboard.html',
                    'line': 'formatValue function'
                })

            if '404 (Not Found)' in msg and '/api/projects/' in msg:
                fixes.append({
                    'error': 'Project deletion 404',
                    'cause': 'Project not found in backend',
                    'fix': 'Update deletion to use new trash system endpoint',
                    'file': 'dashboard.html',
                    'line': 'confirmDelete function'
                })

        return fixes

    def notify_claude(self, errors, fixes):
        """Send error report to Claude"""
        report = {
            'type': 'CONSOLE_ERROR_REPORT',
            'from': 'PAUL',
            'timestamp': datetime.now().isoformat(),
            'errors': errors,
            'fixes': fixes,
            'action': 'fix_required',
            'message': f"Found {len(errors)} console errors that need fixing!"
        }

        with open('paul_to_claude.json', 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"❌ Found {len(errors)} console errors!")
        logging.info("📨 Error report sent to Claude for fixing")

    def monitor_loop(self):
        """Main monitoring loop"""
        logging.info("=" * 70)
        logging.info("PAUL CONSOLE ERROR MONITOR ACTIVE")
        logging.info("=" * 70)

        pages_to_check = [
            f"{self.site_url}/dashboard",
            f"{self.site_url}/admin-panel"
        ]

        while True:
            try:
                all_errors = []

                for page in pages_to_check:
                    errors = self.check_console_errors(page)
                    if errors:
                        all_errors.extend(errors)

                if all_errors:
                    fixes = self.analyze_errors(all_errors)
                    self.notify_claude(all_errors, fixes)
                else:
                    logging.info("✅ No console errors found")

                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logging.error(f"Monitor error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = PaulConsoleMonitor()
    monitor.monitor_loop()