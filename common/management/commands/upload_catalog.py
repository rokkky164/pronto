import openpyxl                                                                                                                                                                                                                                                            
from openpyxl_image_loader import SheetImageLoader
from django.core.management import BaseCommand

from catalog.models import (
    Category, ProductConfig, Product, ProductVariant, 
    Manufacturer, ProductReview, ProductRatings, ProductImages,
    ShippingAndOrdering
)
from utils.db_interactors import db_create_record
from utils.helpers import get_in_memory_file_upload

file_path = '/home/roshan/Downloads/Catalog Pronto.xlsx'       
wb_obj = openpyxl.load_workbook(file_path)
xl_data = [row for row in wb_obj.active.iter_rows(max_col=37, values_only=True)]
image_loader = SheetImageLoader(wb_obj.active)
# img = image_loader.get('O3')

EXCEL_HEADERS = [
    'Product Name',#X
    'Net Weight',#X
    'Gross weight',
    'Quantity per box',
    'Quantity of items per pallete',
    'Volume',
    'Category Name',
    'Image',#X
    'Description',#X
    'Advance payment(In %)',
    'Shelf life',
    'Packaging details',
    'Grade',
    'Private Label available?',#X
    'Bar code',#X
    'Bar code type',#X
    'Is in stock',
    'Manufacturer Name',#X
    'Brand Name',#X
    'Address',
    'Ingredients',#X
    'Annual Production Size',
    'Quantity Available per Month',
    'Lead Time',
    'Quantity Available Today',
    'Moq',
    'Ltl available',
    'Lead time first shipment',
    'Annual production',
    'Quantity in the box',#X
    'Min no boxes pallet',
    'Max no boxes pallet',
    'Max no of items in 40" container',
    'Payment terms',#X
    'Shipment terms',
    'Shipping modes',
    'Types of pallets used'
]
REQUIRED_EXCEL_HEADERS = [
    'Product Name',#X
    'Net Weight',#X
    'Image',#X
    'Description',#X
    'Private Label available?',#X
    'Bar code',#X
    'Bar code type',#X
    'Manufacturer Name',#X
    'Brand Name',#X
    'Ingredients',#X
    'Quantity in the box',#X
    'Payment terms',#X
]

# logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate catalog module related tables'

    def add_arguments(self, parser):
        # optional arguments
        parser.add_argument(
            '--dry',
            action='append',
            type=str,
        )

    def _validate_sheet(self, xl_data):
        for header in REQUIRED_EXCEL_HEADERS:
            if header not in xl_data[0]:
                    raise Exception(f'header is missing {header}')

        if  len(set(EXCEL_HEADERS).difference(list(set(EXCEL_HEADERS).intersection(set(xl_data[0]))))) > 0:
            error = set(EXCEL_HEADERS).difference(list(set(EXCEL_HEADERS).intersection(set(xl_data[0]))))
            raise Exception(f'Some of excel headers are missing {error}')

    def handle(self, *args, **kwargs):
        # Auto populate catalog database from excel sheet
        headers_data = xl_data[0]
        excel_data = xl_data[4:]
        xl_dict = {}

        for index in range(len(excel_data)):
            xl_dict[f'row_{index}'] = {}
            for idx in range(len(excel_data[index])):
                xl_dict[f'row_{index}'][EXCEL_HEADERS[idx]] = excel_data[index][idx]

        object_creation_errors = []
        img_idx = 0 
        for key in xl_dict.keys():
            product_data = {
                'name': xl_dict[key]['Product Name'],
                'description': xl_dict[key]['Description'],
                'advance_payment': xl_dict[key]['Advance payment(In %)'],
                'shelf_life': xl_dict[key]['Shelf life'],
                'packaging_details': xl_dict[key]['Packaging details'],
                'grade': xl_dict[key]['Grade'],
                'bar_code': xl_dict[key]['Bar code'],
                'bar_code_type': xl_dict[key]['Bar code type'],
                'is_private_label_available': True if xl_dict[key]['Private Label available?'] == 'Yes' else False
            }
            _, product = db_create_record(Product, data=product_data)
            if not isinstance(product, Product):
                raise Exception(f'Error occured while creating entry in Product table {product}')
            image_cols = list(image_loader._images.keys())
            img = image_loader.get(image_cols[img_idx])
            image = get_in_memory_file_upload(img, file_name=f"row_{img_idx}.png", mime_type="image/png", file_format="png")
            image_data = {'image': image, 'product_id': product.id}
            img_idx += 1
            _, product_image = db_create_record(ProductImages, data=image_data)
            product_variant_data = {
                'product_id': product.id,
                'net_weight_per_volume': xl_dict[key]['Net Weight'],
                'gross_weight_per_volume': xl_dict[key]['Gross weight'],
                'quantity_per_carton': xl_dict[key]['Quantity per box'],
                'quantity_of_items_per_pallete': xl_dict[key]['Quantity of items per pallete'],
                'volume': xl_dict[key]['Volume']
            }

            _, product_variant = db_create_record(ProductVariant, data=product_variant_data)
            manufacturer_data = {
                "name": xl_dict[key]['Manufacturer Name'],
                'brand_name': xl_dict[key]['Brand Name'],
                'ingredients': xl_dict[key]['Ingredients'],
                'annual_production_size': xl_dict[key]['Annual Production Size'],
                'quantity_available_per_month': xl_dict[key]['Quantity Available per Month'],
                'lead_time': xl_dict[key]['Lead Time'],
                'quantity_available_today': xl_dict[key]['Quantity Available Today'],
                # 'incoterms': xl_dict[key]['Net Weight'], Ask do we need this?
            }
            if not isinstance(product_variant, ProductVariant):
                raise Exception(f'Error occured while creating entry in ProductVariant table {product_variant}')

            _, manufacturer = db_create_record(Manufacturer, data=manufacturer_data)
            if not isinstance(manufacturer, Manufacturer):
                raise Exception(f'Error occured while creating entry in Manufacturer table {manufacturer}')

            product.manufacturer = manufacturer
            product.save()
            shippingnordering_data = {
                'product_id': product.id,
                'quantity_in_the_box': xl_dict[key]['Quantity in the box'],
                'payment_terms': xl_dict[key]['Payment terms'],
                'moq': xl_dict[key]['Moq'],
                'ltl_available': True if xl_dict[key]['Ltl available'] == 'Yes' else False,
                'lead_time_first_shipment': xl_dict[key]['Lead time first shipment'],
                'annual_production': xl_dict[key]['Annual production'],
                'min_no_boxes_pallet': xl_dict[key]['Min no boxes pallet'],
                'max_no_boxes_pallet': xl_dict[key]['Max no boxes pallet'],
                'max_no_items_in_full_40_inch_container': xl_dict[key]['Max no of items in 40" container'],
                'shipment_terms': xl_dict[key]['Shipment terms'],
                'shipping_modes': xl_dict[key]['Shipping modes'],
                'types_of_pallets_used': xl_dict[key]['Types of pallets used']
            }
            self.stdout.write(self.style.SUCCESS(f"shippingnordering_data :: {shippingnordering_data}"))
            _, sno = db_create_record(ShippingAndOrdering, data=shippingnordering_data)
            if not isinstance(sno, ShippingAndOrdering):
                raise Exception(f'Error occured while creating entry in ShippingAndOrdering table {sno}')
