from django.contrib.admin import ModelAdmin
from django.db.models import ForeignKey, OneToOneField, ManyToManyField
from mptt.fields import TreeForeignKey


class CustomBaseModelAdmin(ModelAdmin):
    def __init__(self, model, admin_site):
        self.autocomplete_fields = [field.name for field in model._meta.fields
                                    if type(field) in [ForeignKey, OneToOneField, ManyToManyField, TreeForeignKey]]
        # self.raw_id_fields = [field.name for field in model._meta.fields
        #                       if type(field) in [ForeignKey, OneToOneField, ManyToManyField]]
        # self.list_display = [field.name for field in self.model._meta.fields
        #                      if type(field) != ManyToManyField and field.name not in ['updated_by', 'updated_at']]
        super().__init__(model, admin_site)

    def display_all_list(self):
        self.list_display = [field.name for field in self.model._meta.fields if type(field) != ManyToManyField]
