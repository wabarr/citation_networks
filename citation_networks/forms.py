from django import forms
from django.core.exceptions import ValidationError
import requests
import json
from citation_networks.models import Paper, Author, Authorship
import datetime

class ImportCitations(forms.Form):
    ssid = forms.CharField(help_text="Enter Semantic Scholar ID")

    def addAuthors(self, paper_object, JSON_authorlist):
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

    def addCitationsRefs(self, id):
        thePaperObject = Paper.objects.get(SSID_paper_ID=id)
        thePaperJSON = json.loads(thePaperObject.raw_SS_json)
        for citation in thePaperJSON["citations"]:
            citing_paper, created = Paper.objects.get_or_create(SSID_paper_ID=citation["paperId"])
            citing_paper.title = citation["title"]
            try:
                citing_paper.journal_name = citation["journal"]["name"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                citing_paper.volume = citation["journal"]["volume"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                citing_paper.issue = citation["journal"]["issue"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                citing_paper.pages = citation["journal"]["pages"]
            except KeyError:
                pass
            except TypeError:
                pass
            citing_paper.year = citation["year"]
            citing_paper.save()
            self.addAuthors(citing_paper, citation["authors"])
            thePaperObject.cited_by.add(citing_paper)
            thePaperObject.save()
        for reference in thePaperJSON["references"]:
            referring_paper, created = Paper.objects.get_or_create(SSID_paper_ID=reference["paperId"])
            referring_paper.title = reference["title"]
            try:
                referring_paper.journal_name = reference["journal"]["name"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                referring_paper.volume = reference["journal"]["volume"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                referring_paper.issue = reference["journal"]["issue"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                referring_paper.pages = reference["journal"]["pages"]
            except KeyError:
                pass
            except TypeError:
                pass
            referring_paper.year = reference["year"]
            referring_paper.save()
            self.addAuthors(referring_paper, reference["authors"])
            thePaperObject.references.add(referring_paper)
            thePaperObject.save()

    def clean(self):
        super().clean()
        ## on submit form clean, query SS and create the object if needed, saving the
        ## raw json into a model field called Paper.raw_SS_json
        id = self.cleaned_data["ssid"]
        semantic_API_url = "https://api.semanticscholar.org/graph/v1/paper/"
        status_code = None
        try:
            fields = ["citationCount", "authors", "year", "title", "journal", "publicationTypes", "abstract",
                      "citations", "citations.authors", "citations.year", "citations.title",
                      "citations.journal",
                      "references", "referenceCount", "references.authors", "references.year", "references.title", "references.journal"]
            URL = semantic_API_url + id + "?fields={fields}".format(
                fields=",".join(fields))
            print(URL)
            paper = requests.get(URL)
            if paper.status_code == 200:
                thePaperJSON = paper.json()
            else:
                raise ValidationError("Got error code {code} from Semantic Scholar".format(code=paper_response_from_SS_API.status_code))
        except:
            raise ValidationError(
                "something dreadful happened when trying to fetch paper.  Check your URL {url}".format(
                    url=URL))

        ## if we want to be able to handle papers with more than 1000 citations or references
        ## need to add in multiple calls to API, because they limit the number returned to 1000
        if thePaperJSON["referenceCount"] > 1000:
            raise ValidationError("I don't know how to import a paper with more than 1000 references. Not imported.")
        if thePaperJSON["citationCount"] > 1000:
            raise ValidationError("I don't know how to import a paper with more than 1000 citations. Not imported.")



        thePaperObject, created = Paper.objects.get_or_create(SSID_paper_ID=thePaperJSON["paperId"])
        thePaperObject.raw_SS_json = json.dumps(thePaperJSON)
        thePaperObject.title = thePaperJSON["title"]
        try:
            thePaperObject.journal_name = thePaperJSON["journal"]["name"]
        except KeyError:
            pass
        except TypeError:
            raise ValidationError("Got a type error when trying to parse the JSON")
        try:
            thePaperObject.volume = thePaperJSON["journal"]["volume"]
        except KeyError:
            pass
        except TypeError:
            raise ValidationError("Got a type error when trying to parse the JSON")
        try:
            thePaperObject.issue = thePaperJSON["journal"]["issue"]
        except KeyError:
            pass
        except TypeError:
            raise ValidationError("Got a type error when trying to parse the JSON")
        try:
            thePaperObject.pages = thePaperJSON["journal"]["pages"]
        except KeyError:
            pass
        except TypeError:
            raise ValidationError("Got a type error when trying to parse the JSON")
        thePaperObject.year = thePaperJSON["year"]
        thePaperObject.citations_last_queried = datetime.datetime.now().astimezone()
        thePaperObject.save()
        self.addAuthors(thePaperObject, thePaperJSON["authors"])
