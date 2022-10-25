from django.views.generic import ListView, DetailView, View
from citation_networks.models import Paper, Author
from django.views.generic.edit import FormView
from citation_networks.forms import ImportCitations
from django.http import HttpResponse
from django.http import JsonResponse


class NetworkView(ListView):
    model = Paper
    queryset = Paper.objects.exclude(citations_last_queried__isnull=True).order_by("citations_last_queried").reverse()
    template_name = "citation_networks/network.html"

class NetworkJSON(View):
    def get(self, request, *args, **kwargs):
        QS = Paper.objects.exclude(citations_last_queried__isnull=True).order_by("citations_last_queried").reverse()
        nodes = []
        links = []
        for paper in QS:
            nodes.append({"id":paper.id, "name":paper.__str__()})
            for reference in paper.references.all():
                nodes.append({"id": reference.id, "name": reference.__str__()})
                links.append({"source": paper.id, "target": reference.id})
            for citation in paper.cited_by.all():
                nodes.append({"id": citation.id, "name": citation.__str__()})
                links.append({"source": citation.id, "target": paper.id})
        return JsonResponse({"nodes": nodes, "links": links})


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
        form.addCitationsRefs(form.cleaned_data["ssid"])
        return super().form_valid(form)

class ImportCitationsFormViewFromPaperDetail(ImportCitationsFormView):
    # note this is more complicated than a standard detail view, because it contains a hidden
    # form to query citations

    template_name = 'citation_networks/paper_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object"] = Paper.objects.get(pk=self.kwargs['pk'])
        return context

    def get_initial(self, **kwargs):
        initial = super().get_initial(**kwargs)
        initial["ssid"] = Paper.objects.get(pk=self.kwargs['pk']).SSID_paper_ID
        return initial