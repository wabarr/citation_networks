from django.db import models

class Author(models.Model):
    SS_author_ID = models.PositiveBigIntegerField(unique=True)
    name = models.CharField(max_length=1000)
    raw_SS_json = models.TextField(null=True, blank=True)
    papers_last_queried = models.DateTimeField(null=True, blank=True)
    exclude_from_analysis = models.BooleanField(null=True, default=False, blank=True)

    def __str__(self):
        try:
            return(self.name)
        except:
            return("error in __str__")

class Paper(models.Model):
    SSID_paper_ID = models.CharField(max_length=1000, unique=True, null=True)
    title = models.CharField(max_length=1000,null=True)
    journal_name = models.CharField(max_length=1000, null=True, blank=True)
    volume = models.CharField(max_length=100, null=True, blank=True)
    issue = models.CharField(max_length=100, null=True, blank=True)
    pages = models.CharField(max_length=100, null=True, blank=True)
    authors = models.ManyToManyField(Author, through='Authorship')
    year = models.IntegerField(null=True)
    abstract = models.TextField(null=True, blank=True)
    references = models.ManyToManyField('Paper', blank=True, related_name="refs")
    cited_by = models.ManyToManyField('Paper', blank=True, related_name="cites")
    citations_last_queried = models.DateTimeField(null=True, blank=True)
    raw_SS_json = models.TextField(null=True, blank=True)
    exclude_from_analysis = models.BooleanField(null=True, default=False, blank=True)

    def __str__(self):
        try:
            authorQS = self.authors.all()
            if len(authorQS) == 0:
                return("No Author (" + str(self.year) + ")")
            elif len(authorQS) == 1:
                return(self.authors.get(authorship__authorPosition="F").name + " (" + str(self.year) + ")")
            elif len(authorQS) == 2:
                return(self.authors.get(authorship__authorPosition="F").name + " and " + self.authors.get(authorship__authorPosition="L").name + " (" + str(self.year) + ")")
            else:
                return(self.authors.get(authorship__authorPosition="F").name + " et al. (" + str(self.year) + ")")
        except:
            return("error in __str__")

class Authorship(models.Model):
    class authorPosition(models.TextChoices):
        FIRST = 'F'
        INTERMEDIATE = "I"
        LAST = 'L',
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    authorPosition = models.CharField(max_length=15, choices=authorPosition.choices)

    def __str__(self):
        try:
            return(self.author.__str__() + " → " + self.paper.__str__())
        except:
            return("error in __str__")
