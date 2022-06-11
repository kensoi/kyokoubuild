import vk_api, sqlite3, random, datetime, math, sys, requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

__connection = None

def get_connection(baseName: str):
    global __connection
    if __connection is None:
        __connection = sqlite3.connect(baseName)
    return __connection
    conn = get_connection()
    c = conn.cursor()

def init(t, i):
    vk_session = vk_api.VkApi(token=t)
    global vk, conn, c, vkPhoto, media, group_id, ans
    longpoll, vk = VkBotLongPoll(vk_session, i), vk_session.get_api()
    vkPhoto,group_id = vk.photos.getMessagesUploadServer(), i
    initWork = True
    print('\u0009VK API connected')
    
    media = {
        'img_standart': uploadPhoto(open('img/standart.jpg', 'rb')),
        'img_start': uploadPhoto(open('img/GEFtHBhVNWY.jpg', 'rb')),
        'img_ban': uploadPhoto(open('img/A_L3s3rLUYw.jpg', 'rb')),
        'img_bankick': uploadPhoto(open('img/xmlC4Gw_cec.jpg', 'rb')),
        'img_unban': uploadPhoto(open('img/jvtC37Z-638.jpg', 'rb')),
        'img_viphelp': uploadPhoto(open('img/mlKMUJfXDMo.jpg', 'rb')),
        'img_vipfail': uploadPhoto(open('img/QiroYk61PME.jpg', 'rb')),
        'img_admfail': uploadPhoto(open('img/6qZOPIFLhWA.jpg', 'rb')),
        'img_admcheck': uploadPhoto(open('img/qNhS7Z1Po9M.jpg', 'rb')),
        'video_admhelp': 'video-193595427_456239018',
        'video_work': 'video-193492235_456239027',
        }
    print('\u0009Media connected')
    
    conn = get_connection('database.db')
    c = conn.cursor()
    print('\u0009DB connected')

    while initWork:
        for event in longpoll.check():
            if event.type == VkBotEventType.MESSAGE_NEW:
                request = {
                        'chat_id': event.object['message']['peer_id'],
                        'user_id': event.object['message']["from_id"],
                        'messageId': event.object['message']["id"],
                        'messageText': event.object['message']['text'],
                        'key': '',
                        'action': ''
                        }
                try:
                    request['key'] = event.object['message']['payload']
                except:
                    pass
                try:
                    request['action'] = event.object['message']['action']
                except:
                    pass

                
                result = react(request)
                if result['type'] != '':
                    print('\u0009{} {}-{}\n\u0009\u0009Message: {}\n\u0009\u0009ReactType: {}\n'.format(str(datetime.datetime.now()), request['chat_id'], request['user_id'], request['messageText'], result['type']))
                for item in result['items']:
                    vk.messages.send(random_id=random.randint(0, 999999), message=item['messageText'], attachment = item['messageAttachment'], peer_id=request['chat_id'])
                if result['rule'] == 'send':
                    pass
                elif result['rule'] == 'kick':
                    try:
                        vk.messages.removeChatUser(chat_id = request['chat_id']-2000000000, user_id = result['subUser'])
                    except:
                        vk.messages.send(random_id=random.randint(0, 999999), message='Не получилось кикнуть пользователя.', attachment = '', peer_id=request['chat_id'])
                elif result['rule'] == 'close':
                    initWork = False 

def uploadPhoto(img):
    b = requests.post(vkPhoto['upload_url'], files={'photo': img}).json()
    c = vk.photos.saveMessagesPhoto(photo= b['photo'], server= b['server'], hash= b['hash'])[0]
    return 'photo{}_{}'.format(c['owner_id'], c['id'])

def namech(string: str):
    check, lenght = False, 0
    c.execute("SELECT name FROM names")
    for name in c.fetchall():
        (namestr, ) = name
        if string[0:string.find(' ')] == namestr:
            check = True
            lenght = len(name)
    return {'check': check, 'len': string.find(' ')}

def getUserBD(chat_id: int, user_id: int):
    ban, vip, mod, adm = False, False, False, False
    name, banreason = '', ''
    attempts = 3
    if user_id > 0:
        c.execute("INSERT INTO usrlist SELECT "+str(user_id)+", '[id"+str(user_id)+"|"+vk.users.get(user_ids = user_id)[0]['first_name']+"]', 0, 0 WHERE NOT EXISTS(SELECT 1 FROM usrlist WHERE id = "+str(user_id)+")")
        conn.commit()
        c.execute("SELECT name, admrole, viprole FROM usrlist WHERE id = ?", (user_id,))
        (name,adm,vip) = c.fetchall()[0]
        conv = vk_getChat(chat_id)['chat_settings']
        if conv['owner_id'] == user_id:
            mod = True
        else: 
            for i in conv['admin_ids']:
                if user_id == i:
                    mod = True
        c.execute('SELECT user_id, reason, try FROM banlist WHERE chat_id = ?', (chat_id,))
        res = c.fetchall()
        for i in range(len(res)):
            if ban == False:
                (usr, banreason, attempts) = res[i]
                if user_id == usr:
                    ban = True
    else: 
        name = '[club'+str(vk.groups.getById(group_id=str(math.fabs(user_id)))[0]['id'])+'|'+vk.groups.getById(group_id=str(math.fabs(user_id)))[0]['name']+']'
    return {
        'name': name, 
        'banStatus': ban, 'banReason': banreason, 'banAttempt': attempts, 
        'vipStatus': vip, 'modStatus': mod, 'admStatus': adm, 
    }
def updName(user_id: int, newName: str):
    if len(newName) > 30:
        return 0
    elif newName.lower() == 'admin':
        return 1
    else:
        c.execute("UPDATE usrlist SET name = '[id{}|{}]' WHERE id = {}".format(user_id, newName, user_id))
        conn.commit()
        return 2

def vk_getChat(chat_id):
    return vk.messages.getConversationsById(peer_ids = chat_id)['items'][0]
def getChatInfo(chat_id: int):
    c.execute("INSERT INTO chtlist SELECT "+str(chat_id)+", '"+vk_getChat(chat_id)['chat_settings']['title']+"', '"+ str(vk_getChat(chat_id)['chat_settings']['members_count'])+" участников', 'photo517114114_457255420', 0 WHERE NOT EXISTS(SELECT 1 FROM chtlist WHERE chat_id = "+str(chat_id)+")")
    conn.commit()
    c.execute("SELECT name, description, attachment FROM chtlist WHERE chat_id = ?", (chat_id,))
    (name, description, attachment) = c.fetchall()[0]
    return {'name': name, 
            'description': description, 
            'attachment': attachment}
def updChatInfo_name(chat_id: int, chatName: str):
    getChatInfo(chat_id)
    c.execute("UPDATE chtlist SET name = ? WHERE chat_id = ?", (chatName, chat_id))
    conn.commit()
def updChatInfo_description(chat_id: int, chatDescr: str):
    getChatInfo(chat_id)
    c.execute("UPDATE chtlist SET description = ? WHERE chat_id = ?", (chatDescr, chat_id))
    conn.commit()
def updChatInfo_attachment(chat_id: int, chatAtt: str):
    getChatInfo(chat_id)
    c.execute("UPDATE chtlist SET attachment = ? WHERE chat_id = ?", (chatAtt, chat_id))
    conn.commit()

def getChatBan(chat_id: int):
    text = ''
    c.execute("SELECT user_id, reason, try FROM banlist WHERE chat_id = ?", (chat_id,))
    for i in c.fetchall():
        (user_id, reason, att) = i
        res = getName(user_id)
        text = text + '\n\u2022 ' + res['res'] + ' ('+ kind(user_id) +')'
    return text

def react(r):
    typeMess, rule, link, listOfMessages, subUser = '', '0', '', [], 0
    namech_r = namech(r['messageText'].lower())
    if r['chat_id']>2000000000:
        getUserBDres = getUserBD(r['chat_id'], r['user_id'])
        if not getUserBDres['banStatus']:
            try:
                if r['action']['type'] == 'chat_invite_user' or r['action']['type'] == 'chat_invite_user_by_link':
                    if r['action']['member_id'] == '-195675828':
                        listOfMessages.append({
                                'messageText': 'Всем приветик! Все команды и инструкция по настройке находятся по ссылке vk.com/@canarybot-rules!'.format(getName(r['user_id'])['res']),
                                'messageAttachment': ''
                            })
                        rule = 'send'
                    elif r['action']['member_id'] > 0:
                        getUserBDsubRes = getUserBD(r['chat_id'], r['action']['member_id'])
                        if getUserBDsubRes['banStatus']:
                            listOfMessages.append({
                                'messageText': '{}, {} находится в чёрном списке, поэтому я его кикну.'.format(getUserBDres['name'], getUserBDsubRes['name']),
                                'messageAttachment': ''})
                            if getBDsubRes['banReason'] != '':
                                listOfMessages.append({
                                    'messageText': 'Причина блокировки: '.format(getUserBDres['banReason']),
                                    'messageAttachment': ''})
                            rule, subUser = 'kick', r['action']['member_id']
                        else:
                            listOfMessages.append({
                                'messageText': 'Приветик, {}, прочти статью для ознакомления с командами: vk.com/@canarybot-rules'.format(getUserBDsubRes['name']),
                                'messageAttachment': ''})
            except:
                pass
            if namech_r['check']:
                text = r['messageText']
                text = text[namech_r['len']+1:len(text)]
                if text.lower() == 'привет':
                    listOfMessages.append({
                        'messageText': 'Приветик, {}'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageReact'
                elif text.lower() == 'работай':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': media['video_work']
                    })
                    typeMess = 'messageReact'
                elif text.lower() == 'пожалей' and getUserBDres['admStatus']:
                    listOfMessages.append({
                        'messageText': '{}, *обняла* не робей, сенпай..'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageReact'
                elif text.lower() == 'помощь':
                    if not getUserBDres['admStatus']:
                        listOfMessages.append({
                            'messageText': '{}, вся нужная информация есть в этой статье: vk.com/@canarybot-rules'.format(getUserBDres['name']),
                            'messageAttachment': ''
                        })
                    else:
                        listOfMessages.append({
                            'messageText': '{}, посмотри лучше это:'.format(getUserBDres['name']),
                            'messageAttachment': media['video_admhelp']
                        })
                    typeMess = 'messageReact'
                elif text.lower() == 'инфа о беседе':
                    listOfMessages.append({
                        'messageText': 'Хорошо, {} вот информация о беседе:'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    resource = getChatInfo(r['chat_id'])
                    listOfMessages.append({
                        'messageText': '"{}"\nID чата в базе данных: {}\n\nОписание: {}'.format(resource['name'],str(r['chat_id']-2000000000), resource['description']),
                        'messageAttachment': resource['attachment']
                    })
                    typeMess = 'messageChatInfoShort'
                elif text.lower() == 'кто админ':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChatInfoAdm'
                elif text.lower() == 'кто в чс':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChatInfoBL'
                elif text[0:8].lower() == 'кто такой':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageUserInfoBD'
                elif text[0:13].lower() == 'чат название ':
                    updChatInfo_name(r['chat_id'], text[13:len(text)])
                    listOfMessages.append({
                        'messageText': '{}, название изменено на "{}"'.format(getUserBDres['name'], text[13:len(text)]),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChangeChatName'
                elif text[0:12].lower() == 'чат описание':
                    updChatInfo_description(r['chat_id'], text[13:len(text)])
                    listOfMessages.append({
                        'messageText': '{}, описание успешно изменено'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChangeChatDescription'
                elif text[0:12].lower() == 'чат вложение':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChangeChatAttachment'
                elif text[0:text.find(' ')].lower() == 'ник' and updName(r['user_id'], text[text.find(' ')+1:len(text)]) == 2:
                    listOfMessages.append({
                        'messageText': 'Поздравляем, {} сменил ник на {}'.format(getUserBDres['name'], text[text.find(' ')+1:len(text)]),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChangeNickname'
                elif text[0:text.find(' ')].lower() == 'кик' and text.count('[id') == 1 and text.count('|') == 1 and text.count(']') == 1:
                    subUser = int(text[text.find('[id')+3:text.find('|')])
                    getUserBDsubRes = getUserBD(r['chat_id'], subUser)
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChatKick'
                    rule = 'kick'
                elif text[0:text.find(' ')].lower() == 'бан' and text.count('[id') == 1 and text.count('|') == 1 and text.count(']') == 1:
                    subUser = int(text[text.find('[id')+3:text.find('|')])
                    getUserBDsubRes = getUserBD(r['chat_id'], subUser)
                    reason = text[text.find(']')+2:len(text)]
                    c.execute("INSERT INTO banlist SELECT ?, ?, ?, 3 WHERE NOT EXISTS(SELECT 1 FROM banlist WHERE chat_id = ? AND user_id = ?)", (r['chat_id'], subUser, reason, r['chat_id'], subUser))
                    conn.commit()
                    listOfMessages.append({
                        'messageText': '{} забанил {}. нигадяй'.format(getUserBDres['name'], getUserBDsubRes['name']),
                        'messageAttachment': media['img_ban']
                        })
                    typeMess = 'messageChatBan'
                    rule = 'ban'
                elif text[0:text.find(' ')].lower() == 'разбан' and text.count('[id') == 1 and text.count('|') == 1 and text.count(']') == 1:
                    subUser = int(text[text.find('[id')+3:text.find('|')])
                    getUserBDsubRes = getUserBD(r['chat_id'], subUser)
                    c.execute("DELETE FROM banlist WHERE chat_id = ? AND user_id = ?", (r['chat_id'], subUser))
                    listOfMessages.append({
                        'messageText': '{} разбанил {}. Неужли есть добрые люди..'.format(getUserBDres['name'], getUserBDsubRes['name']),
                        'messageAttachment': media['img_unban']
                        })
                    typeMess = 'messageChatUnban'
                elif text.lower() == 'добавь беседу':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChatlistAdd'
                elif text.lower() == 'обнови беседу':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChatlistUpd'
                elif text.lower() == 'убери беседу':
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': ''
                    })
                    typeMess = 'messageChatlistDel'
                elif text == 'выключить':
                    listOfMessages.append({
                        'messageText': 'Ладно, пойду посплю..',
                        'messageAttachment': ''
                        })
                    typeMess = 'admClose'
                    rule = 'close'
                else:
                    listOfMessages.append({
                        'messageText': '{},'.format(getUserBDres['name']),
                        'messageAttachment': media['img_admfail']
                    })
                    typeMess = 'messageNotDefined'
        elif getUserBDres['banAttempt'] > 1:
            listOfMessages.append({
                'messageText': '{} попытался нарушить табу беседы, осталось {} попыток.'.format(getUserBDres['name'], getUserBDres['banAttempt']-1),
                'messageAttachment': ''
            })
            c.execute("UPDATE banlist SET try = ? WHERE chat_id = ? AND user_id = ?", (getUserBDres['banAttempt']-1, r['chat_id'], r['user_id']))
        else: 
                listOfMessages.append({
                    'messageText': '{} попытался нарушить табу беседы, за что был кикнут из беседы.\nПричина блокировки: {}'.format(getUserBDres['name'], getUserBDres['banAttempt']-1, getUserBDres['banReason']),
                    'messageAttachment': media['img_bankick']
                })
                rule, identify_user = 'kick', r['user_id']
    else:
        t = r['messageText']
        if r['messageText'] == 'Начать' or r['key'] == '{"command":"start"}':
            listOfMessages.append({
                'messageText': 'Ой, привет, {}, почему ты пишешь мне?'.format(getUserBDres['name']),
                'messageAttachment': ''
            })
            listOfMessages.append({
                'messageText': 'Нужно добавиться в беседу? Ох, тогда смотри статью: vk.com/@canarybot-rules',
                'messageAttachment': media['img_standart']
            })
    return  {'type': typeMess,
        'rule': rule,
        'link': link,
        'items': listOfMessages,
        'subUser': subUser}

