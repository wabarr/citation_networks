from django.contrib import admin
from citation_networks.models import Paper, Authorship, Author


class PaperAdmin(admin.ModelAdmin):
    fields = ["SSID_paper_ID", "title", "year", "abstract", "journal", "cited_by", "citations_last_queried"]
    search_fields = ["SSID_paper_ID", "title", "year","authors__name"]

admin.site.register(Paper, PaperAdmin)
admin.site.register(Authorship)
admin.site.register(Author)
