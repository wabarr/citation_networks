class SSPaper:
    def __init__(self, semanticscholarID):
        self.semanticscholarID = semanticscholarID
        self.semantic_API_url = "https://api.semanticscholar.org/graph/v1/paper/"
        try:
            import requests
            fields = ["authors", "journal", "citationCount", "title", "publicationTypes", "citations", "citations.authors", "citations.year", "citations.title", "citations.journal", "year", "abstract"]
            URL = self.semantic_API_url + self.semanticscholarID + "?fields={fields}".format(fields=",".join(fields))
            print(URL)
            paper = requests.get(URL)
            if paper.status_code == 404:
                raise Exception(paper.json()["error"])
            if paper.status_code == 200:
                self.json=paper.json()
        except:
            raise Exception("something dreadful happened when trying to fetch paper {id}.  Check your URL".format(id=self.semanticscholarID))

    def json(self):
        print(self.json)

