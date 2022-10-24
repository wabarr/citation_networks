from django.contrib import admin
from citation_networks.models import Paper, Authorship, Author


class PaperAdmin(admin.ModelAdmin):
    fields = ["SSID_paper_ID", "title", "year", "abstract", "journal", "cited_by", "citations_last_queried"]
    search_fields = ["SSID_paper_ID", "title", "year","authors__name"]

class AuthorAdmin(admin.ModelAdmin):
    fields=["name", "SS_author_ID"]
    search_fields = ["SS_author_ID", "name"]

class AuthorshipAdmin(admin.ModelAdmin):
    search_fields = ["author__name"]

admin.site.register(Paper, PaperAdmin)
admin.site.register(Authorship)
admin.site.register(Author, AuthorAdmin)
