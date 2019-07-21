
import pymongo

class products:
    def __init__(self):
        super().__init__()
        self.status = ''

    def addProduct(self,product):
        #connect to the cluster
        dbClient = pymongo.MongoClient("mongodb://AtlasProductsUser:gOkFZIxFTXexrIar@products-shard-00-00-rpjfy.mongodb.net:27017,products-shard-00-01-rpjfy.mongodb.net:27017,products-shard-00-02-rpjfy.mongodb.net:27017/test?ssl=true&replicaSet=Products-shard-0&authSource=admin&retryWrites=true&w=majority")
        AtlasProducts = dbClient["AtlasProducts"]
        Products = AtlasProducts["Products"]

        flow = Products.insert_one(product)

        return flow.inserted_id



        
        
  


    
    
