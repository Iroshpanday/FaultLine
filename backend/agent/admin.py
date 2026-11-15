from django.contrib import admin

from .models import AgentRun, LLMCall

# These rows are an audit trail of what the agent did and what it cost.
# The admin is for looking, not editing: everything is read-only.


class LLMCallInline(admin.TabularInline):
    model = LLMCall
    extra = 0
    can_delete = False
    ordering = ["attempt_number"]
    fields = [
        "attempt_number",
        "model",
        "status",
        "error_category",
        "latency_ms",
        "input_tokens",
        "output_tokens",
        "cost",
        "cost_source",
    ]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ["id", "store", "status", "steps", "created_at", "finished_at"]
    list_filter = ["status", "store"]
    search_fields = ["id", "idempotency_key"]
    inlines = [LLMCallInline]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(LLMCall)
class LLMCallAdmin(admin.ModelAdmin):
    list_display = [
        "agent_run",
        "attempt_number",
        "model",
        "status",
        "error_category",
        "latency_ms",
        "cost",
        "created_at",
    ]
    list_filter = ["status", "error_category", "provider", "model"]
    search_fields = ["agent_run__id", "provider_request_id"]

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False
