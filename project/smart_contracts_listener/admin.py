from django.contrib import admin

from project.smart_contracts_listener.models import TotalDistributionEvent

class TotalDistributionEventAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'transaction_hash', 'log_index')


admin.site.register(TotalDistributionEvent, TotalDistributionEventAdmin)