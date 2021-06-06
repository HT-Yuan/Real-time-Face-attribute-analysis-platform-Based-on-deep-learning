import  requests,pprint
import datetime
import random

ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
genderList = ['Male', 'Female']
emotionList = ['angry','disgust', 'fear', 'happy','sad', 'surprise', 'neutral']

payload = {
    'username': 'huatsing',
    'password': '000421'
}


response = requests.post("http://huatsing.pythonanywhere.com/api/mgr/signin",
                             data=payload)
pprint.pprint(response.json())

sessionid = response.cookies['sessionid']



for i in range(100):
    age = random.randint(0,7)
    gender = random.randint(0,1)
    emotion = random.randint(0,6)
    time = datetime.datetime.now()
    time = time.strftime('%Y-%m-%d %H:%M:%S')

    payload = {
        'action': 'add_event',

        "data":{
            "time":time,
            "username":"huatsing",
            "age":ageList[age],
            "expression":emotionList[emotion],
            "gender":genderList[gender]
        }
    }
    response = requests.post('http://huatsing.pythonanywhere.com/api/mgr/event', json=payload,cookies={'sessionid': sessionid})
    if(response.json()['ret']!=0):
        print("出错了",response.json()['msg'])

