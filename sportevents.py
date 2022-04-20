import os.path
import requests

MONTHS = {
    "Jan": '01',
    "Feb": '02',
    "Mar": '03',
    "Apr": '04',
    "May": '05',
    "Jun": '06',
    "Jul": '07',
    "Aug": '08',
    "Sep": '09',
    "Oct": '10',
    "Nov": '11',
    "Dec": '12'
}

class SportEvent:
    
    def __init__(self, sport="", date="", time="", at="", opp="", loc="", result="") -> None:

        self.id      = (sport + date + time).replace(' ', '').replace('.', '').replace('-','').replace('\'','').lower()
        self.sport   = sport
        self.date    = date
        self.time    = time
        self.at      = at
        self.opp     = opp
        self.loc     = loc
        self.result  = result

SportEvents = []

# SCRAPING AND SAVING RAW DATA
mainLink = "https://ucdavisaggies.com/schedule.aspx?path="
servLink = "https://ucdavisaggies.com/services/schedule_txt.ashx?schedule="

MSPORTS = [
    "baseball",
    "mbball",
    "cross",
    "football",
    "mgolf",
    "msoc",
    "mten",
    "track",
    "mwpolo"
]
WSPORTS = [
    "wbball",
    "wbvball",
    "equest",
    "fhockey",
    "wgolf",
    "wgym",
    "wlax",
    "wsoc",
    "softball",
    "wswim",
    "wten",
    "itrack",
    "wvball",
    "wwpolo"
]

ALLSPORTS = MSPORTS + WSPORTS

file = "sports.txt"
raw  = ""

if os.path.isfile(file):
    f = open(file, "r")
    raw = f.read()

else:
    f = open(file, "w")
    for i in ALLSPORTS:
        URL = mainLink + i
        res = requests.get(URL, headers= { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        })
        index = res.text.find('/services/schedule_txt.ashx?schedule=')+len('/services/schedule_txt.ashx?schedule=')
        code = res.text[index:index+4]

        URL = servLink + code
        res = requests.get(URL, headers= { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        })
        f.write(res.text + '\n' + '~'*100 + '\n')
        raw += res.text + '\n' + '~'*100 + '\n'




# RAW DATA BEING PARSED AND INITIALIZED INTO SPORTEVENT OBJECTS
def formatDate(dateStr):
    dateStr = dateStr.split()
    month   = MONTHS[dateStr[0]]
    day     = dateStr[1]
    year    = dateStr[3]

    if year.find('-') != -1 :
        if int(month) >= 1 :
            year = year[0:2]+year[5:7]
        else :
            year = year[0:4]

    dateStr = year+'-'+month+'-'+day

    return dateStr

def formatTime(timeStr):
    
    # timeStr = timeStr.lower()

    # if timeStr == "tba" or timeStr == "tbd" or timeStr == "all day":
    #     timeStr = ""
    # if timeStr == "noon":
    #     timeStr = "12:00"
    
    # if timeStr.endswith('t'):
    #     timeStr = timeStr[0: timeStr.rfind('.')]
    #     pass

    # # print(timeStr)

    # if timeStr.find('a') != -1:
    #     timeStr = timeStr[0:-4].strip()
    # if timeStr.find('p') != -1:
    #     timeStr = timeStr[0:-4].strip()
    #     hour = int(timeStr[0:1].replace(':',''))+12
    #     timeStr = str(hour) + (timeStr[timeStr.find(':'):] if ':' in timeStr else ':00')

    # # timeStr = timeStr[-4:]
    return timeStr

raw = raw.split('\n')

currentSport    = raw[2]
lineNumberSport = 0
indices         = [0, 0, 0, 0, 0, 0]
recording       = False

for lineNumberTotal, line in enumerate(raw):

    if(lineNumberTotal + 3 >= len(raw)):
        break

    if(line.startswith('~') and line.endswith('~')):
        currentSport    = raw[lineNumberTotal + 3]
        lineNumberSport = 0
        indices         = [0, 0, 0, 0, 0, 0]
        recording       = False
        
        # print(currentSport + ": ") 

    if (line.startswith("Date")):
        recording = True

    if(recording and line.split()):
        
        if (line.startswith("Date")):

            # print(line)

            props = ["Date", "Time", "At", "Opponent", "Location", "Result"]
            for i, prop in enumerate(props):
                indices[i] = (line.find(prop))

        else: 
            # print(line + " | " + str(indices))

            sport       = currentSport[0:-9].rstrip()

            date        = formatDate(line[0:indices[1]].rstrip() + " " + sport.split()[0])

            sport       = sport.split()
            sport.pop(0)
            sport       = ' '.join(sport)
            
            time        = formatTime(line[indices[1]:indices[2]].rstrip())
            at          = line[indices[2]:indices[3]].rstrip()
            opp         = line[indices[3]:indices[4]].rstrip()
            loc         = line[indices[4]:indices[5]].rstrip()
            result      = line[indices[5]:].rstrip()

            # print(time)

            event = SportEvent(sport, date, time, at, opp, loc, result)
            SportEvents.append(event)

    lineNumberSport += 1

