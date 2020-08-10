from django.shortcuts import HttpResponse, render
from dao.blogclassdao import BlogClassDao
from dbmodels.models import TBlog, TBlogclass,TUser
import json
# Create your views here.

def goBlogClass(request):
    return render(request, 'admin/blog/blogclass.html')
    pass

def getBlogClass(request):
    dictObj = json.loads(request.body.decode('utf-8'),strict=False)
    print("11111")
    print(dictObj)

    # 获取查询条件
    className = dictObj.get('className', '')
    classState = dictObj.get('classState', '')
    classId = dictObj.get('classId', '')
    opr = dictObj.get('opr', '')
    pageSize = dictObj.get('pageSize', 0)
    currentPage = dictObj.get('currentPage', 0)

    if pageSize == 0 or pageSize == "":
        pageSize = 3
        pass
    if currentPage == 0 or currentPage == "":
        currentPage = 1
        pass

    classDao = BlogClassDao()

    params = {'className': className,
              'classState': classState,
              'pageSize': int(pageSize),
              'currentPage': int(currentPage)}

    if opr == 'delClass':
        result = classDao.removeClass([classId])
        params['result'] = result
        pass

    if opr == 'update':
        uClass = classDao.findClassByClassId([classId])
        return HttpResponse(json.dumps({'params': params, 'uClass': uClass}), content_type='application/json')
        pass

    # 提交修改用户的个人信息
    if opr == 'submitUpdate':
        uName = dictObj.get('uName', '')
        result = classDao.updateClass([uName, classId])
        #点击保存只显示修改的单条信息
        #params['className']=uName
        pass

    if opr == 'add':
        aName = dictObj.get('aName', '')
        print(aName)
        result = classDao.createClass([aName])
        classDao.commit()
        pass

    counts = classDao.findClassCounts(params)
    totalPage = counts // int(pageSize) if counts % int(pageSize) == 0 else counts // int(pageSize) + 1
    print(totalPage)
    params['counts'] = counts
    params['totalPage'] = totalPage
    currentPage = int(currentPage) if int(currentPage) < totalPage else totalPage
    currentPage = 1 if currentPage <= 0 else currentPage
    params['currentPage'] = currentPage
    # 计算两个值：startRow
    startRow = (int(currentPage) - 1) * int(pageSize)
    params['startRow'] = startRow
    classList = classDao.findPageClassList(params)
    classDao.close()

    return HttpResponse(json.dumps({'data': classList, 'params': params},ensure_ascii=False), content_type='application/json')
    pass


# 博客管理
def goBlogList(request):
    return render(request, 'admin/blog/blog.html')
    pass
# AJAX异步技术实现CRUD
def blogList(request):
    dictObj = json.loads(request.body.decode('utf-8')) # {'classid':1, 'className': 'Python', 'opr':'del'}


    # 获取查询条件
    blogTitle = dictObj.get('blogTitle', '')
    blogState = dictObj.get('blogState', '')
    blogContent = dictObj.get('blogContent', '')
    blogTips = dictObj.get('blogTips', '')
    blogClassId = dictObj.get('blogClassId', '')
    blogId = dictObj.get('blogId', '')
    opr = dictObj.get('opr', '')
    pageSize = dictObj.get('pageSize', 0)
    currentPage = dictObj.get('currentPage', 0)

    if pageSize == 0 or pageSize == "":
        pageSize = 3
        pass
    if currentPage == 0 or currentPage == "":
        currentPage = 1
        pass

    tBlog = TBlog()
    blogClassDao = BlogClassDao()
    blogClassList = blogClassDao.findAllClassList()

    params = {'blogTitle': blogTitle,
              'blogState': blogState,
              'pageSize': int(pageSize),
              'currentPage': int(currentPage),
              'blogClassList': blogClassList}
    if opr == 'publish' or opr == 'cancel':
        result = TBlog.objects.filter(blogid=blogId).update(blogstate=blogState)
        pass
    # ORM实现删除功能
    if opr == 'delClass':
        tBlog.blogid = blogId    # 将id赋值为tBlog模型对象
        result = tBlog.delete()  #  delete from t_blog where blogid=blogId
        params['result'] = result
        pass
    # 查询博客信息
    if opr == 'update':
        uBlog = TBlog.objects.filter(blogid=blogId).values('blogid', 'blogtitle', 'blogcontent', 'blogtips')
        # select blogid, blogtitle, blogcontent, blogtips from t_blog where blogid=1
        return HttpResponse(json.dumps({'params': params, 'uBlog': uBlog[0]}), content_type='application/json')
        pass

    if opr == 'submitUpdate':
        tBlogclass = TBlogclass()
        tBlogclass.classid = int(blogClassId)

        # 摘要信息
        blogsummary = blogContent[0:300].replace('<p>', '')
        blogsummary = blogsummary.replace('</p>', '')

        result = TBlog.objects.filter(blogid=blogId).update(blogtitle=blogTitle,
                                                            blogcontent=blogContent,
                                                            blogtips=blogTips,
                                                            blogsummary=blogsummary,
                                                            classid=tBlogclass,
                                                            blogstate=blogState)
        if result:
            return HttpResponse(json.dumps({'result': 1}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'result': 0}), content_type='application/json')
            pass

        pass

    # if opr == 'add':
    #     aName = dictObj.get('aName', '')
    #     result = TBlog.objects.create(blogtitle=blogTitle, blogstate=blogState)
    #     pass
    if opr == 'goAdd':
        return HttpResponse(json.dumps({'params': params}), content_type='application/json')
        pass
    if opr == 'add':
        # 是类别信息
        tBlogclass = TBlogclass()
        tBlogclass.classid = int(blogClassId)

        # 摘要信息
        blogsummary = blogContent[0:300].replace('<p>', '')
        blogsummary = blogsummary.replace('</p>', '')

        # 用户信息
        print(request.session['user'])
        tUser = TUser()
        sessionUser = request.session['user']
        tUser.userid = sessionUser['userId']

        print(blogContent)
        # ORM框架的外键列必须传对象
        result = TBlog.objects.create(blogtitle=blogTitle,
                                      blogcontent=blogContent,
                                      blogtips=blogTips,
                                      blogsummary=blogsummary,
                                      classid=tBlogclass,
                                      userid=tUser,
                                      blogstate=blogState)
        if result:
            return HttpResponse(json.dumps({'result': 1}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({'result': 0}), content_type='application/json')
            pass
        pass

    # 计算两个值：startRow
    startRow = (int(currentPage) - 1) * int(pageSize)
    endRow = int(currentPage) * int(pageSize)
    params['startRow'] = startRow

    counts=None
    blogList=[]
    querySet = TBlog.objects
    if blogTitle and blogState:
        print(blogTitle)
        # blogtitle__contains 模糊查询
        blogList = list(querySet.filter(blogtitle__contains=blogTitle,blogstate=blogState).values('blogid',
                                    'blogtitle',
                                    'blogsummary',
                                    'blogtips',
                                    'userid__username',
                                    'classid__classname',
                                    'blogstate')[startRow: endRow])
        counts = querySet.count()
        pass
    elif blogState:
        blogList = list(querySet.filter(blogstate=blogState).values('blogid',
                                    'blogtitle',
                                    'blogsummary',
                                    'blogtips',
                                    'userid__username',
                                    'classid__classname',
                                    'blogstate')[startRow: endRow])
        counts = querySet.count()
        pass
    else:
        blogList = list(querySet.filter(blogtitle__contains=blogTitle).values('blogid',
                                    'blogtitle',
                                    'blogsummary',
                                    'blogtips',
                                    'userid__username',
                                    'classid__classname',
                                    'blogstate')[startRow: endRow])
        counts = querySet.count()
        pass


    totalPage = counts // int(pageSize) if counts % int(pageSize) == 0 else counts // int(pageSize) + 1
    params['counts'] = counts
    params['totalPage'] = totalPage
    currentPage = int(currentPage) if int(currentPage)<totalPage else totalPage
    currentPage = 1 if currentPage <= 0 else currentPage
    params['currentPage'] = currentPage


    return HttpResponse(json.dumps({'data': blogList, 'params': params}), content_type='application/json')
    pass

#写博客页面
def goWriteBlog(request):
    return render(request, 'admin/blog/writeblog.html')
    pass

def goUpdateBlog(request):
    blogId = request.GET.get('blogId', 0)
    params = {}
    params['blogId'] = blogId
    return render(request, 'admin/blog/updateblog.html', {'params': params})
    pass

import os
import uuid
# 文件上传功能
def uploadFile(request):
    # 后缀需要检查的
    file = request.FILES.get('upload')
    if file:
        fileName = str(uuid.uuid4()) +  file.name # 避免文件名称冲突
        try:
            with open(os.path.dirname(__file__) + os.sep + '..' + os.sep + 'static' + os.sep + 'upload'+ os.sep + fileName, "wb+") as fp:
                for chunk in file.chunks():
                    fp.write(chunk)
                    pass
        except Exception as e:
            return HttpResponse(json.dumps({'uploaded': 0, 'fileName': "", 'url': ""}), content_type="application/json")
            pass
        return  HttpResponse(json.dumps({'uploaded': 1, 'fileName':fileName, 'url': os.sep + 'static' + os.sep + 'upload'+ os.sep + fileName}), content_type="application/json")
    else:
        return  HttpResponse(json.dumps({'uploaded': 0, 'fileName': "", 'url': ""}), content_type="application/json")
    pass




