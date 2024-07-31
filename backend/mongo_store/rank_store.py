import os
import pymongo


class RankStore:
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ["MONGO_URI"])
        self.db = self.client[os.environ["SMART_WEALTH_MONGO_STORE"]]
        self.collection = self.db["company-rank"]

    def get_top_k_companies(self, k: int):
        query = {"rank": {"$lte": k}}
        return sorted(
            list(self.collection.find(query, projection={"_id": False})),
            key=lambda x: x["rank"],
        )
