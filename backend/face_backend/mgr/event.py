from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage
from common.models import Event
import json
import datetime
def dispatcher(request):
    # session处理
    if 'usertype' not in request.session:
        return JsonResponse({
            'ret': 302,
            'msg': '未登录'}, 
            status=302)

    if request.session['usertype'] != 'mgr' :
        return JsonResponse({
            'ret': 302,
            'msg': '用户非mgr类型'} ,
            status=302)

    # 将请求参数统一放入request 的 params 属性中，方便后续处理
    
    # GET请求 参数在url中，同过request 对象的 GET属性获取
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST','PUT','DELETE']:
        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        request.params = json.loads(request.body)



    # 根据不同的action分派给不同的函数进行处理
    
    action = request.params['action']
    if action == 'list_event':
        print("ok")
        return listevent(request)
    elif action == 'add_event':
        return addevent(request)
    elif action == 'modify_event':
        return modifyevent(request)
    elif action == 'del_event':
        return deletevent(request)

    else:
        return JsonResponse({'ret': 1, 'msg': '不支持该类型http请求'})


def listevent(request):
    try:
        # .order_by('-id') 表示按照 id字段的值 倒序排列
        # 这样可以保证最新的记录显示在最前面
        qs = Event.objects.values().order_by('-id')

        # 查看是否有 关键字 搜索 参数
        keywords = request.params.get('keywords',None)



        if keywords:
            start_datetime = keywords.split('#')[0]
            end_datetime = keywords.split('#')[1]
	    username =  keywords.split('#')[2]

            qs = qs.filter(time__range=(start_datetime,end_datetime),Username__contains=username)
        # print(qs)
        # 要获取的第几页
        pagenum = request.params['pagenum']

        # 每页要显示多少条记录
        pagesize = request.params['pagesize']

        # 使用分页对象，设定每页多少条记录
        pgnt = Paginator(qs, pagesize)

        # 从数据库中读取数据，指定读取其中第几页
        page = pgnt.page(pagenum)

        # 将 QuerySet 对象 转化为 list 类型
        retlist = list(page)

        # total指定了 一共有多少数据
        return JsonResponse({'ret': 0, 'retlist': retlist,'total': pgnt.count})

    except EmptyPage:
        return JsonResponse({'ret': 0, 'retlist': [], 'total': 0})

    except:
        return JsonResponse({'ret': 2,  'msg': f'未知错误'})


def addevent(request):

    info    = request.params['data']

    # 从请求消息中 获取要添加客户的信息
    # 并且插入到数据库中
    # 返回值 就是对应插入记录的对象 
    record = Event.objects.create(username=info['username'] ,
                            age=info['age'] ,
                            gender=info['gender'],
                            expression =info['expression'] )


    return JsonResponse({'ret': 0, 'id':record.id})

def modifyevent(request):

    # 从请求消息中 获取修改客户的信息
    # 找到该客户，并且进行修改操作
    
    eventid = request.params['id']
    newdata    = request.params['newdata']

    try:
        # 根据 id 从数据库中找到相应的客户记录
        event = Event.objects.get(id=eventid)
    except Event.DoesNotExist:
        return  {
                'ret': 1,
                'msg': f'id 为`{eventid}`的事件不存在'
        }


    if 'username' in  newdata:
        event.username = newdata['username']
    if 'age' in  newdata:
        event.age = newdata['age']
    if 'gender' in  newdata:
        event.gender = newdata['gender']
    if 'expression' in  newdata:
        event.expression = newdata['expression']

    # 注意，一定要执行save才能将修改信息保存到数据库
    event.save()

    return JsonResponse({'ret': 0})

def deletevent(request):

    eventid = request.params['id']

    try:
        # 根据 id 从数据库中找到相应的客户记录
        event = Event.objects.get(id=eventid)
    except Event.DoesNotExist:
        return  {
                'ret': 1,
                'msg': f'id 为`{eventid}`的事件不存在'
        }

    # delete 方法就将该记录从数据库中删除了
    event.delete()

    return JsonResponse({'ret': 0})
