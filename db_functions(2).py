from pymongo import MongoClient
import hashlib

# MongoDB Connection #
cluster = MongoClient("mongodb+srv://abbask31:aggletes.tech@cluster0.8dwgr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["Agletes"]
collection = db["users"]

# Ticket Class #
class Ticket:

    def __init__(self, email, eventid, date, location, checked_in = False):

        self.email      = email
        self.eventid    = eventid
        self.checked_in = checked_in
        self.date = date
        self.location = location
        self.id = email + eventid

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

def add_ticket(ucd_email, ticket):
    collection.update_one({"_id":ucd_email}, {"$push": {"tickets":ticket.__dict__}})

def remove_ticket(ucd_email, ticket):
    collection.update_one({"_id":ucd_email}, {"$pull": {"tickets":{"id":ticket.id}}})

def update_check_in(ucd_email, ticket):
    collection.update_one({"_id":ucd_email, "tickets.id": ticket.id}, {"$set": {"tickets.$.checked_in":True}})

def delete_user(ucd_email):
    collection.update_one({"_id":ucd_email})

def delete_db():
    collection.delete_many({})

def log_in(ucd_email, password):
    user = collection.find_one({"_id":ucd_email})

    if user is None:
        return "This account has not been registered. Please try again or Create an Account"
    else:
        if ucd_email == user["_id"] and hash_password(password) == user["password"]:
            return user
        elif hash_password(password) != user["password"]:
            return "Incorrect Password"

def ticket_status(ucd_email, ticket, idx = 0):

    user = collection.find_one({"_id":ucd_email})

    for i, t in enumerate(user["tickets"]):
        if t["id"] == ticket.id:
            idx = i    

    return user["tickets"][idx]["checked_in"]

def game_date(ucd_email, ticket, idx = 0):
    user = collection.find_one({"_id":ucd_email})

    for i, t in enumerate(user["tickets"]):
        if t["id"] == ticket.id:
            idx = i    

    return user["tickets"][idx]["date"]

def get_phone(ucd_email):
    user = collection.find_one({"_id":ucd_email})
  
    return user["extras"]["phone_number"]

def game_location(ucd_email, ticket, idx = 0):
    user = collection.find_one({"_id":ucd_email})

    for i, t in enumerate(user["tickets"]):
        if t["id"] == ticket.id:
            idx = i    

    return user["tickets"][idx]["location"]


