from django.contrib import admin

from .models import Refund


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    # Refunds are money records: look, don't edit.
    list_display = ["order", "amount", "currency", "status", "provider_ref", "created_at"]
    list_filter = ["status", "store"]
    search_fields = ["order__number", "provider_ref"]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False
