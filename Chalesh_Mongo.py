from telegram.ext import Updater, CommandHandler, Filters, MessageHandler,CallbackQueryHandler
import os
import datetime
import pymongo
from pymongo import MongoClient
from telegram import ReplyKeyboardMarkup,InlineKeyboardButton , InlineKeyboardMarkup
import dotenv
import sys

class Chalesh():
    def __init__(self):
        keyArray=[["Update"],["Cancel"]]
        self.key=ReplyKeyboardMarkup(keyArray)
        inLineKeyArray=[[InlineKeyboardButton("Start Time",callback_data="time")],[InlineKeyboardButton("Duration",callback_data="duration")]]
        self.inlineKey=InlineKeyboardMarkup(inLineKeyArray)

        inLineSaveTimeArray=[[InlineKeyboardButton("Save", callback_data="save time")]]
        self.inlineSaveTimeKey=InlineKeyboardMarkup(inLineSaveTimeArray)

        inLineSaveDurationArray = [[InlineKeyboardButton("Save", callback_data="save duration")]]
        self.inLineSaveDurationKey = InlineKeyboardMarkup(inLineSaveDurationArray)

        self.mindel, self.delNumber = 10, 10
        self.maxMessages = 1000
        self.chaleshID = os.getenv('chaleshID')
        self.duration=10

        self.clean = {
            "_id": self.chaleshID,
            "period": self.duration,
            "start": datetime.datetime.strptime("16:30","%H:%M"),
            "completed": datetime.datetime.today() - datetime.timedelta(days=1)
        }

        return


    def start(self,bot,update):
        bot.send_message(text="سلام آماده ام" , chat_id=update.message.chat_id, reply_markup=self.inlineKey)

        return

    def register(self,message_id,chat_id,user_id,type="Unknown"):
        if chat_id!= self.chaleshID:
            return None
        print("message_id:",message_id," chat_id:",chat_id," user_id:",user_id, " Type:", type)
        
        message = {"_id": message_id,
                   "chat_id": chat_id,
                   "user_id": user_id,
                   "date": datetime.datetime.today(),
                   "type": type}   #,"type": type

        duplicate = collection.find({"chat_id": self.clean["_id"]})
        if not duplicate is None:
            try:
                collection.insert_one(message)
            except Exception as exp:
                print("Error register:", exp)
        removeIdsArray=[]
        try:
            print("Count: ", collection.count_documents({"chat_id": self.chaleshID}))
            self.delNumber = collection.count_documents({"chat_id": self.chaleshID}) - self.maxMessages
            if min(self.mindel,self.delNumber)>0:
                removeIdsArray = collection.find({"chat_id":self.chaleshID}, {"_id": 1}).sort([("date", 1)]).limit(min(self.mindel,self.delNumber))   #.map(function(doc) {return doc._id;}); # Pull out just the _ids


        except Exception as e:
            print ("Error limit 1000: ", e)

        try:
            critical_date=datetime.datetime.today()-datetime.timedelta(days=self.clean["period"])
            if self.clean["completed"] < datetime.datetime.today() and datetime.datetime.now().time() > self.clean["start"].time():

                deleteCandidates=collection.find({"chat_id":self.clean["_id"],"date": { "$lte": critical_date }})
                for candidate in deleteCandidates:
                    print("Candidate to delete:",candidate["_id"])

                # Note: Temporary disable just for test
                self.clean["completed"]=datetime.datetime.today()
                try:
                    cleaning.insert_one(self.clean)
                except:
                    try:
                        cleaning.update_one(self.clean, { "$set": { "completed": self.clean["completed"] } })
                    except Exception as exp:
                        print("Error:", exp)
        except Exception as exp:
            print("Error Cleaning",exp)
        ########################################
        # print(message)
        return removeIdsArray

    def registerID(self,bot,update):
        print(update.message.from_user)
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'])

        try:
            for id in removeIdsArray:
                try:
                    bot.delete_message(chat_id=self.chaleshID, message_id=id)
                except:
                    continue

            collection.delete_many({"chat_id":self.chaleshID}).sort([("date", 1)]).limit(min(self.mindel,self.delNumber))
        except:
            pass
        ################################ Cleaning  ################

        return


    def removeMessageLeft(self,bot,update):
        print ("Start removeMessageLeft")
        bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        print(update.message.message_id , " removed")
        return

    def callback_func(self, bot, update):
        
        print("Effective message:",update._effective_message)
        print ("Start callback_func Joinning Message")
        bot.delete_message(chat_id=update._effective_message.chat_id, message_id=update._effective_message.message_id)
        print(update._effective_message.message_id, " removed")
        
        return


    def setTime(self,bot,update):
        bot.send_message("زمان شروع عملیات پاکسازی را مطابق با قالب ساعت : دقیقه وارد کنید", chat_id=update.message.chat_id, reply_markup=self.key)
        self.operation="setTime"
        return

    def setPeriod(self,bot,update):
        bot.send_message("پیامهای مربوط به چند روز قبل حذف شوند؟",chat_id = update.message.chat_id , reply_markup=self.key)
        self.operation="setPeriod"
        return

    def buttonsDriven(self,bot,update):
        button = update.callback_query
        if button=='time':
            bot.send_message("زمان شروع را وارد کنید",chat_id=update.message.chat_id, reply_markup=self.inlineSaveTimeKey)
        if button=='save time':
            startText=update.message.text
            defaultTime=datetime.datetime.strptime("16:30","%h:%m")
            try:
                self.startTime=datetime.datetime.strftime(startText,"%h:%m")
            except:
                self.startTime=defaultTime
                print("زمان شروع پاکسازی صحیح نمیباشد برای مثال طبق قالب ? ده دقیقه بعد از نیمه شب وارد کنید", self.startTime)

            self.clean["start"]=self.startTime

        if button=='duration':
            bot.send_message("زمان شروع را وارد کنید", chat_id=update.message.chat_id,
                             reply_markup=self.inLineSaveDurationKey)
        if button=='save duration':
            if button == 'save time':
                periodText = update.message.text
                try:
                    self.period = int(periodText)
                except:
                    self.period = 10
                    print("عددد وارد شده معتبر نمیباشد لطفأ دومرتبه سعی کنید")

            self.clean["period"]=self.period
        return

    def registerVideo(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Video")
        return

    def registerText(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'],"Text")
        return

    def registerAnimation(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Animation")
        return

    def registerCommand(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Command")
        return

    def registerContact(self, bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Contact")
        return

    def registerDocumant(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Document")
        return

    def registerForwarded(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Forwarded")
        try:
            for id in removeIdsArray:
                try:
                    print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id":self.chaleshID,"_id": id["_id"]})
                    #bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)

                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    print("Removed: ", self.chaleshID)
                except Exception as e:
                    print(e)
                    continue

        except Exception as e:
            print (e)

        return

    def registerGame(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Game")
        return

    def registerGroup(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Group")
        return

    def registerInvoice(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Invoice")
        return

    def registerLocation(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Location")
        return

    def registerPassport_data(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Passport")
        return

    def registerPhoto(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Photo")
        return

    def registerPrivate(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Private")
        return

    def registerReplay(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Replay")
        return

    def registerSticker(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Sticker")
        return

    def registerVenue(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Venue")
        return

    def registerVideo_Note(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Video Note")
        return

    def registerVoice(self,bot,update):
        removeIdsArray = self.register(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], "Voice")
        return


    def chaleshBot(self):
        updater=Updater("349821902:AAFDHs18HQLUzDNWSvpun8kolbQuvZAoQlE")
        updater.dispatcher.add_handler(CommandHandler("start", self.start))
        updater.dispatcher.add_handler(CommandHandler("time", self.setTime))
        updater.dispatcher.add_handler(CommandHandler("period", self.setPeriod))
        updater.dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member,self.removeMessageLeft))
        updater.dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, self.callback_func))
        updater.dispatcher.add_handler(MessageHandler(Filters.video,self.registerVideo,allow_edited=False))
        updater.dispatcher.add_handler(MessageHandler(Filters.text,self.registerText))
        updater.dispatcher.add_handler(MessageHandler(Filters.animation,self.registerAnimation))
        updater.dispatcher.add_handler(MessageHandler(Filters.command,self.registerCommand))
        updater.dispatcher.add_handler(MessageHandler(Filters.contact,self.registerContact))
        updater.dispatcher.add_handler(MessageHandler(Filters.document,self.registerDocumant))
        updater.dispatcher.add_handler(MessageHandler(Filters.forwarded,self.registerForwarded))
        updater.dispatcher.add_handler(MessageHandler(Filters.game,self.registerGame))
        updater.dispatcher.add_handler(MessageHandler(Filters.group,self.registerGroup))
        updater.dispatcher.add_handler(MessageHandler(Filters.invoice,self.registerInvoice))
        updater.dispatcher.add_handler(MessageHandler(Filters.location,self.registerLocation))
        updater.dispatcher.add_handler(MessageHandler(Filters.passport_data,self.registerPassport_data))
        updater.dispatcher.add_handler(MessageHandler(Filters.photo,self.registerPhoto,allow_edited=False))
        updater.dispatcher.add_handler(MessageHandler(Filters.private,self.registerPrivate))
        updater.dispatcher.add_handler(MessageHandler(Filters.reply,self.registerReplay))
        updater.dispatcher.add_handler(MessageHandler(Filters.sticker,self.registerSticker))
        updater.dispatcher.add_handler(MessageHandler(Filters.venue,self.registerVenue))
        updater.dispatcher.add_handler(MessageHandler(Filters.video_note,self.registerVideo_Note,allow_edited=False))
        updater.dispatcher.add_handler(MessageHandler(Filters.voice,self.registerVoice))

        updater.dispatcher.add_handler(MessageHandler(Filters.all,self.registerID))
        updater.dispatcher.add_handler(CallbackQueryHandler(self.buttonsDriven))

        #updater.dispatcher.add_handler(MessageHandler(Filters.status_update,self.test_filters_status_update))

        updater.start_polling()
        updater.idle()
        return


if __name__=="__main__":
    log=open("log.txt","a")
    dotenv.load_dotenv()
    user = os.getenv('user')       
    password = os.getenv('password')   

    cluster = MongoClient(f"mongodb+srv://{user}:{password}@cluster0-j47c5.gcp.mongodb.net/test?retryWrites=true&w=majority")
    print(cluster)
    db=cluster["Chalesh"]
    collection=db["Messages"]
    cleaning=db["Cleaning"]

    bot=Chalesh()
    bot.chaleshBot()
    log.close()


