from twilio.rest import Client
import db_functions
from datetime import datetime, timedelta, date

# Your Account SID from twilio.com/console
account_sid = "KEY"
# Your Auth Token from twilio.com/console
auth_token  = "TOKEN"

client = Client(account_sid, auth_token)

def create_message(msg, phone_number):
    if type(phone_number) != str:
        phone_number = str(phone_number)

    message = client.messages.create(
        to = "+1" + phone_number,
        from_="+19705925216",
        body = msg        
    )


def ticket_notification(ucd_email, ticket, phone_number):
    
    # Query database for releavnt info 
    phone_number = db_functions.get_phone(ucd_email)
    has_checked_in = db_functions.ticket_status(ucd_email, ticket)
    g_date = db_functions.game_date(ucd_email, ticket)
    
    # parse date
    month = int(g_date[5:7])
    day = int(g_date[8:10])
    year = int(g_date[0:4])
    
    # calc days before a game
    parsed_date = date(year, month, day)
    
    t_date  = date.today()
    day_prior = (parsed_date - t_date).days
    
    
    # send text reminders using Twilio
    if not has_checked_in and day_prior == 1:
        create_message("Gametime soon! Make sure to be there tomorrow!", "5162257486")
    
    elif has_checked_in:
        create_message ("Enjoy the game!", "5162257486")

def giveaway_notification(ucd_email, phone_number):

    phone_number = db_functions.get_phone(ucd_email)

    create_message("Thanks for joining our giveaway! We will keep you posted on your entry. Good luck!", "5162257486") 
