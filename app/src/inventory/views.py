
import csv
from rest_framework.views import APIView
from rest_framework.response import Response

class InventoryStatusView(APIView):
    def get(self, request, *args, **kwargs):
        csv_file_path = '/home/tarik/repos/excel-scrapper/app/resources/generated/low_inventory/.com.google.Chrome.9g5tvE'
        filter_type = request.GET.get('filter', 'all')

        inventory_status = []

        with open(csv_file_path, encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)

            for row in csv_reader:
                quantity_str = row[5]
                quantity = int(quantity_str)
                if filter_type == 'minus' and quantity is not None and quantity < 0:
                    inventory_status.append({
                        "code": row[0],
                        "name": row[1],
                        "barcode": row[2],
                        "category": row[3],
                        "brand": row[4],
                        "quantity": quantity
                    })
                elif filter_type == 'zero' and quantity == 0:
                    inventory_status.append({
                        "code": row[0],
                        "name": row[1],
                        "barcode": row[2],
                        "category": row[3],
                        "brand": row[4],
                        "quantity": quantity
                    })
                elif filter_type == 'zero-or-minus' and (quantity is None or quantity <= 0):
                    inventory_status.append({
                        "code": row[0],
                        "name": row[1],
                        "barcode": row[2],
                        "category": row[3],
                        "brand": row[4],
                        "quantity": quantity
                    })
                elif filter_type == 'all':
                    inventory_status.append({
                        "code": row[0],
                        "name": row[1],
                        "barcode": row[2],
                        "category": row[3],
                        "brand": row[4],
                        "quantity": quantity
                    })

        return Response(inventory_status)


class InventoryBarChartView(APIView):
    def get(self, request, *args, **kwargs):
        csv_file_path = '/home/tarik/repos/excel-scrapper/app/resources/generated/low_inventory/.com.google.Chrome.9g5tvE'
        
        counts = {
            "zeroQuantity": 0,
            "minusQuantity": 0,
            "lessThanTenQuantity": 0
        }

        with open(csv_file_path, encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  # Skip header
            next(csv_reader)  # Skip subheader

            for row in csv_reader:
                quantity_str = row[5]
                try:
                    quantity = int(quantity_str.replace('.', '').replace('ر', '').replace('س', '').replace('\xa0', '').replace(',', ''))
                except ValueError:
                    quantity = None
                
                if quantity == 0:
                    counts["zeroQuantity"] += 1
                if quantity is not None and quantity < 0:
                    counts["minusQuantity"] += 1
                if quantity is not None and quantity < 10:
                    counts["lessThanTenQuantity"] += 1
        
        data = [
            {
                "id": "zeroQuantity",
                "value": counts["zeroQuantity"],
                "label": "كمية المنتج تساوي 0"
            },
            {
                "id": "minusQuantity",
                "value": counts["minusQuantity"],
                "label": "كمية النتج اقل من صفر"
            },
            {
                "id": "lessThanTenQuantity",
                "value": counts["lessThanTenQuantity"],
                "label": "كمية المنتج اقل من 10"
            }
        ]

        return Response(data)
