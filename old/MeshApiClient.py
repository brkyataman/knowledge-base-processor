import requests
import json


class MeshApiClient:

    def __init__(self):
        self.base_address = "https://id.nlm.nih.gov/mesh/"
        self.req_count = 0

    def query_sparql(self, query,offset=0,limit=1000):
        self.req_count += 1
        params = dict(query=query, offset=offset, limit=limit, format="JSON", inference="true")
        response = requests.get(self.base_address + "sparql", params=params)

        # add http request guard

        result = json.loads(response.text)
        return result["results"]["bindings"]
