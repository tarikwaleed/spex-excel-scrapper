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

    

    def get_report(self, report_type: str, period: str):
        """
        Args:
            report_type (str):  ("invoice", "profit", "products_profit").
            period (str): ("daily", "monthly").
        """
        download_paths = {
            'invoice': {
                'daily': os.getenv('DAILY_INVOICES_PATH'),
                'monthly': os.getenv('MONTHLY_INVOICES_PATH'),
            },
            'profit': {
                'daily': os.getenv('DAILY_PROFIT_PATH'),
                'monthly': os.getenv('MONTHLY_PROFIT_PATH'),
            },
            'products_profit': {
                'daily': os.getenv('DAILY_PRODUCTS_PROFIT'),
                'monthly': os.getenv('MONTHLY_PRODUCTS_PROFIT'),
            },
            'clients_sales': {
                'daily': os.getenv('CLIENTS_SALES_PATH_DAILY'),
                'monthly': os.getenv('CLIENTS_SALES_PATH_MONTHLY'),
            }
        }

        if period == 'daily':
            date_to = (datetime.today()).strftime('%d/%m/%Y')
            date_from = date_to
        else:
            date_to = datetime.today().strftime('%d/%m/%Y')
            date_from = datetime.today().replace(day=1).strftime('%d/%m/%Y')

        date_from_encoded = urllib.parse.quote(date_from)
        date_to_encoded = urllib.parse.quote(date_to)

        report_urls = {
            'invoice': f'https://al-afaq20.daftra.com/owner/reports/revenue.csv?report_type=invoice&date_from={date_from_encoded}&date_to={date_to_encoded}&group_by={period}',
            # تقارير البرح حسب الفترة
            'profit': f'https://al-afaq20.daftra.com/owner/reports/stock_transactions_profit.csv?group_by={period}&is_summary=0&report_type=stock_transaction&type=stock_transaction&date_from={date_from_encoded}&date_to={date_to_encoded}',
            'products_profit': f'https://al-afaq20.daftra.com/owner/products/products_profit.csv?date_range_from={date_from_encoded}&date_range_to={date_to_encoded}&sort=2&sort_order=desc',
            #ارباح مبيعات الاصناف- العميل
            'clients_sales': f'https://al-afaq20.daftra.com/owner/products/products_profit.csv?&date_range_from={date_from_encoded}&date_range_to={date_to_encoded}&type=client&sort=2&sort_order=desc'
        }

        download_dir = download_paths[report_type][period]
        url = report_urls[report_type]

        self._download_file(url, download_dir)
