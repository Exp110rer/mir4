from django.views.generic import ListView, DetailView
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from hub_api.models import Order, Composition, Item, ProductCategory
from mirusers.models import Hub
from datetime import datetime, timedelta, date
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

    # queryset = Order.objects.filter(buyoutDate__gte=datetime.now(), buyoutDate__lt=datetime.now() + timedelta(days=7))

    def test_func(self):
        return self.request.user.groups.filter(name='Orders_CS').exists() or self.request.user.groups.filter(
            name='Orders_BCP').exists()

    def get_context_data(self, *, object_list=None, **kwargs):
        filter_date = self.request.GET.get('filter_date', None)
        filter_productCategory = self.request.GET.get('filter_productCategory', 'ALL')
        filter_hub = self.request.GET.get('filter_hub', 'ALL')
        context = super().get_context_data()
        if self.request.user.groups.filter(name='Orders_CS').exists():
            context['user_group'] = 'CS'
        elif self.request.user.groups.filter(name='Orders_BCP').exists():
            context['user_group'] = 'BCP'
        else:
            context['user_group'] = 'NA'
        context['product_categories'] = ProductCategory.objects.all()
        context['hubs'] = Hub.objects.filter(id__gt=1)
        context['filter_date'] = filter_date
        context['filter_productCategory'] = filter_productCategory
        context['filter_hub'] = filter_hub
        return context

    def dispatch(self, request, *args, **kwargs):
        f_date = request.GET.get('filter_date', None)
        filter_date = datetime.strptime(f_date, "%Y-%m-%d") if f_date else None
        filter_productCategory = request.GET.get('filter_productCategory', 'ALL')
        filter_hub = request.GET.get('filter_hub', 'ALL')
        filter_query = dict()
        if filter_date:
            filter_query['buyoutDate'] = filter_date
        else:
            filter_query['buyoutDate__gte'] = datetime.now()
            filter_query['buyoutDate__lt'] = datetime.now() + timedelta(days=14)
        if filter_productCategory != 'ALL':
            filter_query['productCategory'] = filter_productCategory
        if filter_hub != 'ALL':
            filter_query['hub__name'] = filter_hub
        print("Filter query", filter_query)
        self.queryset = Order.objects.filter(**filter_query).order_by('buyoutDate')
        return super().dispatch(request)


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
        items = Item.objects.filter(composition__order=order, validity=1)
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
        wb = openpyxl.Workbook()
        ws = wb.create_sheet('')
        if "Sheet" in wb.sheetnames:
            wb.remove(wb['Sheet'])
        values = ['PurchaseOrderNumber',
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
        i = 2
        for composition in compositions:
            composition_items = Item.objects.filter(composition=composition)
            composition_batches = set([item.batch for item in composition_items])
            if not composition_batches: composition_batches = {None}
            for composition_batch in composition_batches:
                ws.cell(row=i, column=1, value=order.order)
                ws.cell(row=i, column=2, value=order.buyoutDate)
                ws.cell(row=i, column=3, value=composition.sku)
                if order.traceability:
                    initial_amount = len(composition_items.filter(batch=composition_batch))
                    validated_amount = len(composition_items.filter(batch=composition_batch, validity=1))
                    ws.cell(row=i, column=4, value=validated_amount)
                    if initial_amount != validated_amount:
                        ws.cell(row=i, column=4).font = Font(color='FF0000')
                else:
                    ws.cell(row=i, column=4, value=composition.amount)
                if composition.unitOfMeasure == 'case':
                    ws.cell(row=i, column=5, value='CS')
                elif composition.unitOfMeasure == 'out':
                    ws.cell(row=i, column=5, value='OUT')
                else:
                    ws.cell(row=i, column=5, value='Unknown')
                ws.cell(row=i, column=6, value=composition_batch)
                ws.cell(row=i, column=7, value=order.saleType)
                i += 1
        file_obj = io.BytesIO()
        wb.save(file_obj)
        buyoutDate = str(order.buyoutDate).replace('-', '')
        if order.contractType == 't':
            file_contact_type = 's'
        elif order.contractType == 'c':
            file_contact_type = 'k'
        file_name = f'filename="{order.order}_{order.hub.name}_Sales_{order.productCategory}_{buyoutDate}_{order.saleType}_{file_contact_type}.xlsx"'
        order.downloadedBy_id = request.user.id
        order.save()
        return HttpResponse(file_obj.getvalue(), headers={'Content-Type': 'application/vnd.ms-excel',
                                                          'Content-Disposition': f"inline; {file_name}"})

    def test_func(self):
        return self.request.user.groups.filter(name='Orders_CS').exists()
