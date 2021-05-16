from utlis.rank import setrank,isrank,remrank,remsudos,setsudo, GPranks,IDrank
from utlis.send import send_msg, BYusers, GetLink,Name,Glang,getAge
from utlis.locks import st,getOR
from utlis.tg import Bot
from config import *

from pyrogram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import threading, requests, time, random, re, json, datetime
import importlib
from os import listdir
from os.path import isfile, join


from pyrogram.api.types import InputPeerChat
def allGP(client, message,redis):
  type = message.chat.type
  userID = message.from_user.id
  chatID = message.chat.id
  username = message.from_user.username
  if username is None:
    username = "None"
  userFN = message.from_user.first_name
  title = message.chat.title
  rank = isrank(redis,userID,chatID)
  text = message.text
  c = importlib.import_module("lang.arcmd")
  r = importlib.import_module("lang.arreply")
  redis.hincrby("{}Nbot:{}:msgs".format(BOT_ID,chatID),userID)
  if text :
    if re.search(c.setGPadmin,text):
      if re.search("@",text):
        user = text.split("@")[1]
      if re.search(c.setGPadmin2,text):
        user = int(re.search(r'\d+', text).group())
      if message.reply_to_message:
        user = message.reply_to_message.from_user.id
      if 'user' not in locals():return False
      if GPranks(userID,chatID) == "member":return False
      Getus = Bot("getChatMember",{"chat_id":chatID,"user_id":userID})["result"]
      if Getus["status"] == "administrator" and not Getus["can_promote_members"]:return False
      try:
        getUser = client.get_users(user)
        userId = getUser.id
        userFn = getUser.first_name
        if GPranks(userId,chatID) != "member":return False
        pr = Bot("promoteChatMember",{"chat_id":chatID,"user_id":userId,"can_change_info":1,"can_delete_messages":1,"can_invite_users":1,"can_restrict_members":1,"can_pin_messages":1})
        if pr["ok"]:
          T ="<a href=\"tg://user?id={}\">{}</a>".format(userId,Name(userFn))
          Bot("sendMessage",{"chat_id":chatID,"text":r.prGPadmin.format(T),"reply_to_message_id":message.message_id,"parse_mode":"html"})
      except Exception as e:
        Bot("sendMessage",{"chat_id":chatID,"text":r.userNocc,"reply_to_message_id":message.message_id,"parse_mode":"html"})

    if re.search(c.sors,text):
      kb = InlineKeyboardMarkup([[InlineKeyboardButton("حساب المطور", url="t.me/IM_KI")],[InlineKeyboardButton("تواصل البوت", url="t.me/IM_KI")],[InlineKeyboardButton("شروحات السورس 📑", url="t.me/tshaketeam")]])
      Botuser = client.get_me().username
      Bot("sendMessage",{"chat_id":chatID,"text":r.sors.format("@"+Botuser),"disable_web_page_preview":True,"reply_to_message_id":message.message_id,"parse_mode":"markdown","reply_markup":kb})
    
    if re.search(c.dellink,text):
      kb = InlineKeyboardMarkup([[InlineKeyboardButton(c.dellink2, url="https://telegram.org/deactivate")]])
      Botuser = client.get_me().username
      Bot("sendMessage",{"chat_id":chatID,"text":r.dellink,"disable_web_page_preview":True,"reply_to_message_id":message.message_id,"parse_mode":"markdown","reply_markup":kb})

    if re.search(c.ShowO,text) and (rank is not False or rank is not  0 or rank != "vip"):
      reply_markup = getOR(rank,r,userID)
      Bot("sendMessage",{"chat_id":chatID,"text":r.Showall,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True,"reply_markup":reply_markup})

    if text == "عدد الكروب" and (rank is not False or rank is not  0 ):
      from pyrogram.api.functions.channels import GetFullChannel
      chat = client.resolve_peer(chatID)
      full_chat = client.send(GetFullChannel(channel=chat)).full_chat
      Bot("sendMessage",{"chat_id":chatID,"text":r.gpinfo.format(message.chat.title,full_chat.participants_count,full_chat.admins_count,full_chat.kicked_count,full_chat.banned_count,message.message_id),"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})
    if text == c.ID and not redis.sismember("{}Nbot:IDSend".format(BOT_ID),chatID) and not message.reply_to_message:
      Ch = True
      # if redis.sismember("{}Nbot:IDpt".format(BOT_ID),chatID):
      t = IDrank(redis,userID,chatID,r)
      msgs = (redis.hget("{}Nbot:{}:msgs".format(BOT_ID,chatID),userID) or 0)
      edits = (redis.hget("{}Nbot:{}:edits".format(BOT_ID,chatID),userID) or 0)
      rate = int(msgs)*100/20000
      age = getAge(userID,r)
      if redis.hget("{}Nbot:SHOWid".format(BOT_ID),chatID):
        tx = redis.hget("{}Nbot:SHOWid".format(BOT_ID),chatID)
        rep = {"#age":"{age}","#name":"{name}","#id":"{id}","#username":"{username}","#msgs":"{msgs}","#stast":"{stast}","#edits":"{edits}","#rate":"{rate}","{us}":"{username}","#us":"{username}"}
        for v in rep.keys():
          tx = tx.replace(v,rep[v])
      else:
        tx = r.IDnPT
      if not redis.sismember("{}Nbot:IDSendPH".format(BOT_ID),chatID):
        get = Bot("getUserProfilePhotos",{"user_id":userID,"offset":0,"limit":1})
        if get["ok"] == False: 
          Ch = True
        elif get["result"]["total_count"] == 0:
          Ch = True
        else:
          Ch = False
          file_id = get["result"]["photos"][0][0]["file_id"]
          Bot("sendPhoto",{"chat_id":chatID,"photo":file_id,"caption":tx.format(username=("@"+username or "None"),id=userID,stast=t,msgs=msgs,edits=edits,age=age,rate=str(rate)+"%"),"reply_to_message_id":message.message_id,"parse_mode":"html"})
      if Ch == True:
        Bot("sendMessage",{"chat_id":chatID,"text":tx.format(username=("@"+username or "None"),id=userID,stast=t,msgs=msgs,edits=edits,age=age,rate=str(rate)+"%"),"reply_to_message_id":message.message_id,"parse_mode":"html"})

      # if not redis.sismember("{}Nbot:IDSendPH".format(BOT_ID),chatID) and not redis.sismember("{}Nbot:IDpt".format(BOT_ID),chatID):
      #   get = Bot("getUserProfilePhotos",{"user_id":userID,"offset":0,"limit":1})
      #   if get["ok"] == False: 
      #     Ch = True
      #   elif get["result"]["total_count"] == 0:
      #     Ch = True
      #   else:
      #     Ch = False
      #     reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(r.RIDPHs,callback_data=json.dumps(["ShowDateUser","",userID]))]])
      #     file_id = get["result"]["photos"][0][0]["file_id"]
      #     Bot("sendPhoto",{"chat_id":chatID,"photo":file_id,"caption":r.RID.format(userID),"reply_to_message_id":message.message_id,"parse_mode":"html","reply_markup":reply_markup})
      # if Ch == True and not redis.sismember("{}Nbot:IDpt".format(BOT_ID),chatID):
      #   reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(r.RIDPHs,callback_data=json.dumps(["ShowDateUser","",userID]))]])
      #   Bot("sendMessage",{"chat_id":chatID,"text":r.RID.format(userID),"reply_to_message_id":message.message_id,"parse_mode":"html","reply_markup":reply_markup})
    
    
      
    if text and re.search("الاسرع",text) and not redis.sismember("{}Nbot:gpgames".format(BOT_ID),chatID):
      KlamSpeed = ["سحور","سياره","استقبال","قنفه","ايفون","بزونه","مطبخ","كرستيانو","دجاجه","مدرسه","الوان","غرفه","ثلاجه","كهوه","سفينه","العراق","محطه","طياره","رادار","منزل","مستشفى","كهرباء","تفاحه","اخطبوط","سلمون","فرنسا","برتقاله","تفاح","مطرقه","بتيته","لهانه","شباك","باص","سمكه","ذباب","تلفاز","حاسوب","انترنيت","ساحه","جسر"]
      name = random.choice(KlamSpeed)
      temp = redis.set("{}Nbot:Klmspeed".format(BOT_ID),name)
      name = str.replace(name,"سحور","س ر و ح")
      name = str.replace(name,"سياره","ه ر س ي ا")
      name = str.replace(name,"استقبال","ل ب ا ت ق س ا")
      name = str.replace(name,"قنفه","ه ق ن ف")
      name = str.replace(name,"ايفون","و ن ف ا")
      name = str.replace(name,"بزونه","ز و ه ن")
      name = str.replace(name,"مطبخ","خ ب ط م")
      name = str.replace(name,"كرستيانو","س ت ا ن و ك ر ي")
      name = str.replace(name,"دجاجه","ج ج ا د ه")
      name = str.replace(name,"مدرسه","ه م د ر س")
      name = str.replace(name,"الوان","ن ا و ا ل")
      name = str.replace(name,"غرفه","غ ه ر ف")
      name = str.replace(name,"ثلاجه","ج ه ث ل ا")
      name = str.replace(name,"كهوه","ه ك ه و")
      name = str.replace(name,"سفينه","ه ن ف ي س")
      name = str.replace(name,"العراق","ق ع ا ل ر ا")
      name = str.replace(name,"محطه","ه ط م ح")
      name = str.replace(name,"طياره","ر ا ط ي ه")
      name = str.replace(name,"رادار","ر ا ر ا د")
      name = str.replace(name,"منزل","ن ز م ل")
      name = str.replace(name,"مستشفى","ى ش س ف ت م")
      name = str.replace(name,"كهرباء","ر ب ك ه ا ء")
      name = str.replace(name,"تفاحه","ح ه ا ت ف")
      name = str.replace(name,"اخطبوط","ط ب و ا خ ط")
      name = str.replace(name,"سلمون","ن م و ل س")
      name = str.replace(name,"فرنسا","ن ف ر س ا")
      name = str.replace(name,"برتقاله","ر ت ق ب ا ه ل")
      name = str.replace(name,"تفاح","ح ف ا ت")
      name = str.replace(name,"مطرقه","ه ط م ر ق")
      name = str.replace(name,"بتيته","ب ت ت ي ه")
      name = str.replace(name,"لهانه","ه ن ل ه ل")
      name = str.replace(name,"شباك","ب ش ا ك")
      name = str.replace(name,"باص","ص ا ب")
      name = str.replace(name,"سمكه","ك س م ه")
      name = str.replace(name,"ذباب","ب ا ب ذ")
      name = str.replace(name,"تلفاز","ت ف ل ز ا")
      name = str.replace(name,"حاسوب","س ا ح و ب")
      name = str.replace(name,"انترنيت","ا ت ن ر ن ي ت")
      name = str.replace(name,"ساحه","ح ا ه س")
      name = str.replace(name,"جسر","ر ج س")
      Bot("sendMessage",{"chat_id":chatID,"text":name,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})
      
     
      
    if re.search(str(redis.get("{}Nbot:Klmspeed".format(BOT_ID))), text):
       textmsg = "🎁┇مبروك. لقد حصلت على 5 نقاط زيادة كمكافأة لك للعب مرة اخرى ارسل {الاسرع}"
       redis.hincrby("{}Nbot:{}:points".format(BOT_ID,chatID),userID,5)
       Bot("sendMessage",{"chat_id":chatID,"text":textmsg,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})  

    if text and re.search("سمايلات",text) and not redis.sismember("{}Nbot:gpgames".format(BOT_ID),chatID):
      Random = ["🍏","🍎","🍐","🍊","🍋","🍉","🍇","🍓","🍈","🍒","🍑","🍍","🥥","🥝","🍅","🍆","🥑","🥦","🥒","🌶","🌽","🥕","🥔","🥖","🥐","🍞","🥨","🍟","🧀","🥚","🍳","🥓","🥩","🍗","🍖","🌭","🍔","🍠","🍕","🥪","🥙","☕️","🍵","🥤","🍶","🍺","🍻","🏀","⚽️","🏈","⚾️","🎾","🏐","🏉","🎱","🏓","🏸","🥅","🎰","🎮","🎳","🎯","🎲","🎻","🎸","🎺","🥁","🎹","🎼","🎧","🎤","🎬","🎨","🎭","🎪","🎟","🎫","🎗","🏵","🎖","🏆","🥌","🛷","🚗","🚌","🏎","🚓","🚑","🚚","🚛","🚜","🇮🇶","⚔","🛡","🔮","🌡","💣","📌","📍","📓","📗","📂","📅","📪","📫","📬","📭","⏰","📺","🎚","☎️","📡"]
      SM = random.choice(Random)
      tempSM = redis.set("{}Nbot:smiles".format(BOT_ID),SM)
      Bot("sendMessage",{"chat_id":chatID,"text":f"🔰┇ اسرع واحد يرسل هذا السمايل : {SM} ","reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})
   
    if re.search(str(redis.get("{}Nbot:smiles".format(BOT_ID))), text):
       textmsg = "🎁┇مبروك. لقد حصلت على 7 نقاط زيادة كمكافأة لك للعب مرة اخرى ارسل {سمايلات}"
       redis.hincrby("{}Nbot:{}:points".format(BOT_ID,chatID),userID,7)
       Bot("sendMessage",{"chat_id":chatID,"text":textmsg,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True}) 
    
    if text and re.search("حزوره",text) and not redis.sismember("{}Nbot:gpgames".format(BOT_ID),chatID):
      Hzora = ["الجرس","عقرب الساعه","السمك","المطر","5","الكتاب","البسمار","7","الكعبه","بيت الشعر","لهانه","انا","امي","الابره","الساعه","22","غلط","كم الساعه","البيتنجان","البيض","المرايه","الضوء","الهواء","الضل","العمر","القلم","المشط","الحفره","البحر","الثلج","الاسفنج","الصوت","بلم"]
      name = random.choice(Hzora)
      temp = redis.set("{}Nbot:Hzor".format(BOT_ID),name)
      name = str.replace(name,"الجرس","شيئ اذا لمسته صرخ ما هوه ؟")
      name = str.replace(name,"عقرب الساعه","اخوان لا يستطيعان تمضيه اكثر من دقيقه معا فما هما ؟")
      name = str.replace(name,"السمك","ما هو الحيوان الذي لم يصعد الى سفينة نوح عليه السلام ؟")
      name = str.replace(name,"المطر","شيئ يسقط على رأسك من الاعلى ولا يجرحك فما هو ؟")
      name = str.replace(name,"5","ما العدد الذي اذا ضربته بنفسه واضفت عليه 5 يصبح ثلاثين ")
      name = str.replace(name,"الكتاب","ما الشيئ الذي له اوراق وليس له جذور ؟")
      name = str.replace(name,"البسمار","ما هو الشيئ الذي لا يمشي الا بالضرب ؟")
      name = str.replace(name,"7","عائله مؤلفه من 6 بنات واخ لكل منهن .فكم عدد افراد العائله ")
      name = str.replace(name,"الكعبه","ما هو الشيئ الموجود وسط مكة ؟")
      name = str.replace(name,"بيت الشعر","ما هو البيت الذي ليس فيه ابواب ولا نوافذ ؟ ")
      name = str.replace(name,"لهانه","وحده حلوه ومغروره تلبس مية تنوره .من هيه ؟ ")
      name = str.replace(name,"انا","ابن امك وابن ابيك وليس باختك ولا باخيك فمن يكون ؟")
      name = str.replace(name,"امي","اخت خالك وليست خالتك من تكون ؟ ")
      name = str.replace(name,"الابره","ما هو الشيئ الذي كلما خطا خطوه فقد شيئا من ذيله ؟ ")
      name = str.replace(name,"الساعه","ما هو الشيئ الذي يقول الصدق ولكنه اذا جاع كذب ؟")
      name = str.replace(name,"22","كم مره ينطبق عقربا الساعه على بعضهما في اليوم الواحد ")
      name = str.replace(name,"غلط","ما هي الكلمه الوحيده التي تلفض غلط دائما ؟ ")
      name = str.replace(name,"كم الساعه","ما هو السؤال الذي تختلف اجابته دائما ؟")
      name = str.replace(name,"البيتنجان","جسم اسود وقلب ابيض وراس اخظر فما هو ؟")
      name = str.replace(name,"البيض","ماهو الشيئ الذي اسمه على لونه ؟")
      name = str.replace(name,"المرايه","ارى كل شيئ من دون عيون من اكون ؟ ")
      name = str.replace(name,"الضوء","ما هو الشيئ الذي يخترق الزجاج ولا يكسره ؟")
      name = str.replace(name,"الهواء","ما هو الشيئ الذي يسير امامك ولا تراه ؟")
      name = str.replace(name,"الضل","ما هو الشيئ الذي يلاحقك اينما تذهب ؟ ")
      name = str.replace(name,"العمر","ما هو الشيء الذي كلما طال قصر ؟ ")
      name = str.replace(name,"القلم","ما هو الشيئ الذي يكتب ولا يقرأ ؟")
      name = str.replace(name,"المشط","له أسنان ولا يعض ما هو ؟ ")
      name = str.replace(name,"الحفره","ما هو الشيئ اذا أخذنا منه ازداد وكبر ؟")
      name = str.replace(name,"البحر","ما هو الشيئ الذي يرفع اثقال ولا يقدر يرفع مسمار ؟")
      name = str.replace(name,"الثلج","انا ابن الماء فان تركوني في الماء مت فمن انا ؟")
      name = str.replace(name,"الاسفنج","كلي ثقوب ومع ذالك احفض الماء فمن اكون ؟")
      name = str.replace(name,"الصوت","اسير بلا رجلين ولا ادخل الا بالاذنين فمن انا ؟")
      name = str.replace(name,"بلم","حامل ومحمول نصف ناشف ونصف مبلول فمن اكون ؟ ")
      Bot("sendMessage",{"chat_id":chatID,"text":f"🔰┇ اسرع واحد يحل الحزوره : {name}","reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})

    if re.search(str(redis.get("{}Nbot:Hzor".format(BOT_ID))), text):
       textmsg = "🎁┇مبروك. لقد حصلت على 8 نقاط زيادة كمكافأة لك للعب مرة اخرى ارسل {حزوره}"
       redis.hincrby("{}Nbot:{}:points".format(BOT_ID,chatID),userID,8)
       Bot("sendMessage",{"chat_id":chatID,"text":textmsg,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True}) 




    if text and re.search("معاني",text) and not redis.sismember("{}Nbot:gpgames".format(BOT_ID),chatID):
      Maany_Rand = ["قرد","دجاجه","بطريق","ضفدع","بومه","نحله","ديك","جمل","بقره","دولفين","تمساح","قرش","نمر","اخطبوط","سمكه","خفاش","اسد","فأر","ذئب","فراشه","عقرب","زرافه","قنفذ","تفاحه","باذنجان"]
      name = random.choice(Maany_Rand)
      temp = redis.set("{}Nbot:MaanyRand".format(BOT_ID),name)
      name = str.replace(name,"قرد","🐒")
      name = str.replace(name,"دجاجه","🐔")
      name = str.replace(name,"بطريق","🐧")
      name = str.replace(name,"ضفدع","🐸")
      name = str.replace(name,"بومه","🦉")
      name = str.replace(name,"نحله","🐝")
      name = str.replace(name,"ديك","🐓")
      name = str.replace(name,"جمل","🐫")
      name = str.replace(name,"بقره","🐄")
      name = str.replace(name,"دولفين","🐬")
      name = str.replace(name,"تمساح","🐊")
      name = str.replace(name,"قرش","🦈")
      name = str.replace(name,"نمر","🐅")
      name = str.replace(name,"اخطبوط","🐙")
      name = str.replace(name,"سمكه","🐟")
      name = str.replace(name,"خفاش","🦇")
      name = str.replace(name,"اسد","🦁")
      name = str.replace(name,"فأر","🐭")
      name = str.replace(name,"ذئب","🐺")
      name = str.replace(name,"فراشه","🦋")
      name = str.replace(name,"عقرب","🦂")
      name = str.replace(name,"زرافه","🦒")
      name = str.replace(name,"قنفذ","🦔")
      name = str.replace(name,"تفاحه","🍎")
      name = str.replace(name,"باذنجان","🍆")
      Bot("sendMessage",{"chat_id":chatID,"text":f"🔰┇ اسرع واحد يدز معنى السمايل : {name}","reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})

    if re.search(str(redis.get("{}Nbot:MaanyRand".format(BOT_ID))), text):
       textmsg = "🎁┇مبروك. لقد حصلت على 6 نقاط زيادة كمكافأة لك للعب مرة اخرى ارسل {معاني}"
       redis.hincrby("{}Nbot:{}:points".format(BOT_ID,chatID),userID,6)
       Bot("sendMessage",{"chat_id":chatID,"text":textmsg,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True}) 

    if text and re.search("العكس",text) and not redis.sismember("{}Nbot:gpgames".format(BOT_ID),chatID):
      katu = ["باي","فهمت","موزين","اسمعك","احبك","موحلو","نضيف","حاره","ناصي","جوه","سريع","ونسه","طويل","سمين","ضعيف","شريف","شجاع","رحت","عدل","نشيط","شبعان","موعطشان","خوش ولد","اني","هادئ"]
      name = random.choice(katu)
      temp = redis.set("{}Nbot:opissite".format(BOT_ID),name)
      name = str.replace(name,"باي","هلو")
      name = str.replace(name,"فهمت","مافهمت")
      name = str.replace(name,"موزين","زين")
      name = str.replace(name,"اسمعك","ماسمعك")
      name = str.replace(name,"احبك","ماحبك")
      name = str.replace(name,"موحلو","حلو")
      name = str.replace(name,"نضيف","وصخ")
      name = str.replace(name,"حاره","بارده")
      name = str.replace(name,"ناصي","عالي")
      name = str.replace(name,"جوه","فوك")
      name = str.replace(name,"سريع","بطيء")
      name = str.replace(name,"ونسه","ضوجه")
      name = str.replace(name,"طويل","قزم")
      name = str.replace(name,"سمين","ضعيف")
      name = str.replace(name,"ضعيف","قوي")
      name = str.replace(name,"شريف","كواد")
      name = str.replace(name,"شجاع","جبان")
      name = str.replace(name,"رحت","اجيت")
      name = str.replace(name,"عدل","ميت")
      name = str.replace(name,"نشيط","كسول")
      name = str.replace(name,"شبعان","جوعان")
      name = str.replace(name,"موعطشان","عطشان")
      name = str.replace(name,"خوش ولد","موخوش ولد")
      name = str.replace(name,"اني","مطي")
      name = str.replace(name,"هادئ","عصبي")
      Bot("sendMessage",{"chat_id":chatID,"text":f"🔰┇ اسرع واحد يدز العكس : {name}","reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})


    
    
    
    
    if re.search(str(redis.get("{}Nbot:opissite".format(BOT_ID))), text):
       textmsg = "🎁┇مبروك. لقد حصلت على 10 نقاط زيادة كمكافأة لك للعب مرة اخرى ارسل {العكس}"
       redis.hincrby("{}Nbot:{}:points".format(BOT_ID,chatID),userID,10)
       Bot("sendMessage",{"chat_id":chatID,"text":textmsg,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True}) 

    if text and re.search("امثله",text) and not redis.sismember("{}Nbot:gpgames".format(BOT_ID),chatID):
      mthal = ["جوز","ضراطه","الحبل","الحافي","شقره","بيدك","سلايه","النخله","الخيل","حداد","المبلل","يركص","قرد","العنب","العمه","الخبز","بالحصاد","شهر","شكه","يكحله"]
      name = random.choice(mthal)
      temp = redis.set("{}Nbot:amthila".format(BOT_ID),name)
      name = str.replace(name,"جوز","ينطي____للماعده سنون")
      name = str.replace(name,"ضراطه","الي يسوق المطي يتحمل___")
      name = str.replace(name,"بيدك","اكل___محد يفيدك")
      name = str.replace(name,"الحافي","تجدي من___نعال")
      name = str.replace(name,"شقره","مع الخيل يا___")
      name = str.replace(name,"النخله","الطول طول___والعقل عقل الصخلة")
      name = str.replace(name,"سلايه","بالوجه امراية وبالظهر___")
      name = str.replace(name,"الخيل","من قلة___شدو على الچلاب سروج")
      name = str.replace(name,"حداد","موكل من صخم وجهه كال آني___")
      name = str.replace(name,"المبلل","___ما يخاف من المطر")
      name = str.replace(name,"الحبل","اللي تلدغة الحية يخاف من جرة___")
      name = str.replace(name,"يركص","المايعرف___يكول الكاع عوجه")
      name = str.replace(name,"العنب","المايلوح___يكول حامض")
      name = str.replace(name,"العمه","___إذا حبت الچنة ابليس يدخل الجنة")
      name = str.replace(name,"الخبز","انطي___للخباز حتى لو ياكل نصه")
      name = str.replace(name,"باحصاد","اسمة___ومنجله مكسور")
      name = str.replace(name,"شهر","امشي__ولا تعبر نهر")
      name = str.replace(name,"شكه","يامن تعب يامن__يا من على الحاضر لكة")
      name = str.replace(name,"القرد","__بعين امه غزال")
      name = str.replace(name,"يكحله","اجه___عماها")
      Bot("sendMessage",{"chat_id":chatID,"text":f"🔰┇ اسرع واحد يكمل المثل : {name}","reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})

    if re.search(str(redis.get("{}Nbot:amthila".format(BOT_ID))), text):
       textmsg = "🎁┇مبروك. لقد حصلت على 10 نقاط زيادة كمكافأة لك للعب مرة اخرى ارسل {امثله}"
       redis.hincrby("{}Nbot:{}:points".format(BOT_ID,chatID),userID,10)
       Bot("sendMessage",{"chat_id":chatID,"text":textmsg,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True}) 
    if text and re.search("بوبي",text):
      namebot = ["عمري فداك  بوبي" , " ها حبيبي 🌚♥️ " ,"كول حبيبي ؟ " , " ها حبي وياك مكتب ئلسيد "," الو الو رد مخنوك ","ها يحلو كول"," عمري الحلو " , " صاعد اتصال ويا الحب دقيقة وجيك 😘💘 "," مشغول حالياً 🌚🌸 " , " لابسك لتلح " ," هايروحي؟ "]
      randomresponse = random.choice(namebot)
      Bot("sendMessage",{"chat_id":chatID,"text":randomresponse,"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})
      
    if text == "رتبتي":
      t = IDrank(redis,userID,chatID,r)
      Bot("sendMessage",{"chat_id":chatID,"text":f"⏏️꒐ موقعك : {t}","reply_to_message_id":message.message_id,"parse_mode":"html"})
    if text == c.ID and not redis.sismember("{}Nbot:IDSend".format(BOT_ID),chatID) and message.reply_to_message:
      us = message.reply_to_message.from_user.id
      rusername = message.reply_to_message.from_user.username
      if rusername is None:
        rusername = "None"
      t = IDrank(redis,us,chatID,r)
      msgs = (redis.hget("{}Nbot:{}:msgs".format(BOT_ID,chatID),us) or 0)
      edits = (redis.hget("{}Nbot:{}:edits".format(BOT_ID,chatID),us) or 0)
      rate = int(msgs)*100/20000
      age = getAge(us,r)
      tx = r.ReIDnPT
      Bot("sendMessage",{"chat_id":chatID,"text":tx.format(Reus=("@"+rusername or "None"),ReID=us,Rerank=t,Remsgs=msgs,Reedits=edits,Rage=age,Rerate=str(rate)+"%"),"reply_to_message_id":message.message_id,"parse_mode":"html"})
    if re.search(c.idus,text) and not redis.sismember("{}Nbot:IDSend".format(BOT_ID),chatID):
      user = text.split("@")[1]
      try:
        getUser = client.get_users(user)
        us = getUser.id
        rusername = user
        if rusername is None:
          rusername = "None"
        age = getAge(us,r)
        t = IDrank(redis,us,chatID,r)
        msgs = (redis.hget("{}Nbot:{}:msgs".format(BOT_ID,chatID),us) or 0)
        edits = (redis.hget("{}Nbot:{}:edits".format(BOT_ID,chatID),us) or 0)
        rate = int(msgs)*100/20000
        tx = r.ReIDnPT
        Bot("sendMessage",{"chat_id":chatID,"text":tx.format(Reus=("@"+rusername or "None"),ReID=us,Rerank=t,Remsgs=msgs,Reedits=edits,Rage=age,Rerate=str(rate)+"%"),"reply_to_message_id":message.message_id,"parse_mode":"html"})
      except Exception as e:
        print(e)

    if re.search(c.ShowSudos, text):
      tx = (redis.get("{}Nbot:SHOWsudos".format(BOT_ID)) or "")
      Bot("sendMessage",{"chat_id":chatID,"text":tx,"reply_to_message_id":message.message_id,"parse_mode":"html"})
    if text == c.mymsgs:
      get = redis.hget("{}Nbot:{}:msgs".format(BOT_ID,chatID),userID)
      Bot("sendMessage",{"chat_id":chatID,"text":r.yourmsgs.format((get or 0)),"reply_to_message_id":message.message_id,"parse_mode":"html"})
    if text == c.link and not redis.sismember("{}Nbot:showlink".format(BOT_ID),chatID):
      get = (redis.hget("{}Nbot:links".format(BOT_ID),chatID) or GetLink(chatID) or "none")
      Bot("sendMessage",{"chat_id":chatID,"text":r.showGPlk.format(get),"reply_to_message_id":message.message_id,"parse_mode":"html","disable_web_page_preview":True})

    if text == c.myedits:
      get = redis.hget("{}Nbot:{}:edits".format(BOT_ID,chatID),userID)
      Bot("sendMessage",{"chat_id":chatID,"text":r.youredits.format((get or 0)),"reply_to_message_id":message.message_id,"parse_mode":"html"})

    if text == c.myaddcontact:
      get = redis.hget("{}Nbot:{}:addcontact".format(BOT_ID,chatID),userID)
      Bot("sendMessage",{"chat_id":chatID,"text":r.youraddcontact.format((get or 0)),"reply_to_message_id":message.message_id,"parse_mode":"html"})
    
    
    if not redis.sismember("{}Nbot:ReplySendBOT".format(BOT_ID),chatID):
      if redis.hexists("{}Nbot:TXreplys".format(BOT_ID),text):
        tx = redis.hget("{}Nbot:TXreplys".format(BOT_ID),text)
        try:
          rep = {"#cn":"{cn}","#age":"{age}","#fn":"{fn}","#id":"{id}","#username":"{username}","#msgs":"{msgs}","#stast":"{stast}","#edits":"{edits}","#rate":"{rate}","{us}":"{username}","#us":"{username}"}
          for v in rep.keys():
            tx = tx.replace(v,rep[v])
          Bot("sendMessage",{"chat_id":chatID,"text":tx.format(fn=userFN,username=("@"+username or "n"),id=userID,stast=IDrank(redis,userID,chatID,r),cn=title),"reply_to_message_id":message.message_id,"parse_mode":"html"})
        except Exception as e:
          Bot("sendMessage",{"chat_id":chatID,"text":tx,"reply_to_message_id":message.message_id,"parse_mode":"html"})
          
      if redis.hexists("{}Nbot:STreplys".format(BOT_ID),text):
        ID = redis.hget("{}Nbot:STreplys".format(BOT_ID),text)
        Bot("sendSticker",{"chat_id":chatID,"sticker":ID,"reply_to_message_id":message.message_id})
      
      if redis.hexists("{}Nbot:GFreplys".format(BOT_ID),text):
        ID = redis.hget("{}Nbot:GFreplys".format(BOT_ID),text)
        Bot("sendanimation",{"chat_id":chatID,"animation":ID,"reply_to_message_id":message.message_id})

      if redis.hexists("{}Nbot:{}:VOreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:VOreplys".format(BOT_ID),text)
        Bot("sendvoice",{"chat_id":chatID,"voice":ID,"reply_to_message_id":message.message_id})

      if redis.hexists("{}Nbot:PHreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:PHreplys".format(BOT_ID),text)
        Bot("sendphoto",{"chat_id":chatID,"photo":ID,"reply_to_message_id":message.message_id})

      if redis.hexists("{}Nbot:DOreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:DOreplys".format(BOT_ID),text)
        Bot("sendDocument",{"chat_id":chatID,"document":ID,"reply_to_message_id":message.message_id})



    if not redis.sismember("{}Nbot:ReplySend".format(BOT_ID),chatID):
      if redis.hexists("{}Nbot:{}:TXreplys".format(BOT_ID,chatID),text):
        tx = redis.hget("{}Nbot:{}:TXreplys".format(BOT_ID,chatID),text)
        try:
          rep = {"#cn":"{cn}","#age":"{age}","#fn":"{fn}","#id":"{id}","#username":"{username}","#msgs":"{msgs}","#stast":"{stast}","#edits":"{edits}","#rate":"{rate}","{us}":"{username}","#us":"{username}"}
          for v in rep.keys():
            tx = tx.replace(v,rep[v])
          Bot("sendMessage",{"chat_id":chatID,"text":tx.format(fn=userFN,username=("@"+username or "n"),id=userID,stast=IDrank(redis,userID,chatID,r),cn=title),"reply_to_message_id":message.message_id,"parse_mode":"html"})
        except Exception as e:
          Bot("sendMessage",{"chat_id":chatID,"text":tx,"reply_to_message_id":message.message_id,"parse_mode":"html"})

      if redis.hexists("{}Nbot:{}:STreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:{}:STreplys".format(BOT_ID,chatID),text)
        Bot("sendSticker",{"chat_id":chatID,"sticker":ID,"reply_to_message_id":message.message_id})
      
      if redis.hexists("{}Nbot:{}:GFreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:{}:GFreplys".format(BOT_ID,chatID),text)
        Bot("sendanimation",{"chat_id":chatID,"animation":ID,"reply_to_message_id":message.message_id})

      if redis.hexists("{}Nbot:{}:VOreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:{}:VOreplys".format(BOT_ID,chatID),text)
        Bot("sendvoice",{"chat_id":chatID,"voice":ID,"reply_to_message_id":message.message_id})
       
      if redis.hexists("{}Nbot:{}:AUreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:{}:AUreplys".format(BOT_ID,chatID),text)
        Bot("sendaudio",{"chat_id":chatID,"audio":ID,"reply_to_message_id":message.message_id})
 
      if redis.hexists("{}Nbot:{}:PHreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:{}:PHreplys".format(BOT_ID,chatID),text)
        Bot("sendphoto",{"chat_id":chatID,"photo":ID,"reply_to_message_id":message.message_id})

      if redis.hexists("{}Nbot:{}:DOreplys".format(BOT_ID,chatID),text):
        ID = redis.hget("{}Nbot:{}:DOreplys".format(BOT_ID,chatID),text)
        Bot("sendDocument",{"chat_id":chatID,"document":ID,"reply_to_message_id":message.message_id})

  if redis.smembers("{}Nbot:botfiles".format(BOT_ID)):
    onlyfiles = [f for f in listdir("files") if isfile(join("files", f))]
    filesR = redis.smembers("{}Nbot:botfiles".format(BOT_ID))
    for f in onlyfiles:
      if f in filesR:
        fi = f.replace(".py","")
        UpMs= "files."+fi
        try:
          U = importlib.import_module(UpMs)
          t = threading.Thread(target=U.updateMsgs,args=(client, message,redis))
          t.daemon = True
          t.start()
          importlib.reload(U)
        except Exception as e:
          import traceback
          traceback.print_exc()
          print(e)
          pass
