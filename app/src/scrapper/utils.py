from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import glob
from datetime import datetime, timedelta
import urllib.parse
class Scrapper:

    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None

    def _initialize_driver(self, download_dir=None):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        
        if download_dir:
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            self.options.add_experimental_option("prefs", prefs)
        
        if self.headless:
            self.options.add_argument("--headless=new")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=self.options,
                                       service=Service(ChromeDriverManager().install()))

    def _set_download_directory(self, download_dir):
        if self.driver is not None:
            self.driver.quit()
        self._initialize_driver(download_dir)

    def _download_file(self, url, download_dir):
            # Ensure download directory exists
        os.makedirs(download_dir, exist_ok=True)
        
        # Delete existing files in the download directory
        for file_path in glob.glob(os.path.join(download_dir, '*'))+glob.glob(os.path.join(download_dir, '.*')):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted existing file: {file_path}")
                else:
                    print(f"Skipping non-file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        # Set the download directory for this specific file
        self._set_download_directory(download_dir)
        
        # Open the page and trigger the download
        self.driver.get(url)
        
        # Login process
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')

        email_input = self.driver.find_element('id', 'Email')
        password_input = self.driver.find_element('id', 'Password')

        if email and password:
            email_input.send_keys(email)
            password_input.send_keys(password)
            login_button = self.driver.find_element('xpath', '//button[@type="submit"]')
            login_button.click()

        # Optional: Wait until the download completes, if necessary
        
        # Close the driver
        self.driver.quit()

    
    def get_report(self, report_type: str, period: str, category: str = None):
        """
        Args:
            report_type (str): ("invoice", "profit", "products_profit").
            period (str): ("daily", "monthly").
            category (str, optional): The name of the product category. Defaults to None for uncategorized products' profit.
        """
        # Define paths for different report types and categories
        category_paths = {
            'SUN': {
                'daily': os.getenv('DAILY_SUN_PROFIT'),
                'monthly': os.getenv('MONTHLY_SUN_PROFIT'),
            },
            'OPTICAL': {
                'daily': os.getenv('DAILY_OPTICAL_PROFIT'),
                'monthly': os.getenv('MONTHLY_OPTICAL_PROFIT'),
            },
            'CHAIN': {
                'daily': os.getenv('DAILY_CHAIN_PROFIT'),
                'monthly': os.getenv('MONTHLY_CHAIN_PROFIT'),
            },
            'Single Vision': {
                'daily': os.getenv('DAILY_SINGLE_VISION_PROFIT'),
                'monthly': os.getenv('MONTHLY_SINGLE_VISION_PROFIT'),
            },
            'single vision tra': {
                'daily': os.getenv('DAILY_SINGLE_VISION_TRA_PROFIT'),
                'monthly': os.getenv('MONTHLY_SINGLE_VISION_TRA_PROFIT'),
            },
            'progressive': {
                'daily': os.getenv('DAILY_PROGRESSIVE_PROFIT'),
                'monthly': os.getenv('MONTHLY_PROGRESSIVE_PROFIT'),
            },
            'CLEAR CONTACT LENS': {
                'daily': os.getenv('DAILY_CLEAR_CONTACT_LENS_PROFIT'),
                'monthly': os.getenv('MONTHLY_CLEAR_CONTACT_LENS_PROFIT'),
            },
            'COLOR CONTACT LENS': {
                'daily': os.getenv('DAILY_COLOR_CONTACT_LENS_PROFIT'),
                'monthly': os.getenv('MONTHLY_COLOR_CONTACT_LENS_PROFIT'),
            },
            'DIVEL SINGLE VISION': {
                'daily': os.getenv('DAILY_DIVEL_SINGLE_VISION_PROFIT'),
                'monthly': os.getenv('MONTHLY_DIVEL_SINGLE_VISION_PROFIT'),
            },
            'RODEN STOCK PROGRESSIVE': {
                'daily': os.getenv('DAILY_RODENSTOCK_PROGRESSIVE_PROFIT'),
                'monthly': os.getenv('MONTHLY_RODENSTOCK_PROGRESSIVE_PROFIT'),
            },
            'RODENSTOCK SINGLE': {
                'daily': os.getenv('DAILY_RODENSTOCK_SINGLE_PROFIT'),
                'monthly': os.getenv('MONTHLY_RODENSTOCK_SINGLE_PROFIT'),
            },
        }

        # Define category IDs
        category_ids = {
            'SUN': 9,
            'OPTICAL': 10,
            'CHAIN': 11,
            'Single Vision': 13,
            'single vision tra': 14,
            'progressive': 15,
            'CLEAR CONTACT LENS': 16,
            'COLOR CONTACT LENS': 17,
            'DIVEL SINGLE VISION': 18,
            'RODEN STOCK PROGRESSIVE': 19,
            'RODENSTOCK SINGLE': 20,
        }

        # Set the date range based on the period
        if period == 'daily':
            date_to = datetime.today().strftime('%d/%m/%Y')
            date_from = date_to
        else:
            date_to = datetime.today().strftime('%d/%m/%Y')
            date_from = datetime.today().replace(day=1).strftime('%d/%m/%Y')

        date_from_encoded = urllib.parse.quote(date_from)
        date_to_encoded = urllib.parse.quote(date_to)

        # Report URLs for uncategorized 'invoice' and 'profit' reports
        report_urls = {
            'invoice': f'https://al-afaq20.daftra.com/owner/reports/revenue.csv?report_type=invoice&date_from={date_from_encoded}&date_to={date_to_encoded}&group_by={period}',
            'profit': f'https://al-afaq20.daftra.com/owner/reports/stock_transactions_profit.csv?group_by={period}&is_summary=0&report_type=stock_transaction&type=stock_transaction&date_from={date_from_encoded}&date_to={date_to_encoded}'
        }

        # Download paths for 'invoice' and 'profit' reports
        download_paths = {
            'invoice': {
                'daily': os.getenv('DAILY_INVOICES_PATH'),
                'monthly': os.getenv('MONTHLY_INVOICES_PATH'),
            },
            'profit': {
                'daily': os.getenv('DAILY_PROFIT_PATH'),
                'monthly': os.getenv('MONTHLY_PROFIT_PATH'),
            }
        }

        # Check if the report type is for 'products_profit' (which may be categorized)
        if report_type == 'products_profit':
            if category:
                # Ensure the category exists
                if category not in category_paths or category not in category_ids:
                    raise ValueError(f"Invalid category: {category}")

                # If category is provided, get the category_id for the category
                category_id = category_ids[category]

                # Construct the URL for the specific category
                url = f'https://al-afaq20.daftra.com/owner/products/products_profit.csv?date_range_from={date_from_encoded}&date_range_to={date_to_encoded}&sort=2&sort_order=desc&category={category_id}'
                
                # Get the download directory for the category based on the period
                download_dir = category_paths[category][period]
            else:
                # If no category is provided, use the general products profit report URL
                url = f'https://al-afaq20.daftra.com/owner/products/products_profit.csv?date_range_from={date_from_encoded}&date_range_to={date_to_encoded}&sort=2&sort_order=desc'

                # Choose a general directory for uncategorized reports
                if period == 'daily':
                    download_dir = os.getenv('DAILY_PRODUCTS_PROFIT')
                else:
                    download_dir = os.getenv('MONTHLY_PRODUCTS_PROFIT')

        # Handle 'invoice' and 'profit' report types
        elif report_type in ['invoice', 'profit']:
            # Construct the URL for the 'invoice' or 'profit' report
            url = report_urls[report_type]

            # Get the appropriate download directory based on report type and period
            download_dir = download_paths[report_type][period]

        else:
            raise ValueError(f"Invalid report type: {report_type}")

        # Download the file (category-specific or general for 'products_profit', or 'invoice'/'profit')
        self._download_file(url, download_dir)
