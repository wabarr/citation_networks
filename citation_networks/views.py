from django.views.generic import ListView, DetailView, View
from citation_networks.models import Paper, Author
from django.views.generic.edit import FormView
from citation_networks.forms import ImportPaperCitations, ImportAuthor
from django.http import HttpResponseRedirect
from django.http import JsonResponse


class NetworkView(ListView):
    model = Paper
    queryset = Paper.objects.exclude(citations_last_queried__isnull=True).order_by("citations_last_queried").reverse()
    template_name = "citation_networks/network.html"

class NetworkJSONDetail(View):
    def get(self, request, *args, **kwargs):
        paper = Paper.objects.get(pk=self.kwargs["pk"])

        nodeids = []
        nodeids.append(paper.id)

        links = []

        nodecolors = []
        nodecolors.append("#D34E24") #color for central paper

        nodelabels = []
        nodelabels.append(paper.__str__())


        for reference in paper.references.all():
            if reference.id not in nodeids:
                nodeids.append(reference.id)
                nodelabels.append(reference.__str__())
                nodecolors.append("#38726C")
            links.append({"from": paper.id, "to": reference.id})
        for citation in paper.cited_by.all():
            if citation.id not in nodeids:
                nodeids.append(citation.id)
                nodelabels.append(citation.__str__())
                nodecolors.append("#F7F052")
            links.append({"from": citation.id, "to": paper.id})
        nodes = []
        for nid, lab, col in zip(nodeids, nodelabels, nodecolors):
            nodes.append({"id": nid, "title": lab, "color": col})
        return JsonResponse({"nodes": nodes, "links": links})

class NetworkJSON(View):
    def get(self, request, *args, **kwargs):
        QS = Paper.objects.exclude(citations_last_queried__isnull=True).order_by("citations_last_queried").reverse()

        nodeids = []

        nodelabels = []

        nodetitles = []

        nodecolors = []

        links = []

        nodesizes = []

        nodeopacities = []

        for paper in QS:
            ## add queried papers to nodes and format
            nodeids.append(paper.id)
            nodelabels.append(paper.__str__())
            nodetitles.append(paper.__str__())
            nodecolors.append("#D34E24")
            nodeopacities.append(1)
            nodesizes.append(100)

        for paper in QS:
            ## iterate on queryset again and add refs and cites
            for reference in paper.references.all():
                if reference.id not in nodeids:
                    nodeids.append(reference.id)
                    nodelabels.append("")
                    nodetitles.append(reference.__str__())
                    nodecolors.append("#38726C")
                    nodeopacities.append(0.6)
                    nodesizes.append(20)
                links.append({"from": paper.id, "to": reference.id})
            for citation in paper.cited_by.all():
                if citation.id not in nodeids:
                    nodeids.append(citation.id)
                    nodelabels.append("")
                    nodetitles.append(citation.__str__())
                    nodecolors.append("#38726C")
                    nodeopacities.append(0.6)
                    nodesizes.append(20)
                links.append({"from": citation.id, "to": paper.id})
        nodes=[]
        for nid, col, op, size, lab, title in zip(nodeids, nodecolors, nodeopacities, nodesizes, nodelabels, nodetitles):
            nodes.append({"id":nid, "title":title, "color":col, "opacity":op, "size":size, "label":lab})

        return JsonResponse({"nodes": nodes, "links": links})


class AuthorDetailView(DetailView):
    model = Author

class AuthorListView(ListView):
    model = Author
    queryset = Author.objects.all().order_by("name")
    paginate_by = 30

class PaperListView(ListView):
    model = Paper
    queryset = Paper.objects.exclude(citations_last_queried__isnull=True).order_by("citations_last_queried").reverse()
    paginate_by = 30

class ImportPaperFormView(FormView):
    template_name = 'citation_networks/import_paper.html'
    form_class = ImportPaperCitations
    success_url = '/papers/'

    def form_valid(self, form):
        form.addCitationsRefs(form.cleaned_data["ssid"])
        return super().form_valid(form)


class ImportAuthorFormView(FormView):
    template_name = 'citation_networks/import_author.html'
    form_class = ImportAuthor

    def form_valid(self, form):
        ## need to do this to have access to form data in get_success_url
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        auth = Author.objects.get(SS_author_ID=self.form.cleaned_data["ss_author_id"])
        return '/authors/' + str(auth.pk)


class ImportCitationsFormViewFromPaperDetail(ImportPaperFormView):
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
