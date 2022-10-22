from django.views.generic import ListView, DetailView
from citation_networks.models import Paper, Author, Authorship
from semantic_scholarship.semantic_scholar import SSPaper
import datetime

class PaperDetailView(DetailView):
    model = Paper

class PaperListView(ListView):
    model = Paper
    queryset = Paper.objects.exclude(citations_last_queried__isnull=True)



def addAuthors(paper_object, JSON_authorlist):
    authors=enumerate(JSON_authorlist)
    for i, author in authors:
        theAuthorObject, created = Author.objects.get_or_create(SS_author_ID=author["authorId"], name=author["name"])
        # zero index because get_or_create returns tuple containing (object, created?)
        numAuthors = len(JSON_authorlist)
        if i == 0:
            Authorship.objects.get_or_create(paper=paper_object,
                                             author=theAuthorObject,
                                             authorPosition="F")

        elif i == numAuthors - 1:
            Authorship.objects.get_or_create(paper=paper_object,
                                             author=theAuthorObject,
                                             authorPosition="L")
        else:
            Authorship.objects.get_or_create(paper=paper_object,
                                             author=theAuthorObject,
                                             authorPosition="I")

def addPaper2DB(ssid):
    paper_response_from_SS_API = SSPaper(ssid)
    thePaperJSON = paper_response_from_SS_API.json
    thePaperObject,created=Paper.objects.get_or_create(
        SSID_paper_ID = thePaperJSON["paperId"],
        title = thePaperJSON["title"],
        journal = thePaperJSON["journal"],
        year = thePaperJSON["year"],
        abstract = thePaperJSON["abstract"])
    addAuthors(thePaperObject, thePaperJSON["authors"])
    for citation in thePaperJSON["citations"]:
         citing_paper,created = Paper.objects.get_or_create(
                                 SSID_paper_ID=citation["paperId"],
                                 title=citation["title"],
                                 journal=citation["journal"],
                                 year=citation["year"])
         addAuthors(citing_paper, citation["authors"])
         thePaperObject.cited_by.add(citing_paper)
         thePaperObject.citations_last_queried=datetime.datetime.now().astimezone()
         thePaperObject.save()
