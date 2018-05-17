from random import randint
from telebot import types
import telebot
import database
import random
db = database.database
deck = database.deck
import time
token = "550498827:AAGrkloMvGbcTybDLng4O3D4D1xE8Jo4dKY"
bot = telebot.TeleBot(token)
from firebase import firebase
statistics = database.statistics


url = "https://blackjack-telegram.firebaseio.com/"
fb = firebase.FirebaseApplication(url, None)

def update():
    statistics = fb.get(url, None)
    print(statistics)


def updFb(res, mes):
    id = str(mes.chat.id)

    if id in statistics:
        statistics[id][res] += 1
        fb.patch(id+"/", statistics[id])



def checkforWin(mes):
    usersdb = db[str(mes.chat.id)]
    userTotal = int(countValue(usersdb['cards']))
    dealerTotal = int(countValue(usersdb['dealer']['cards']))
    if usersdb['isStand'] == False:
        if userTotal > 21:
            bot.send_message(mes.chat.id, "YOU LOST! WHAT A SHAME! Let's try again?", reply_markup=newbut("Yeah!"))
            updFb("Losses", mes)
        elif userTotal == 21:
            bot.send_message(mes.chat.id, "Congratulations! You won! Wanna try again?", reply_markup=newbut("Yeah!"))
            updFb("Wins", mes)
        elif userTotal < 21 and usersdb['isStand'] == False:
            bot.send_message(mes.chat.id, "What would you like to do now?", reply_markup=newbut("Hit", "Stand"))

        elif list(usersdb['cards'].keys())[0][:3] == "Ace" and list(usersdb['cards'].keys())[1][:3] == "Ace":
            bot.send_message(mes.chat.id, "Congratulations! 'Tis BLACKJACKH! Wanna try again?", reply_markup=newbut("Yeah!"))
            updFb("Wins", mes)

    elif usersdb['isStand'] == True:
        newtotal = countValue(usersdb['dealer']['cards'])
        if newtotal == 21 and countValue(usersdb['cards']) < 21:
            bot.send_message(mes.chat.id, "YOU LOST! WHAT A SHAME! Let's try again?", reply_markup=newbut("Yeah!"))
            updFb("Losses", mes)

        elif newtotal == 21 and countValue(usersdb['cards']) == 21:
            bot.send_message(mes.chat.id, "Wow, it's a tie. Let's try again?", reply_markup=newbut("Yeah!"))
            updFb("Ties", mes)

        elif newtotal == countValue(usersdb['cards']):
            bot.send_message(mes.chat.id, "Wow, it's a tie. Let's try again?", reply_markup=newbut("Yeah!"))
            updFb("Ties", mes)

        elif list(usersdb['dealer']['cards'].keys())[0][:3] == "Ace" and list(usersdb['dealer']['cards'].keys())[1][:3] == "Ace":
            bot.send_message(mes.chat.id, "You lost! Dealer has BLACKJACK! Wanna try again?", reply_markup=newbut("Yeah!"))
            updFb("Losses", mes)

        elif newtotal < 21 and countValue(usersdb['cards']) > newtotal:
            bot.send_message(mes.chat.id, "Congratulations! You won! Wanna try again?", reply_markup=newbut("Yeah!"))
            updFb("Wins", mes)

        elif newtotal < 21 and countValue(usersdb['cards']) < newtotal:
            bot.send_message(mes.chat.id, "YOU LOST! WHAT A SHAME! Let's try again?", reply_markup=newbut("Yeah!"))
            updFb("Losses", mes)

        elif newtotal > 21:
            bot.send_message(mes.chat.id, "Congratulations! You won! Wanna try again?", reply_markup=newbut("Yeah!"))
            updFb("Wins", mes)

def findKey(key, dict):
    keys = list(dict.keys())
    values = list(dict.values())
    whattoreturn = False
    for i in range(0, len(dict)):
        if str(key) == str(keys[i]):
            whattoreturn = True#dict[str(keys[i])]
            print("Found key "+str(key))

    return whattoreturn

def countValue(usersdb):
    keys = list(usersdb.keys())
    values = list(usersdb.values())
    total = 0
    for i in range(0, len(keys)):
        total += int(values[i])
    return total

def dealerhit(mes):
    usersdb = db[str(mes.chat.id)]
    keys = list(usersdb['deck'].keys())
    newcard = random.choice(keys)
    usersdb['dealer']['cards'][str(newcard)] = deck[str(newcard)]
    usersdb['deck'].pop(str(newcard), None)
    newtotal = countValue(usersdb['dealer']['cards'])
    findAceForDealer(usersdb)
    bot.send_message(mes.chat.id, "Dealer takes a new card. It is " + str(newcard) + ". His total value is now " + str(newtotal))
    if newtotal < 17:
        time.sleep(1)
        dealerhit(mes)
    else:
        checkforWin(mes)



def finishgame(mes):
    usersdb = db[str(mes.chat.id)]
    usersdb['isStand'] = True
    dealer = usersdb['dealer']
    dealertotal = countValue(dealer['cards'])
    print("Debugging dealer's cards: "+str(dealer['cards']))
    bot.send_message(mes.chat.id, "Dealer is revealing his card. It is " + list(dealer['cards'].keys())[1]+". Dealer's total value is "+ str(dealertotal))
    if dealertotal < 17:
        dealerhit(mes)

    elif dealertotal > 16:
        checkforWin(mes)



def dealToDealer(usersdb):
    keys = list(usersdb['deck'].keys())
    userdeck = list(usersdb['deck'])
    usersdb['dealer']['cards'] = {}

    firstcard = random.choice(keys)
    usersdb['dealer']['cards'][str(firstcard)] = deck[str(firstcard)]
    usersdb['deck'].pop(str(firstcard), None)

    secondcard = random.choice(keys)
    usersdb['dealer']['cards'][str(secondcard)] = deck[str(secondcard)]
    usersdb['deck'].pop(str(secondcard), None)


    print("DEALER'S HAND: "+str(usersdb['dealer']['cards']))
    countValue(usersdb['dealer']['cards'])

def dealToUser(usersdb):
    keys = list(usersdb['deck'].keys())
    userdeck = list(usersdb['deck'])
    usersdb['cards'] = {}

    print("DEBUG: " + str(len(userdeck)))

    firstcard = random.choice(keys)
    usersdb['cards'][str(firstcard)] = deck[str(firstcard)]
    usersdb['deck'].pop(str(firstcard), None)

    secondcard = random.choice(keys)
    usersdb['cards'][str(secondcard)] = deck[str(secondcard)]
    usersdb['deck'].pop(str(secondcard), None)

    print("DEBUG: "+str(len(userdeck)))


    print(usersdb['cards'])
    print("DEBUG: " + str(len(userdeck)))
    countValue(usersdb['cards'])

def findAce(usersdb):
    db = usersdb['cards']
    keys = list(db.keys())
    values = list(db.values())
    print("User's cards: " + str(usersdb['cards']) + ". We gonna find aces")
    for i in range(0, len(db)):
        if str(keys[i][:3]) == "Ace" and countValue(db) > 21:
            db[str(keys[i])] = 1
            print(db)
            print("Changed one ace from 11 to 1")

def findAceForDealer(usersdb):
    db = usersdb['dealer']['cards']
    keys = list(db.keys())
    values = list(db.values())
    print("Dealers's cards: " + str(usersdb['dealer']['cards']) + ". We gonna find aces")
    for i in range(0, len(db)):
        if str(keys[i][:3]) == "Ace" and countValue(db) > 21:
            values[i] = 1
            print("Changed one ace from 11 to 1")

def setStage(stage, mes):
    if stage == "end":
        print("End, user won")
        bot.send_message(mes.chat.id, "Congratulations! You won! Wanna try again?", reply_markup=newbut("Yeah!"))
    else:
        print("what?")

def hit(mes):
    usersdb = db[str(mes.chat.id)]
    keys = list(usersdb['deck'].keys())
    newcard = random.choice(keys)
    usersdb['cards'][str(newcard)] = deck[str(newcard)]
    usersdb['deck'].pop(str(newcard), None)
    findAce(usersdb)
    newtotal = countValue(usersdb['cards'])

    bot.send_message(mes.chat.id,
                     "You hit and dealer gave you " + str(newcard) + ". Your total value is now " + str(newtotal))

    checkforWin(mes)

def newGame(mes):
    print("Starting new game for "+mes.from_user.first_name)
    print("Cards in deck: "+str(len(deck)))
    if findKey(mes.chat.id, db) != False:
        db.pop(str(mes.chat.id), None)
        print("User already existed, deleted his db entry")

    ############################ Preparing user's deck.
    db[str(mes.chat.id)] = {}
    udb = db[str(mes.chat.id)]
    udb['deck'] = deck.copy()
    udb['isStand'] = False
    ############################ Preparing user's dealer.
    udb['dealer'] = {}
    print("Dealer created")

    #### Let's deal some cards to dealer first
    dealToDealer(udb)
    print("Card dealt to dealer. Notifying user")


    bot.send_message(mes.chat.id, "Dealer has a closed card and an opened one, which is "+
                     str(list(udb['dealer']['cards'].keys())[0])+
                     ". It's value is "+
                     str(list(udb['dealer']['cards'].values())[0]))

    #### Let's deal to user now
    dealToUser(udb)
    userscards = udb['cards']
    usertotal = countValue(userscards)
    usercardnames = list(userscards.keys())

    findAce(udb)
    bot.send_message(mes.chat.id, "Your cards are "+usercardnames[0]+" and "+usercardnames[1]+". Total value: "+str(countValue(udb['cards'])))
    checkforWin(mes)

def newbut(*args):
    mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    buts = []
    for arg in args:
        but = types.KeyboardButton(arg)
        buts.append(but)
    mrkup.add(*buts)
    return mrkup

update()


@bot.message_handler(commands=["start"])
def handle_start(mes):
    bot.send_message(mes.chat.id, "Hello there! Let's play some blackjack!", reply_markup=newbut("Yeah!"))


@bot.message_handler(content_types=["text"])
def handle_text(mes):

    if mes.text == "Hit" and findKey(str(mes.chat.id), db) == True:
        print("User wants to hit. Let's give it to 'em")
        hit(mes)
    elif mes.text == "Stand" and findKey(str(mes.chat.id), db) == True:
        finishgame(mes)

    elif mes.text == "Yeah!":
        newGame(mes)

    elif findKey(str(mes.chat.id), db) == False:
        print("No user found. Starting a new game")
        bot.send_message(mes.chat.id, "Hello there! Let's play some blackjack!", reply_markup=newbut("Yeah!"))
    else:
        print("Something wrong")
        newGame(mes)


try:
    bot.polling()
except Exception as x:
    print(x)