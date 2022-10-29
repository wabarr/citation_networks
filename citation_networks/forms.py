from django import forms
from django.core.exceptions import ValidationError
import requests
import json
from citation_networks.models import Paper, Author, Authorship
import datetime


def add_authors(paper_object, JSON_authorlist):
    ## given an instance of a Paper object, and a JSON list of authors from the SS API, create Authorship
    authors = enumerate(JSON_authorlist)
    for i, author in authors:
        theAuthorObject, created = Author.objects.get_or_create(SS_author_ID=author["authorId"])
        if created:
            theAuthorObject.name = author["name"]
            theAuthorObject.save()
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

def helper_add_cites_refs(paper_object, JSON_list, citationORreference):
    #given a paper object, a list of citations or references, and a string indicating
    #whether the papers in JSON_list are papers or refereneces, add all the papers to db
    #this is used to avoid having nearly identifical code blocks for adding refs and cites
    for work in JSON_list:
        ## if no paperId try based on title
        if not work["paperId"]:
            potentially_new_paper, created = Paper.objects.get_or_create(title=work["title"])
        else:
            potentially_new_paper, created = Paper.objects.get_or_create(SSID_paper_ID=work["paperId"])
        if created:
            potentially_new_paper.title = work["title"]
            try:
                potentially_new_paper.journal_name = work["journal"]["name"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                potentially_new_paper.volume = work["journal"]["volume"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                potentially_new_paper.issue = work["journal"]["issue"]
            except KeyError:
                pass
            except TypeError:
                pass
            try:
                potentially_new_paper.pages = work["journal"]["pages"]
            except KeyError:
                pass
            except TypeError:
                pass
            potentially_new_paper.year = work["year"]
            potentially_new_paper.save()
            add_authors(potentially_new_paper, work["authors"])

        if citationORreference == "citation":
            paper_object.cited_by.add(potentially_new_paper)
            paper_object.save()

        if citationORreference == "reference":
            paper_object.references.add(potentially_new_paper)
            paper_object.save()

        paper_object.citations_last_queried = datetime.datetime.now().astimezone()

class ImportCitations(forms.Form):
    ssid = forms.CharField(help_text="Enter Semantic Scholar ID")

    def addCitationsRefs(self, id):
        thePaperObject = Paper.objects.get(SSID_paper_ID=id)
        thePaperJSON = json.loads(thePaperObject.raw_SS_json)
        
        helper_add_cites_refs(thePaperObject, thePaperJSON["citations"], "citation")

        helper_add_cites_refs(thePaperObject, thePaperJSON["references"], "reference")

    def clean(self):
        super().clean()
        ## on submit form clean, query SS and create the object if needed, saving the
        ## raw json into a model field called Paper.raw_SS_json
        id = self.cleaned_data["ssid"]
        semantic_API_url = "https://api.semanticscholar.org/graph/v1/paper/"
        #status_code = None
        fields = ["citationCount", "authors", "year", "title", "journal", "publicationTypes", "abstract",
                  "citations", "citations.authors", "citations.year", "citations.title",
                  "citations.journal",
                  "references", "referenceCount", "references.authors", "references.year", "references.title",
                  "references.journal"]
        URL = semantic_API_url + id + "?fields={fields}".format(
            fields=",".join(fields))
        print(URL)
        try:
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
        thePaperObject.save()
        add_authors(thePaperObject, thePaperJSON["authors"])
