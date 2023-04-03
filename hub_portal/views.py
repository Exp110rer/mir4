from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from hub_api.models import Order, Composition, Item
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font
import io


# Create your views here.

class OrderBCPListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'hub_portal/orders_bcp.html'
    queryset = Order.objects.filter(status=2, created__gt=datetime.now() - timedelta(days=200))

    def test_func(self):
        return self.request.user.groups.filter(name='Orders_BCP').exists()


class OrderCSListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Order
    template_name = 'hub_portal/orders_cs.html'
    queryset = Order.objects.filter(created__gt=datetime.now() - timedelta(days=200))

    def test_func(self):
        return self.request.user.groups.filter(name='Orders_CS').exists()


class OrderBCPDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    def dispatch(self, request, pk, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        order = Order.objects.get(id=pk)
        wb = openpyxl.Workbook()
        ws = wb.create_sheet('TDSheet', 0)
        if 'Sheet' in wb.sheetnames:
            wb.remove(wb['Sheet'])
        ws.column_dimensions['B'].width = 70
        ws.column_dimensions['C'].width = 35
        items = Item.objects.filter(composition__order=order)
        ws.cell(row=1, column=2, value='gtin')
        ws.cell(row=1, column=3, value='sku')
        for data in enumerate(items, start=2):
            ws.cell(row=data[0], column=2, value=data[1].tuid)
            ws.cell(row=data[0], column=3, value=f"0000000000{data[1].sku}")
        file_obj = io.BytesIO()
        wb.save(file_obj)
        file_name = f'filename="{order.order}.xlsx"'
        return HttpResponse(file_obj.getvalue(), headers={'Content-Type': 'application/vnd.ms-excel',
                                                          'Content-Disposition': f"inline; {file_name}"})

    def test_func(self):
        return self.request.user.groups.filter(name='Orders_BCP').exists()


class OrderCSDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    def dispatch(self, request, pk, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return self.handle_no_permission()
        order = Order.objects.get(id=pk)
        if order.status != 2:
            return self.handle_no_permission()
        items = Item.objects.filter(composition__order=order)
        wb = openpyxl.Workbook()
        ws = wb.create_sheet('')
        if "Sheet" in wb.sheetnames:
            wb.remove(wb['Sheet'])
        values = ['Sold to Party',
                  'PurchaseOrderNumber',
                  'Delivery Date',
                  'Material',
                  'Quantity',
                  'Unit of Measure',
                  'Batch',
                  'Owner']
        for i, value in enumerate(values, start=1):
            ws.cell(row=1, column=i, value=value)
            ws.column_dimensions[chr(i + 64)].width = 20
        compositions = Composition.objects.filter(order=order)
        for i, composition in enumerate(compositions, start=2):
            ws.cell(row=i, column=1, value=order.saleType)
            ws.cell(row=i, column=2, value=order.order)
            ws.cell(row=i, column=3, value=order.buyoutDate)
            # ws.cell(row=i, column=3, value=f"{order.created.year}{order.created.month:02}{order.created.day:02}")
            ws.cell(row=i, column=4, value=composition.sku)
            if order.traceability:
                amount_calculated = len(items.filter(composition=composition, validity=1))
                amount_db = composition.amount
                ws.cell(row=i, column=5, value=amount_calculated)
                if amount_db != amount_calculated:
                    ws.cell(row=i, column=6).font = Font(color='FF0000')
            else:
                ws.cell(row=i, column=5, value=composition.amount)
            ws.cell(row=i, column=6, value=composition.unitOfMeasure)
            ws.cell(row=i, column=7, value="Dummy")
            ws.cell(row=i, column=8, value=order.saleType)

        file_obj = io.BytesIO()
        wb.save(file_obj)
        buyoutDate = str(order.buyoutDate).replace('-','')
        file_name = f'filename="{order.order}_{order.hub.name}_Sales_{order.productCategory}_{buyoutDate}_{order.saleType}_{order.contractType}.xlsx"'
        return HttpResponse(file_obj.getvalue(), headers={'Content-Type': 'application/vnd.ms-excel',
                                                          'Content-Disposition': f"inline; {file_name}"})

    def test_func(self):
        return self.request.user.groups.filter(name='Orders_CS').exists()
