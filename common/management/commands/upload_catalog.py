import openpyxl                                                                                                                                                                                                                                                            

from openpyxl_image_loader import SheetImageLoader

file_path = '/home/roshan/Downloads/AzNar_Price_List_Georgia_April_2023.xlsx'       

wb_obj = openpyxl.load_workbook(file_path)

xl_data = [row for row in wb_obj.active.iter_rows(max_col=15, values_only=True)]

image_loader = SheetImageLoader(wb_obj.active)

img = image_loader.get('O3')