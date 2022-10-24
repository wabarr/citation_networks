from django.views.generic import ListView, DetailView, TemplateView
from citation_networks.models import Paper, Author
from django.views.generic.edit import FormView
import datetime
from citation_networks.forms import ImportCitations

class PaperDetailView(DetailView):
    model = Paper

class AuthorDetailView(DetailView):
    model = Author

class AuthorListView(ListView):
    model = Author
    queryset = Author.objects.all().order_by("name")

class PaperListView(ListView):
    model = Paper
    queryset = Paper.objects.exclude(citations_last_queried__isnull=True).order_by("citations_last_queried").reverse()

class ImportCitationsFormView(FormView):
    template_name = 'citation_networks/import_citations.html'
    form_class = ImportCitations
    success_url = '/papers/'

    def form_valid(self, form):
        form.doImport(form.cleaned_data["multipleIDstring"])
        return super().form_valid(form)
