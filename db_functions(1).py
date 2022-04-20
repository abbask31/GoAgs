from pymongo import MongoClient
import hashlib
import itertools

# MongoDB Connection #
cluster = MongoClient("mongodb+srv://abbask31:aggletes.tech@cluster0.8dwgr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["Agletes"]
collection = db["users"]

# Ticket Class #
class Ticket:
    id_iter = itertools.count()
    def __init__(self, sport, date, checked_in = False):
        
        self.sport = sport
        self.date = date
        self.checked_in = checked_in
        self.id = next(self.id_iter)

def hash_password(password):
    crypt = hashlib.sha512()
    crypt.update(password.encode('utf-8'))
    return crypt.hexdigest()

def sign_up( ucd_email, password, name, year, phone_number ):
    
    post = { 
        "_id":ucd_email,
        "tickets": [],
        "password": hash_password(password),
        "extras":{
            "name": name,
            "year": year,
            "phone_number": phone_number
        }
    }
    collection.insert_one(post)

def update_ticket(ucd_email, ticket):
    collection.update_one({"_id":ucd_email}, {"$push": {"tickets":ticket.__dict__}})

def update_check_in(ucd_email, ticket):
    collection.update_one({"_id":ucd_email, "tickets.id": ticket.id}, {"$set": {"tickets.$.checked_in":True}})

def delete_user(ucd_email):
    collection.update_one({"_id":ucd_email})

def delete_db():
    collection.delete_many({})

def login(ucd_email, password):
    user = collection.find_one({"_id":ucd_email})
    if user is None:
        return "This account has not been registered. Please try again or Create an Account"
    else:
        if ucd_email == user["_id"] and hash_password(password) == user["password"]:
            return user
        elif hash_password(password) != user["password"]:
            return "Incorrect Password"

def ticket_status(ucd_email, ticket):
    user = collection.find_one({"_id":ucd_email})

    return user["tickets"][ticket.id]["checked_in"]


