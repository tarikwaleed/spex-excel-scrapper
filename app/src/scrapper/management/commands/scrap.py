from django.core.management.base import BaseCommand
import logging
import inspect
import time
from shared.models import CommandException
from scrapper.utils import Scrapper

class Command(BaseCommand):

    def handle(self, *args, **options):
        exception_count = 0
        start_time = time.time()

        logger = logging.getLogger(__name__)
        exceptions_logger = logging.getLogger("exceptions")

        logger.info(
            "----------------------------------------------------------------------------------------------------------------------------------------------------"
        )

        current_function_name = inspect.currentframe().f_code.co_name

        try:
            scraper = Scrapper(headless=True)
            
            # Define the report tasks for each category and period
            tasks = [
                # Invoices and Profit reports
                ('invoice', 'daily'),
                ('profit', 'daily'),
                ('invoice', 'monthly'),
                ('profit', 'monthly'),

                # Products Profit reports for each category
                ('products_profit', 'daily', 'SUN'),
                ('products_profit', 'monthly', 'SUN'),
                ('products_profit', 'daily', 'OPTICAL'),
                ('products_profit', 'monthly', 'OPTICAL'),
                ('products_profit', 'daily', 'CHAIN'),
                ('products_profit', 'monthly', 'CHAIN'),
                ('products_profit', 'daily', 'Single Vision'),
                ('products_profit', 'monthly', 'Single Vision'),
                ('products_profit', 'daily', 'single vision tra'),
                ('products_profit', 'monthly', 'single vision tra'),
                ('products_profit', 'daily', 'progressive'),
                ('products_profit', 'monthly', 'progressive'),
                ('products_profit', 'daily', 'CLEAR CONTACT LENS'),
                ('products_profit', 'monthly', 'CLEAR CONTACT LENS'),
                ('products_profit', 'daily', 'COLOR CONTACT LENS'),
                ('products_profit', 'monthly', 'COLOR CONTACT LENS'),
                ('products_profit', 'daily', 'DIVEL SINGLE VISION'),
                ('products_profit', 'monthly', 'DIVEL SINGLE VISION'),
                ('products_profit', 'daily', 'RODEN STOCK PROGRESSIVE'),
                ('products_profit', 'monthly', 'RODEN STOCK PROGRESSIVE'),
                ('products_profit', 'daily', 'RODENSTOCK SINGLE'),
                ('products_profit', 'monthly', 'RODENSTOCK SINGLE'),

                # Clients Sales reports
                # ('clients_sales', 'daily'),
                # ('clients_sales', 'monthly'),
            ]

            def run_scraper(report_type, period, category=None):
                try:
                    if category:
                        scraper.get_report(report_type, period, category=category)
                    else:
                        scraper.get_report(report_type, period)
                except Exception as e:
                    nonlocal exception_count
                    exception_count += 1
                    exceptions_logger.error(
                        f"Exception happened in Package:{__package__} "
                        f"Module:{__name__} Function:{current_function_name}() "
                        f"While processing {report_type} - {period} - {category or 'No Category'}: {e}"
                    )

            # Run the scraping tasks sequentially in a loop
            for task in tasks:
                report_type, period, *category = task
                run_scraper(report_type, period, *category)

        except Exception as e:
            exception_count += 1
            exceptions_logger.error(
                f"Exception happened in Package:{__package__} Module:{__name__} Function:{current_function_name}(): {e}"
            )

        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Synced in {duration:.2f} seconds")

        if exception_count > 0:
            self.stdout.write(
                self.style.ERROR(
                    f"Synced with {exception_count} exceptions in {duration:.2f} seconds"
                )
            )
            command_exception = CommandException(
                command=__name__, count=exception_count
            )
            command_exception.save()
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Synced without exception in {duration:.2f} seconds"
                )
            )
