from django import forms
import requests
from citation_networks.models import Paper, Author, Authorship
import datetime

class ImportCitations(forms.Form):
    multipleIDstring = forms.CharField(widget=forms.Textarea, help_text="Enter one or more Semantic Scholar paper IDs, separated by commas")

    def doImport(self, multipleIDstring):
        class SSPaper:
            def __init__(self, ID):
                self.ID = ID
                self.semantic_API_url = "https://api.semanticscholar.org/graph/v1/paper/"
                try:
                    fields = ["citationCount", "authors", "year", "title", "journal", "publicationTypes", "abstract",
                              "citations", "citations.authors", "citations.year", "citations.title",
                              "citations.journal",
                              "references", "references.authors", "references.year", "references.title",
                              "references.journal"]
                    URL = self.semantic_API_url + self.ID + "?fields={fields}".format(
                        fields=",".join(fields))
                    print(URL)
                    paper = requests.get(URL)
                    if paper.status_code == 404:
                        raise Exception(paper.json()["error"])
                    if paper.status_code == 200:
                        self.json = paper.json()
                except:
                    raise Exception(
                        "something dreadful happened when trying to fetch paper {id}.  Check your URL".format(
                            id=self.ID))

            def json(self):
                print(self.json)

        def addAuthors(paper_object, JSON_authorlist):
            authors = enumerate(JSON_authorlist)
            for i, author in authors:
                theAuthorObject, created = Author.objects.get_or_create(SS_author_ID=author["authorId"],
                                                                        name=author["name"])
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

        def addPaper2DB(ID):
            paper_response_from_SS_API = SSPaper(ID)
            thePaperJSON = paper_response_from_SS_API.json
            thePaperObject, created = Paper.objects.get_or_create(SSID_paper_ID=thePaperJSON["paperId"])
            thePaperObject.title=thePaperJSON["title"]
            thePaperObject.journal=thePaperJSON["journal"]
            thePaperObject.year=thePaperJSON["year"]
            thePaperObject.save()
            addAuthors(thePaperObject, thePaperJSON["authors"])
            for citation in thePaperJSON["citations"]:
                citing_paper, created = Paper.objects.get_or_create(SSID_paper_ID=citation["paperId"])
                citing_paper.title=citation["title"]
                citing_paper.journal=citation["journal"]
                citing_paper.year=citation["year"]
                citing_paper.save()
                addAuthors(citing_paper, citation["authors"])
                thePaperObject.cited_by.add(citing_paper)
                thePaperObject.citations_last_queried = datetime.datetime.now().astimezone()
                thePaperObject.save()
            for reference in thePaperJSON["references"]:
                referring_paper, created = Paper.objects.get_or_create(SSID_paper_ID=reference["paperId"])
                referring_paper.title=reference["title"]
                referring_paper.journal=reference["journal"]
                referring_paper.year=reference["year"]
                referring_paper.save()
                addAuthors(referring_paper, reference["authors"])
                thePaperObject.references.add(referring_paper)
                thePaperObject.save()
        for SSid in multipleIDstring.split(','):
            addPaper2DB(SSid)
