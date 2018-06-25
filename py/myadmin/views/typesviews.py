from django.shortcuts import render,reverse
from django.http import HttpResponse,JsonResponse
from .. models import Types
# Create your views here.
def gettypesorder():
	# 获取所有数据
	# tlist = Types.objects.all()
	tlist = Types.objects.extra(select = {'paths':'concat(path,id)'}).order_by('paths')
	for x in tlist:
		if x.pid == 0:
			x.pname = '顶级分类'
		else:
			t = Types.objects.get(id=x.pid)
			x.pname = t.name
		num = x.path.count(',')-1
		x.name = (num*'|----')+x.name
	return tlist

def add(request):
	if request.method == 'GET':
		# 返回一个添加页面
		
		# 获取当前数据库中的分类
		tlist = gettypesorder()
		
		context = {'tlist':tlist}

		return render(request,'myadmin/types/add.html',context)
	elif request.method == 'POST':
		# 执行添加
		ob = Types() 
		ob.name = request.POST['name']
		ob.pid = request.POST['pid']
		if ob.pid == '0':
			# 顶级分类
			ob.path = '0,'
		else:
			# 根据当前父级id获取path，再添加当前父级id
			t = Types.objects.get(id=ob.pid)
			ob.path = t.path+str(ob.pid)+','
		ob.save()
		return HttpResponse('<script>alert("添加成功");location.href="'+reverse('myadmin_types_list')+'"</script>')
def index(request):
	tlist = gettypesorder()

	context = {'tlist':tlist}
	return render(request,'myadmin/types/list.html',context)
	

def delete(request):
	try:
		tid = request.GET.get('uid',None)

		# 判断当前类下是否有子类
		num = Types.objects.filter(pid = tid).count()

		if num != 0:
			data = {'msg':'当前下有子类，不能删除','code':1}
		else:
			# 判断当前类是否有商品
			ob = Types.objects.get(id=tid)
			
			ob.delete()

			data = {'msg':'删除成功','code':0}
	except:
		data = {'msg':'删除失败','code':1}

	return JsonResponse(data)

def edit(request):
	# 接受参数
	uid = request.GET.get('uid',None)
	if not uid:
		return HttpResponse('<script>alert("没有用户数据");location.href="'+reverse('myadmin_types_list')+'"</script>')

	# 获取对象
	ob = Types.objects.get(id=uid)

	if request.method == 'GET':

		# 分配数据
		context = {'uinfo':ob}
		# 显示编辑页面
		return render(request,'myadmin/types/edit.html',context)

	elif request.method == 'POST':

		try:
			ob.name = request.POST['name']
			ob.save()

			return HttpResponse('<script>alert("更新成功");location.href="'+reverse('myadmin_types_list')+'"</script>')
		except:
			return HttpResponse('<script>alert("更新失败");location.href="'+reverse('myadmin_types_edit')+'?uid='+str(ob.id)+'"</script>')





