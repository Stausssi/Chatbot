from datetime import datetime, timedelta
from random import randint
from gtts import gTTS
import requests, os, wikipedia, time
#import webbrowser

wikipedia.set_lang("de")
lang = "de"

userInput = ""
userName = ""

answered = False
nameGiven = False

weather_date_key = ""
currentDate = datetime.now()

healthy = {"gut", "super", "blendend", "traumhaft", "sehr gut", "richtig gut", "überragend", "wunderbar"}

greet_answers = {
    0: "",
    1: "Ich bin {}!",
    2: "Mein Name ist {}!",
    3: "Meine Entwickler haben mich '{}' getauft!",
    4: "Wie ist dein Name?",
    5: "Wie heißt du?",
    6: "Wer bist du?",
    7: "Schön dich kennen zu lernen{}!",
    8: "Freut mich,{}!",
    9: "Hallo{}!",
    10: "Grüß Gott!",
    11: "Servus{}!",
    12: "Guten Morgen{}!"
}

langs = {
    "pl" : "Bobinski",
    "af" : "Stephen Hawking",
    "de" : "Stephanie",
    "tr" : "Ömer"
}


def bot_output(msg):
    os.system("pkill omxplayer")
    
    global answered
    answered = True

    print(langs.get(lang).upper() + ": " + msg)
    
    TTS_obj = gTTS("H " + msg, lang)
    TTS_obj.save("tts.mp3")

    os.system("omxplayer tts.mp3 >/dev/null 2>&1 &")


def get_weather_data(): 

    key = "2c8bb4c453be605143ff6ad59e0b7b84"

    base_url = "api.openweathermap.org/data/2.5/"
    extra_information = "&units=metric&lang=de"

    if weather_date_key == "jetzt":
        base_url += "weather?"
    else:
        base_url += "forecast?"
        h_difference = round((24 - currentDate.hour) / 3, 0)
        d_difference = 6 - currentDate.isoweekday() 
        switcher = {
            "heute" : h_difference,
            "morgen" : h_difference + 8,
            "übermorgen" : h_difference + 16,
            "wochenende" : d_difference * 8 + h_difference + 16
        }

        if(switcher.get(weather_date_key) > 50):
            bot_output("Ich kann das Wetter leider nur maximal 5 Tage im Vorraus ermitteln!")
            return
        else:
            extra_information += "&cnt=" + str(switcher.get(weather_date_key)).replace(".0", "")

    city = "Stuttgart Feuerbach"

    url = "http://" + base_url + "appid=" + key + "&q=" + city + extra_information

    response = requests.get(url)

    weather_data = response.json()

    if weather_data["cod"] != "404" and weather_date_key == "jetzt":
        tmp = weather_data["main"]

        temperature = tmp["temp"]
        humidity = tmp["humidity"]
        desc = weather_data["weather"][0]["description"]
        pressure = tmp["pressure"]

        bot_output("Hier das jetzige Wetter in Stuttgart Feuerbach:" 
                   + "\n- Die Temperatur beträgt: " + str(round(temperature, 2)) 
                   + "°C\n- Die Luftfeuchtigkeit beträgt: " + str(humidity) 
                   + "%\n- Der Luftdruck beträgt: " + str(pressure) 
                   + "hPa\n- Beschreibung: " + desc)

    elif weather_data["cod"] != "404" and weather_date_key != "jetzt":
        loopcount = 0
        temp = 0
        min_temp = 100
        max_temp = -100
        humidity = 0
        pressure = 0

        for section in weather_data["list"]:
            if (weather_date_key != "wochenende" and loopcount >= weather_data["cnt"] - 8) or (weather_date_key == "wochenende" and loopcount >= weather_data["cnt"] - 16) or weather_date_key == "morgen":
                tmp = section["main"]
                temp += tmp["temp"]
                humidity += tmp["humidity"]
                pressure += tmp["pressure"]

                if max_temp < tmp["temp_max"]:
                    max_temp = tmp["temp_max"]

                if min_temp > tmp["temp_min"]:
                    min_temp = tmp["temp_min"]

            
            loopcount +=1
            
        if weather_date_key != "wochenende" and weather_date_key != "heute":
            temp /= 8
            humidity /= 8
            pressure /= 8
        elif weather_date_key == "wochenende":
            temp /= 16
            humidity /= 16
            pressure /= 16
        else:
            temp /= h_difference
            humidity /= h_difference
            pressure /= h_difference

        bot_output("Hier das durchschnittliche Wetter für '{}' in Stuttgart Feuerbach:".format(weather_date_key.capitalize())
                   + "\n- Die erwartete Temperatur beträgt: {}°C (zwischen {}°C und {}°C)".format(str(round(temp, 2)), str(min_temp), str(max_temp))
                   + "\n- Die erwartete Luftfeuchtigkeit beträgt: {}%".format(str(round(humidity, 2)))
                   + "\n- Der erwartete Luftdruck beträgt: {}hPa".format(str(round(pressure, 2))))
    else:
        bot_output("Ich konnte leider kein Wetter für Stuttgart Feuerbach finden!")


def isWeekend(date):
    return date.weekday() > 4


def get_user_input():
    if nameGiven:
        return input(userName.upper() + ": ").strip().lower()
    else:
        return input("> ").strip().lower()


def no_answer():
    answers = {
        1: "Das kann ich dir leider nicht beantworten!",
        2: "Darauf habe ich noch keine Antwort!",
        3: "Tut mir leid aber auf diese Frage habe ich keine Antwort parat!",
        4: "Das kann ich leider noch nicht!"
    }
    return answers.get(randint(1, 4))


def get_time_diff(date1, date2):
    diff = date2 -date1

    days_diff = diff.days
    sec_diff = diff.seconds

    d_diff = divmod(sec_diff, 86400)
    h_diff = divmod(d_diff[1], 3600)
    m_diff = divmod(h_diff[1], 60)
    s_diff = m_diff[1]

    return days_diff, h_diff[0], m_diff[0], s_diff


def get_user_name():
    global nameGiven

    if not nameGiven:
        global userName
        userName = get_user_input()

        nameGiven = True

    return userName.lower().capitalize()   


def greet():
    secondIdent = 0
    if not nameGiven:
        secondIdent = randint(4, 6)

    bot_output(greet_answers.get(randint(1, 3)).format(langs.get(lang))+ " " + greet_answers.get(secondIdent))

    if not nameGiven:
        bot_output(greet_answers.get(randint(7, 9)).format(" " + get_user_name()))


def get_wiki(keyword):
    keyword = keyword.replace("wer ", "").replace("was ", "").replace("ist ", "").replace("sind ", "").replace("war ", "").replace("?", "").strip()

    bot_output(no_answer() + " Soll ich auf Wikipedia nachschlagen?")
    input = get_user_input()

    if "ja" in input:
        try: 
            bot_output(wikipedia.summary(keyword))
        except wikipedia.exceptions.PageError:
            bot_output("Ich habe nichts auf Wikipedia für '" + keyword + "' gefunden!")
        except wikipedia.exceptions.DisambiguationError:
            bot_output("Ich habe zu viele Ergebnisse für '" + keyword + "' gefunden! Versuche dein Schlagwort zu präzisieren!")
    else:
        bot_output("Alles klar!")


def context_WER():
    for word in userInput.split(" "):
        if "bist" in word and "du" in userInput:
            greet()
            break
        elif "bin" in word and "ich" in userInput:
            bot_output("Du bist mein Gesprächspartner")
            break
        elif "dich" in word and ("programmiert" in userInput or "entwickelt" in userInput or "geschaffen" in userInput):
            bot_output("Simon Stauss, Leon Unbehaun und Tom-Luis Vince")
            break
        elif "ist" in word or "sind" in word or "war" in word:
            if "leon" in userInput or "simon" in userInput or "tom" in userInput:
                bot_output("Mein(e) Entwickler.")
            elif "deine" in userInput and "entwickler" in userInput:
                bot_output("Simon Stauss, Leon Unbehaun und Tom-Luis Vince")
            else:
                get_wiki(userInput)

            break


def context_WAS():
    for word in userInput.split(" "):
        if "datum" in word and "heute" in userInput:
            bot_output("Das heutige Datum ist: " + currentDate.strftime("%d-%b-%Y"))
            break
        elif "tag" in word and "heute" in userInput:
            dtoday = currentDate.strftime('%A')
            bot_output("Heute ist " + dtoday + ", der " + currentDate.strftime("%d-%b-%Y"))
            break
        elif "jahr" in word: 
            bot_output("Wir haben das Jahr " + str(currentDate.year))
            break
        elif "name" in word and "dein" in userInput:
            greet()
            break
        elif "essen" in word or "speiseplan" in word or "speisekarte" in word:
            #bot_output("Der Speiseplan wurde in einem neuen Fenster geöffnet!")
            #webbrowser.open_new('/home/pi/Desktop/sp.pdf')

            bot_output("Am Freitag gibt es folgendes zu essen:\n"
                       + "beFIT:\n"
                       + "  Seelachsfilet auf Gemüsebulgur mit Joghurtdip\n"
                       + "4,60€\n\n"
                       + "Hauptgericht:\n"
                       + "  Kraut-Schupfnudeln\n"
                       + "3,30€\n\n"
                       + "Stammessen:\n"
                       + "  Klare Brühe mit 3 Grießklöschen\n"
                       + "  Geröstete Maultaschen mit Ei\n"
                       + "  Kartoffelsalat\n"
                       + "3,60€\n\n"
                       + "Beilagen:\n"
                       + "  Schwarzwurzeln\n"
                       + "  Vollkornzöpfli\n"
                       + "  Reis\n"
                       + "  Salzkartoffeln\n"
                       + "Für jeweils 0,80€")

            break
        elif "ist" in word or "sind" in word or "war" in word:
            get_wiki(userInput)
            break


def context_WIE():
    for word in userInput.split(" "):
        if "wetter" in word:

            global weather_date_key
            weather_date_key = "jetzt"

            if "heute" in userInput:
                weather_date_key = "heute"
            elif "morgen" in userInput and "übermorgen" not in userInput:
                weather_date_key = "morgen"
            elif "übermorgen" in userInput:
                weather_date_key = "übermorgen"
            elif "wochenende" in userInput:
                weather_date_key = "wochenende"

            get_weather_data()
            break

        elif "name" in word or "heißt" in word or "heist" in word or "heisst" in word:
            greet()
            break

        elif "zeit" in word or "uhr" in word or "uhrzeit" in word: 

            minutes = currentDate.minute
            hours = currentDate.hour
    
            if minutes < 10:
                bot_output(str(hours) + ":0" + str(minutes))
            else:
                bot_output(str(hours) + ":" + str(minutes))
            break

        elif ("geht" in word and "es" in userInput) or "gehts" in word:
            bot_output("Mir geht es gut! Wie geht es dir?")
            health = get_user_input()
            if health in healthy:
                bot_output("Freut mich!")
            else:
                bot_output("Das wird schon wieder!")
            
            break
        elif "alt" in word and "du" in userInput:
            createDate = datetime(2019, 11, 11, 10, 32)

            diff = get_time_diff(createDate, currentDate)
            bot_output("Ich existiere seit {} Tagen, {} Stunden, {} Minuten und {} Sekunden!".format(diff[0], diff[1], diff[2], diff[3]))
            break

        
def context_WANN():
    year = currentDate.year
    month = currentDate.month
    day = currentDate.day

    for word in userInput.split(" "):
        if "feierabend" in word:
            if isWeekend(currentDate):
                bot_output("Am Wochenende wird nicht gearbeitet!")
            else: 
                endTime = datetime(year, month, day, 15, 30)

                diff = get_time_diff(currentDate, endTime)

                bot_output("Noch {} Stunden, {} Minuten und {} Sekunden bis zum Feierabend!".format(diff[1], diff[2], diff[3]))
                break

        elif "arbeitsbeginn" in word:
            startTime = datetime(year, month, day + 1, 7, 15)

            if isWeekend(currentDate) or currentDate.weekday() == 4:
                startTime += timedelta(days = 6 - currentDate.weekday())

            diff = get_time_diff(currentDate, startTime)

            bot_output("Noch {} Tage, {} Stunden, {} Minuten und {} Sekunden bis zum nächsten Arbeitsbeginn!".format(diff[0], diff[1], diff[2], diff[3]))
            break

        elif "weihnachten" in word:
            christmas = datetime(year, 12, 24, 18)

            diff = get_time_diff(currentDate, christmas)

            bot_output("Noch {} Tage, {} Stunden, {} Minuten und {} Sekunden bis heilig Abend!".format(diff[0], diff[1], diff[2], diff[3]))
            break


def get_context(questionWord):
    if questionWord == "warum":
        bot_output("Warum-Fragen kann ich leider noch nicht beantworten!")
    elif questionWord == "wo":
        bot_output("Wo-Fragen kann ich leider noch nicht beantworten!")
    elif questionWord == "was":
        context_WAS()
    elif questionWord == "wann":
        context_WANN()
    elif questionWord == "wie":
        context_WIE()
    elif questionWord == "wer":
        context_WER()
    else:
        if "hallo" in userInput or "servus" in userInput or "moin" in userInput or "hi" in userInput:
            firstIdent = randint(9, 12)
            if not nameGiven:
                firstIdent = randint(9, 12)
                bot_output(greet_answers.get(firstIdent).format("") + " " + greet_answers.get(randint(4, 6)))
                bot_output(greet_answers.get(randint(7, 9)).format(" " + get_user_name()))
            else:
                bot_output(greet_answers.get(firstIdent).format(" " + get_user_name()))
        elif "dank" in userInput:
            answers = {
                1: "Ich helfe gerne!",
                2: "Bitte!",
                3: "Gern geschehen."
            }

            bot_output(answers.get(randint(1, 3)))
        elif "wechsel" in userInput or "wechsle" in userInput:
            global lang

            picture = None

            if "bobinski" in userInput and lang != "pl":
                lang = "pl"
                
                picture = open("/home/pi/Desktop/bobinski.txt")
                
            elif "stephen hawking" in userInput and lang != "af":
                lang = "af"

                picture = open("/home/pi/Desktop/hawking.txt")

            elif ("deutsch" in userInput or "stephanie" in userInput) and lang != "de":
                lang = "de"

                picture = open("/home/pi/Desktop/stephanie.txt")

            elif ("oemer" in userInput or "ömer" in userInput or "peker" in userInput) and lang != "tr":
                lang = "tr"

                picture = open("/home/pi/Desktop/oemer.txt")

            elif langs.get(lang).lower() in userInput:
                bot_output("Du redest schon mit mir!")
                return
            else:
                bot_output("Diese Person existiert (noch) nicht!")
                return

            os.system("clear")
            os.system("setfont Uni3-TerminusBold16.psf.gz")
            
            print(picture.read())
            picture.close()

            TTS_obj = gTTS("H Du redest nun mit " + langs.get(lang) + "!", lang)
            TTS_obj.save("tts.mp3")

            os.system("pkill omxplayer")
            os.system("omxplayer tts.mp3 >/dev/null 2>&1 &")

            time.sleep(4)
            os.system("clear")

            global answered
            answered = True

            greeting()
        else:
            bot_output(no_answer())
     
            
def get_question_word():
    for word in userInput.split(" "):
        if "warum" in word or "weshalb" in word:
            return "warum"
        elif "wo" in word:
            return "wo"
        elif "was" in word or "welcher" in word or "welches" in word or "welchen" in word:
            return "was"
        elif "wann" in word:
            return "wann"
        elif "wer" in word or "welche" in word:
            return "wer"
        elif "wie" in word:
            return "wie"
    
    return "none"
     
       
def parse_input():
    if userInput == "":
        answers = {
            1: "Qualitativ hochwertiger Beitrag!",
            2: "\\n",
            3: "Grenzwertige Aussage...",
            4: "<Blank>"
        }
        bot_output(answers.get(randint(1, 4)))
    else:
        get_context(get_question_word())
    

def valid_input():
    return "stop" not in userInput and "bis bald" not in userInput


def greeting():
    os.system("setfont Uni3-TerminusBold32x16.psf.gz")

    print("""
    ______________  ______________________________________ 
    __  ____/__  / / /__    |__  __/__  __ )_  __ \__  __ )
    _  /    __  /_/ /__  /| |_  /  __  __  |  / / /_  __  |
    / /___  _  __  / _  ___ |  /   _  /_/ // /_/ /_  /_/ / 
    \____/  /_/ /_/  /_/  |_/_/    /_____/ \____/ /_____/ inski
    """)

    print("Beende die Konversation mit 'stop' oder 'bis bald'!\n")


# programm

os.system("setterm -foreground black -background white")
os.system("clear")

os.system("omxplayer greeting.mp3 >/dev/null 2>&1 &")

greeting()

while(True):
    userInput = get_user_input()

    if valid_input():
        currentDate = datetime.now().replace(microsecond = 0)
        answered = False
        parse_input()
        
        if not answered:
            bot_output(no_answer())
    else:
        break

bot_output("Bis bald!\n")