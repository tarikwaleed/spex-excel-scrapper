import csv
import random
from rest_framework.utils.formatting import remove_trailing_string
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from rest_framework import status
from sales.serializers import DailySalesStatsSerializer,TopClientsSerializer
import requests
from collections import defaultdict
from datetime import datetime


class SalesStatsView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the period from query params, default to 'daily'
        period = request.query_params.get('period', 'daily')

        if period == 'monthly':
            invoices_path = os.getenv('MONTHLY_INVOICES_PATH')
            profit_path = os.getenv('MONTHLY_PROFIT_PATH')
        else:  # default to daily
            invoices_path = os.getenv('DAILY_INVOICES_PATH')
            profit_path = os.getenv('DAILY_PROFIT_PATH')

        invoice_count = total_revenue = average_revenue = 0.0

        # Check if invoices directory exists
        if os.path.exists(invoices_path):
            files = os.listdir(invoices_path)
            csv_file_name = next((f for f in files if f.startswith('.com')), None)

            if csv_file_name:
                csv_file_path = os.path.join(invoices_path, csv_file_name)

                # Check if the file is not empty
                if os.path.getsize(csv_file_path) > 0:
                    with open(csv_file_path, encoding='utf-8') as csvfile:
                        all_rows = list(csv.reader(csvfile))

                        # Ensure there are enough rows to process
                        if len(all_rows) > 5:
                            relevant_rows = all_rows[3:-3]
                            invoice_count = len(relevant_rows)

                            # Clean and parse total revenue from the last row
                            total_revenue_str = all_rows[-1][3] if period=="daily" else all_rows[-1][4]
                            # return Response(total_revenue_str)
                            total_revenue_cleaned = total_revenue_str.replace('ر', '').replace('س', '').replace('\xa0', '').replace('\u2060', '').replace(',', '').strip()
                            total_revenue = float(total_revenue_cleaned)

                            # Calculate the average revenue
                            average_revenue =round(total_revenue / invoice_count,2) if invoice_count > 0 else 0.0

        total_profit = 0.0

        # Check if profit directory exists
        if os.path.exists(profit_path):
            files = os.listdir(profit_path)
            csv_file_name = next((f for f in files if f.startswith('.com')), None)

            if csv_file_name:
                csv_file_path = os.path.join(profit_path, csv_file_name)

                # Check if the file is not empty
                if os.path.getsize(csv_file_path) > 0:
                    with open(csv_file_path, encoding='utf-8') as csvfile:
                        all_rows = list(csv.reader(csvfile))

                        # Ensure there are enough rows to process
                        if len(all_rows) > 1:
                            # Clean and parse total profit from the last row
                            total_profit_str = all_rows[-1][-1]
                            total_profit_cleaned = total_profit_str.replace('ر', '').replace('س', '').replace('\xa0', '').replace('\u2060', '').replace(',', '').strip()
                            total_profit = float(total_profit_cleaned)

        # Calculate revenue to profit percentage
        if total_revenue > 0:
            revenue_to_profit_percentage = round((total_profit / total_revenue) * 100, 1)
        else:
            revenue_to_profit_percentage = 0.0

        # Serialize and return the data
        serializer = DailySalesStatsSerializer({
            'invoice_count': invoice_count,
            'total_revenue': total_revenue,
            'average_revenue': average_revenue,
            'total_profit': total_profit,
            'revenue_to_profit_percentage': revenue_to_profit_percentage
        })

        return Response(serializer.data, status=status.HTTP_200_OK)


class TopClientsView(APIView):
    def get(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'daily')
        
        clients_path_key = f'CLIENTS_SALES_PATH_{period.upper()}'  # Fetch correct path based on period
        clients_path = os.getenv(clients_path_key)

        if not clients_path:
            return Response({"error": "Invalid period or path not configured"}, status=status.HTTP_400_BAD_REQUEST)
        
        clients = []
        
        if os.path.exists(clients_path):
            files = os.listdir(clients_path)
            csv_file_name = next((f for f in files if f.startswith('.com')), None)
            
            if csv_file_name:
                csv_file_path = os.path.join(clients_path, csv_file_name)
                
                if os.path.getsize(csv_file_path) > 0:  
                    with open(csv_file_path, encoding='utf-8') as csvfile:
                        csv_reader = csv.reader(csvfile)
                        all_rows = list(csv_reader)
                        relevant_rows = all_rows[2:-1]  # Skip headers and last row
                        
                        for row in relevant_rows:
                            client_name = row[0]
                            try:
                                total_value = float(row[2].replace('ر⁠.س', '').replace(',', ''))
                            except ValueError:
                                continue  # Skip rows with invalid data
                            
                            clients.append({
                                "id": client_name,
                                "label": client_name,
                                "value": total_value
                            })
                    
                    top_clients = sorted(clients, key=lambda x: x["value"], reverse=True)[:5]

                    serializer = TopClientsSerializer(top_clients, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "No valid CSV file found"}, status=status.HTTP_404_NOT_FOUND)


class TopProductsView(APIView):
    def get(self, request, *args, **kwargs):
        period = request.GET.get('period', 'daily')
        filter_type = request.GET.get('filter', 'top')  # Default to 'top' if no filter is provided

        if period == 'monthly':
            products_profit_path = os.getenv('MONTHLY_PRODUCTS_PROFIT')
        else:  
            products_profit_path = os.getenv('DAILY_PRODUCTS_PROFIT')

        files = os.listdir(products_profit_path)
        csv_file_name = next((f for f in files if f.startswith('.com')), None)

        if csv_file_name:
            csv_file_path = os.path.join(products_profit_path, csv_file_name)

            products = []

            with open(csv_file_path, encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile)
                all_rows = list(csv_reader)
                relevant_rows=all_rows[2:-1]

                arr=[]
                for row in relevant_rows:
                    product_name = row[0]
                    
                    # Clean up the sales value string
                    cleaned_sales_value = (row[2]
                                           .replace('ر', '')   # Remove currency symbols or other characters
                                           .replace('س', '')
                                           .replace('\xa0', '')
                                           .replace('\u2060', '')
                                           .replace(',', '')   # Remove comma (thousands separator)
                                           ).split('.')[0]


                    sales_value = int(float(cleaned_sales_value))
                    products.append({
                            "id": product_name,
                            "label": product_name,
                            "value": sales_value,
                            "color": f"hsl({random.randint(0, 360)}, 70%, 50%)"
                    })


            # Sort the products based on the filter and return the top or lowest results
            if filter_type == 'lowest':
                sorted_products = sorted(products, key=lambda x: x["value"])[:5]
            else:  # Default to top products
                sorted_products = sorted(products, key=lambda x: x["value"], reverse=True)[:5]

            return Response(sorted_products)

        # return Response({"error": "No valid CSV file found."}, status=404)


class InvoicesTrendView(APIView):
    def get(self, request, *args, **kwargs):
        daftra_api_key = os.getenv("DAFTRA_API_KEY")
        url = f'{os.getenv("DAFTRA_API_BASE_URL")}/invoices?'

        headers = {
            "APIKEY": daftra_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        period = request.query_params.get('period', 'daily')  # Default to 'daily'
        try:
            response = requests.get(url, headers=headers)
            invoices = response.json().get('data')
            
            if period == 'monthly':
                days_count = defaultdict(int)
                today = datetime.today().date()
                
                for invoice_data in invoices:
                    created_date = invoice_data.get('Invoice', {}).get('created')
                    
                    created_time = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
                    if created_time.year == today.year and created_time.month == today.month:
                        day = created_time.day
                        days_count[day] += 1
                
                result = [{"x": day, "y": count} for day, count in sorted(days_count.items())]
                
            else:  # Default to 'daily'
                hours_count = defaultdict(int)
                today = datetime.today().date()
                
                for invoice_data in invoices:
                    created_date = invoice_data.get('Invoice', {}).get('created')
                    
                    created_time = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
                    if created_time.date() == today:
                        hour = created_time.hour
                        hours_count[hour] += 1
                
                result = [{"x": hour, "y": count} for hour, count in sorted(hours_count.items())]
            
            return Response(result)
        except Exception as e:
            raise e
