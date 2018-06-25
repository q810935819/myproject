from django.shortcuts import render,reverse
from django.http import HttpResponse,JsonResponse

from . typesviews import gettypesorder
from ..models import Goods,Types

import os
# Create your views here.

# 执行文件的上传
def uploads(request):
    
    # 获取请求中的 文件 File 
    myfile = request.FILES.get('pic',None)

    # 获取上传的文件后缀名 myfile.name.split('.').pop()
    p = myfile.name.split('.').pop()
    arr = ['jpg','png','jpeg','gif']
    if p not in arr:
        return 1

    import time,random
    # 生成新的文件名
    filename = str(time.time())+str(random.randint(1,99999))+'.'+p
    
    # 打开文件
    destination = open("./static/goodspics/"+filename,"wb+")

    # 分块写入文件  
    for chunk in myfile.chunks():      
       destination.write(chunk)  

    # # destination.write(myfile.read()) #不推荐

    # 关闭文件
    destination.close()
    
    # return HttpResponse(filename)

    return '/static/goodspics/'+filename

def add(request):
	if request.method == 'GET':
		tlist = gettypesorder()
		context = {'tlist':tlist}
		return render(request,'myadmin/goods/add.html',context)

	elif request.method == 'POST':
		try:
			# 先判断是否有图片上传
			if not request.FILES.get('pic',None):
				return HttpResponse('<script>alert("必须选择商品图片");location.href="'+reverse('myadmin_goods_add')+'"</script>')
			pic = uploads(request)
			if pic == 1:
				return HttpResponse('<script>alert("图片类型错误");location.href="'+reverse('myadmin_goods_add')+'"</script>')

			# 执行商品添加  接收表单提交的数据
			data = request.POST.copy().dict()
			# 删除csrf验证的字段数据
			del data['csrfmiddlewaretoken']
			data['pics'] = pic

			data['typeid'] = Types.objects.get(id = data['typeid'])

			ob = Goods.objects.create(**data)
			return HttpResponse('<script>alert("添加成功");location.href="'+reverse('myadmin_goods_list')+'"</script>')
		except:
			return HttpResponse('<script>alert("添加失败");location.href="'+reverse('myadmin_goods_add')+'"</script>')
def index(request):
	# 获取搜索条件
	types = request.GET.get('type',None)
	keywords = request.GET.get('keywords',None)

	# 判断是否具有搜索条件

	if types:
		# 有搜索条件
		if types == 'all':
	# 全条件搜索
			# select * from user where username like '%aa%' 
			from django.db.models import Q
			glist = Goods.objects.filter(
			Q(price__contains=keywords)|
			Q(title__contains=keywords)|
			Q(store__contains=keywords)|
			Q(status__contains=keywords)
			)
	# 	elif types == 'typeid':
	# # 按照所属分类搜索
	# 		glist = Goods.objects.filter(typeid__contains=keywords)

		elif types == 'price':
		# 按照价格搜索
			glist = Goods.objects.filter(price__contains=keywords)

		elif types == 'title':
		# 按照商品名搜索
			glist = Goods.objects.filter(title__contains=keywords)

		elif types == 'store':
		# 按照库存搜索
			glist = Goods.objects.filter(store__contains=keywords)

		elif types == 'status':
		# 按照状态搜索
			glist = Goods.objects.filter(status__contains=keywords)


	else:
	# 获取所有的用户数据
		glist = Goods.objects.filter()


	# 判断排序条件
	# glist = glist.order_by('-id')

	# 导入分页类
	from django.core.paginator import Paginator
	# 实例化分页对象,参数1,数据集合,参数2 每页显示条数
	paginator = Paginator(glist, 10)
	# 获取当前页码数
	p = request.GET.get('p',1)
	# 获取当前页的数据
	glist = paginator.page(p)


	# 分配数据
	context = {'glist':glist}

	# 加载模板
	return render(request,'myadmin/goods/list.html',context)
	# glist = Goods.objects.all()

	# context = {'glist':glist}

	# return render(request,'myadmin/goods/list.html',context)
	

def delete(request):
	try:
		uid = request.GET.get('uid',None)
		ob = Goods.objects.get(id=uid)
		print(ob.status)
		# 判断当前用户是否右头像,如果右则删除
		# if ob.pics:
		# # /static/pics/
		# 	os.remove('.'+ob.pics)

		# ob.delete()
		ob.status = 1
		# print(ob.status)
		ob.save()
		print(ob.status)
		data = {'msg':'下架成功','code':0}
		return render(request,'myadmin/goods/list.html')
	except:
		data = {'msg':'下架失败','code':1}

	return JsonResponse(data)



def edit(request):
	# 接受参数
	uid = request.GET.get('uid',None)
	if not uid:
		return HttpResponse('<script>alert("没有用户数据");location.href="'+reverse('myadmin_goods_list')+'"</script>')

	# 获取对象
	ob = Goods.objects.get(id=uid)

	if request.method == 'GET':

		# 分配数据
		context = {'uinfo':ob}
		# 显示编辑页面
		return render(request,'myadmin/goods/edit.html',context)

	elif request.method == 'POST':

		try:
			# 判断是否上传了新的图片
			if request.FILES.get('pics',None):
				# 判断是否使用的默认图
				if ob.pics:
					# 如果使用的不是默认图,则删除之前上传的头像
					os.remove('.'+ob.pics)

					# 进行用户头像上传
					if request.FILES.get('pics',None):
						data['pics'] = uploads(request)
						if data['pics'] == 1:
							return HttpResponse('<script>alert("上传的文件类型不符合要求");location.href="'+reverse('myadmin_goods_add')+'"</script>')
					else:
						del data['pics']

				# 执行上传
				ob.pics = uploads(request)


			ob.title = request.POST['title']
			ob.descr = request.POST['descr']
			ob.price = request.POST['price']
			ob.store = request.POST['store']
			ob.pic = request.POST['pic']
			ob.info = request.POST['info']
			ob.save()

			return HttpResponse('<script>alert("更新成功");location.href="'+reverse('myadmin_goods_list')+'"</script>')
		except:
			return HttpResponse('<script>alert("更新失败");location.href="'+reverse('myadmin_goods_edit')+'?uid='+str(ob.id)+'"</script>')


