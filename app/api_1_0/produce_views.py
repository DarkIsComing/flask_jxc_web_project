from flask import render_template, flash, redirect, url_for, request, jsonify
from . import api
from ..forms import AddMaterialForm, SearchForm, AttachForm, NumForm
from ..models import Material, StockIn, StockOut, InventoryFlow, MaterialType
from .. import db
import time
from datetime import datetime
from sqlalchemy import or_,and_
import json
from werkzeug import secure_filename
import os
import pandas as pd
import re
import urllib
import logging
from .utils import table_exists,connect_to_mysql


#检查该物料在物料表中是否存在      
@api.route('/check', methods=('GET', 'POST'))
def check():
    """
    描述:在上传了文件之后,点击‘全部检查’之后就会调用该路由并将该表格中的所有物料的存在状态显示在’状态‘一栏中。
        @param data: str类型, curd.html向/check发送ajax请求,data就是从前端接收到的包含表格中的所有元件和封装的字符串,
        输出样式为yj=FIDUCIAL&yj=FT232RLSSOP&yj=NCP1117-3.3T3 &id=0805&id=0805&id=0805
        @param lists: 输出样式为['yj=FT232RLSSOP', 'yj=NCP1117-3.3T3', 'id=0805', 'id=0805']
        @param yj: lists列表经过字符串处理的元件名:输出样式为['0805', '0805']
        @param ids:  lists列表经过字符串处理的封装名:输出样式为['0', '0.1UF']
        @param boolean: 将每个对应的yj与ids拿去匹配物料表，如果该条数据存在,则返回True,否则返回False.
    """
    data=request.get_data(as_text=True)     #str
    lists=data.split('&')
    yj=[]
    ids=[]
    boolean=[]
    for l in lists:
        if l.startswith('yj'):
            yj.append(l)
        if l.startswith('id'):
            ids.append(l)
    for i,item in enumerate(yj):
        yj[i]=yj[i][3:]
    for i,item in enumerate(ids):
        ids[i]=ids[i][3:]
    for i,j in zip(yj,ids):
        query_info=Material.query.filter(and_(Material.name==i,Material.package==j)).first()
        if query_info is None:
            boolean.append(False)
        else:
            boolean.append(True)
    return jsonify({'data': boolean})

#上传文件
@api.route('/upload', methods=('GET', 'POST'))
def upload():
    """
    描述:上传文件，对文件内部数据进行处理，获取里面的元件名和封装名两项数据，并且统计对应的数目
        @param form: 文件上传表单的实例
        @param files: 当按下提交键后，通过request对象上的files获取文件,根据form表单对应的名字upload_files获取。
        @function secure_filename: 防止用户上传文件导致的xss攻击。
        @param path:  os.path.abspath(__file__)获取当前目录的绝对路径，
        os.path.join(os.path.abspath(__file__),"../..")得到当前目录的上上一级的目录路径。
        path为mnt文件的项目路径。
        @param s: list列表,每一项是文件中读取的每一行的内容
        @param l: list列表,输出样式为[b'C1', b'8.89', b'5.08', b'0', b'100nf', b'OC-C0603']
        @param j: list列表,每一项是一个字典,输出样式为
        [{'贴装位': 'C1', '横坐标': '8.89', '纵坐标': '5.08', '角度': '0', '元件名': '100nf', '封装': 'OC-C0603'},
         {'贴装位': 'C2', '横坐标': '25.4', '纵坐标': '5.08', '角度': '180', '元件名': '100nf', '封装': 'OC-C0603'}]
        @param df: 将j转换成pandas的DataFrame格式。
                 元件名            封装    横坐标    纵坐标   角度  贴装位
                0      100nf      OC-C0603   8.89   5.08    0   C1
                1      100nf      OC-C0603   25.4   5.08  180   C2
        @param new_df: 只取df的元件名和封装两列
                新df:          元件名            封装
                0      100nf      OC-C0603
                1      100nf      OC-C0603
        @param new_dataframe: 按照new_df的元件名和封装两列分组获取统计的个数,reset_index给它添加列名‘counts'
                元件名       封装     counts     
                100nf     OC-C0603        3
                10K       OC-R0603        3
        @param yjm: 文件数据处理过后得到的元件名['100nf' '10K' 'DTSM-2' 'FIDUCIAL']
        @param fz: 文件数据处理过后得到的封装名['OC-C0603' 'OC-R0603' '' 'FIDUCIAL_1MM']
        @param count: 文件数据统计过后对应的数量[3 3 3 2]
    """
    form = AttachForm()
    if form.validate_on_submit():
        files= request.files['upload_files']
        filename = secure_filename(files.filename)
        path=os.path.abspath(os.path.join(os.path.abspath(__file__),"../.."))+"/mnt"
        files.save(os.path.join(path,filename))             #将上传的文件存到mnt文件夹里。
        j=[]
        with open(os.path.join(path,filename),'rb') as f:        #打开该文件
            s=f.readlines()
            for line in s:
                l=line.split()           
                if len(l) == 6:
                    j.append({'贴装位':bytes.decode(l[0],errors='ignore'),
                                '横坐标':bytes.decode(l[1],errors='ignore'),
                                '纵坐标':bytes.decode(l[2],errors='ignore'),
                                '角度':bytes.decode(l[3],errors='ignore'),
                                '元件名':bytes.decode(l[4],errors='ignore'),
                                '封装':bytes.decode(l[5],errors='ignore')})
                elif len(l) ==5:
                    j.append({'贴装位':bytes.decode(l[0],errors='ignore'),
                                '横坐标':bytes.decode(l[1],errors='ignore'),
                                '纵坐标':bytes.decode(l[2],errors='ignore'),
                                '角度':bytes.decode(l[3],errors='ignore'),
                                '元件名':bytes.decode(l[4],errors='ignore'),
                                '封装':''})
            df=pd.DataFrame(j)   
            new_df=df[['元件名','封装']]    
            data_frame=new_df.groupby(['元件名','封装']).size() 
            new_dataframe=data_frame.reset_index(name='counts')    
            yjm=new_dataframe['元件名'].values
            fz=new_dataframe['封装'].values
            count=new_dataframe['counts'].values       
            z=zip(yjm,fz,count)
            f.close()
        return render_template('curd.html',form=form,filename=filename,z=z)
    return render_template('curd.html',form=form)
            
#在上传文件后内部添加物料
@api.route('/addIn',methods=['GET','POST'])
def add_in():
    """
    描述:从type表中查询所有的物料类型,传入前端的物料类型<select>option中，使用户可以在添加物料的时候根据数据库中已有的物料类型进行添加
        @param names: type表中查询到的所有的物料类型
    """
    results = MaterialType.query.all()
    names=[]
    for result in results:
        names.append(result.type_name)
    return jsonify({'type':names})

#提交
@api.route('/submit',methods=['GET','POST'])
def submit():
    """
    描述:在准备点击添加物料提交按钮时，先判断该物料在物料表中是否存在，并且判断这三个数值是否有为空的。
    只有在物料不存在并且三个数值不为空的情况下才添加该物料到物料表中。
        @param yj: 要添加的物料的元件名
        @param fz: 要添加的物料的封装名
        @param types: 要添加的物料的物料类型
    """
    yj=request.values.get('yj') 
    fz=request.args.get('fz')
    types=request.args.get('types')
    old_material=Material.query.filter(
        and_(Material.name==yj,Material.package==fz)).first()
    if old_material:
        flash('该物料已经存在,请重新添加')
        return jsonify({'msg':'exists'})
    else:
        if yj.strip()=='' or fz.strip()=='' or types.strip()=='':
            return jsonify({'msg':'failed'})
    material=Material()
    material.name=yj
    material.package=fz
    material.types=types
    material.stock=0
    db.session.add(material)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('新的物料添加失败。')
        return jsonify({'msg':'failed'})
    flash('新的物料添加成功。')
    return jsonify({'msg':'succeed'})


#保存
@api.route('/save',methods=['GET','POST'])
def save():
    """
    描述:点击‘全部保存’之后将表格中所有的数据以csv的格式保存在app/csv目录下。
        @param data: str类型, curd.html向/save发送ajax请求,data就是从前端接收到的包含表格中的所有元件和封装的字符串,
        输出样式为yj=FIDUCIAL&yj=FT232RLSSOP&yj=NCP1117-3.3T3 &id=0805&id=0805&id=0805
        @param lists: 输出样式为['yj=FT232RLSSOP', 'yj=NCP1117-3.3T3', 'id=0805', 'id=0805']
        @function urllib.request.unquote():将带百分号的ascii编码恢复成utf-8的字符形式。
        example:print(urllib.request.unquote(http://www.qianmu.org/%E6%B9%96%E9%A6%96%E5%A4%A7%E5%AD%A6))
        >>>http://www.qianmu.org/湖首大学
        @param yj: lists列表经过字符串处理的元件名:输出样式为['0805', '0805']
        @param ids:  lists列表经过字符串处理的封装名:输出样式为['0', '0.1UF']
        @param number: 对应的数量:输出样式为[3, 2]
    """
    #as_text=True 将原始数据格式bytes转换成Unicode了
    data=request.get_data(as_text=True)         #id=1206&id=FIDUCIAL_1MM&id=DIO4148-0805&id=SOT-23&id=SOT223&id=SSOP28DB&id=SOT323-5L&id=CRYSTAL-3.2-2.5&id=TQFP100&num=13&num=2&num=1&num=1&num=1&num=1&num=1&num=1&num=1 <class 'str'>
    lists=data.split('&')
    yj=[]
    ids=[]
    number=[]
    filename='noname'
    for l in lists:
        if l.startswith('yj'):
            yj.append(l)
        if l.startswith('id'):
            ids.append(l)
        if l.startswith('num'):
            number.append(l)
        if l.startswith('filename'):
            filename=l[9:].split('.')[0]
    filename=urllib.request.unquote(filename)           #解决上传的文件名中有中文导致的ASCII码格式而不是utf-8格式
    for i,item in enumerate(yj):
        yj[i]=yj[i][3:]
    for i,item in enumerate(ids):
        ids[i]=ids[i][3:]
    for i,item in enumerate(number):
        number[i]=number[i][4:]
    df=pd.DataFrame({"元件名":yj,"封装名称":ids,"数量":number})
    if filename !='noname' and filename !='':
        path=os.path.abspath(os.path.join(os.path.abspath(__file__),"../.."))+"/csv/"
        df.to_csv(path+filename+".csv",index=False,sep=',')
        return jsonify({'data': 'success'})
    return jsonify({'data': 'fail'})
    
#生产表中单物料生产出库
@api.route('/AdjustInventory',methods=['GET','POST'])
def adjust_inventory():  
    """
    描述:生产表中单物料生产出库,修改物料表中的库存数量，并且添加库存流水记录。
        @param s: 要修改的数量,正数则加,负数则减
        @param path: 保存的csv路径
        @param name: 打开的csv的文件名称
        @param single_yj: 该物料的元件名
        @param single_fz: 该物料的封装名
    """
    s=int(request.args.get('s'))
    path=request.args.get('path')       #保存的csv路径
    name=request.args.get('name')       #打开的csv的文件名称
    single_yj=request.args.get('yj')
    single_fz=request.args.get('fz')
    query_info=Material.query.filter(and_(Material.name==single_yj,Material.package==single_fz)).first()
    if query_info:
        if query_info.stock >=s:
            query_info.stock=int(query_info.stock)-s
        else:
            query_info.stock=int(query_info.stock)-s
            flash('入库成功,但是库存已经为负')
    #库存流水表
        inventory_flow=InventoryFlow()
        inventory_flow.name=single_yj
        inventory_flow.package=single_fz
        inventory_flow.ID= query_info.ID
        inventory_flow.date= datetime.now()
        inventory_flow.types='product'
        inventory_flow.occurred_amount=-s
        inventory_flow.stock=query_info.stock
        db.session.add(inventory_flow)
        try:
            db.session.commit()
            flash('修改库存成功')
        except:
            db.session.rollback()
            flash('修改库存失败')
    else:
        flash('该物料不存在')
    return redirect(url_for('api_1_0.opencsv',single_yj=single_yj,single_fz=single_fz,name=name,path=path))

#生产表中单物料修改总数
@api.route('/changeSum',methods=['GET','POST'])
def change_sum():  
    """
    描述:生产表中单物料修改总数,修改物料表中的库存数量，并且添加库存流水记录。并且修改csv中的数量。
        @param source_file: 资源路径
        @param path: 保存的csv路径
        @param name: 打开的csv的文件名称
        @param sums: 生产块数*生产表中该物料生产所需的物料数量
        @param num: 修改的数量,正则加负则减
        @param yj: 该物料的元件名
        @param fz: 该物料的封装名
    """
    path=request.args.get('path')       #保存的csv路径
    name=request.args.get('name')       #打开的csv的文件名称
    source_file=path+'/'+name           #资源路径
    sums=request.args.get('sums')
    num=request.args.get('num')       
    yj=request.args.get('yj')
    fz=request.args.get('fz')
    df=pd.read_csv(source_file)
    num=int(num)
    if yj and fz is not None:
        if not df.loc[(df['元件名']==yj)&(df['封装名称']==fz),'总数'].empty:
            df.loc[(df['元件名']==yj)&(df['封装名称']==fz),'总数']+=num
            df.to_csv(source_file,index=False,sep=',')
            flash('修改成功')
            return jsonify({'change':'succeed'})
        else:
            flash('修改失败')
            return jsonify({'change':'failed'})
    else:
        return jsonify({'change':'failed'}) 



 #一键出库   
@api.route('/produceAll',methods=['GET','POST'])          
def produce_all():
    """
    描述:生产表中点击一键出库,对表格中的每一行都进行出库操作。成功则显示success，失败显示failed
        @param source_file: 资源路径
        @param path: 保存的csv路径
        @param name: 打开的csv的文件名称
        @param yj: ['100nf' '10K' 'DTSM-2' 'FIDUCIAL']
        @param fz: ['OC-C0603' 'OC-R0603' None 'FIDUCIAL_1MM']
        @param sums: [60 60 60 40]
    """
    msg={}
    path=request.args.get('path')       #保存的csv路径
    name=request.args.get('name')       #打开的csv的文件名称
    source_file=path+'/'+name           #资源路径
    df=pd.read_csv(source_file)
    df = df.astype(object).where(pd.notnull(df), None)      #如果csv中某个值为空，则把它设置为None
    yj=df['元件名'].values          #<class 'numpy.ndarray'>
    fz=df['封装名称'].values        #<class 'numpy.ndarray'>
    if '总数' not in df.columns:
        df['总数']=0    
        df.to_csv(source_file,index=False,sep=',')  
    sums=df['总数'].values
    for i,(y,f,s) in enumerate(zip(yj,fz,sums)):
        query_info=Material.query.filter(and_(Material.name==y,Material.package==f)).first()
        s=int(s)
        if query_info:
            query_info.stock=int(query_info.stock)-s
            inventory_flow=InventoryFlow()
            inventory_flow.name=y
            inventory_flow.package=f
            inventory_flow.ID= query_info.ID
            inventory_flow.date= datetime.now()
            inventory_flow.types='product'
            inventory_flow.occurred_amount=-s
            inventory_flow.stock=query_info.stock
            db.session.add(inventory_flow)
            try:
                db.session.commit()
                msg[i]='succeed'
            except:
                db.session.rollback()
                msg[i]='failed'  
        else:
            msg[i]='failed'
    return jsonify(msg)

@api.route('/opencsv',methods=['GET','POST'])          
def opencsv():
    """
    描述:生产表中点击一键出库,对表格中的每一行都进行出库操作。成功则显示success，失败显示failed
        @param source_file: 资源路径
        @param path: 保存的csv路径
        @param name: 打开的csv的文件名称
        @param yj: ['100nf' '10K' 'DTSM-2' 'FIDUCIAL']
        @param fz: ['OC-C0603' 'OC-R0603' None 'FIDUCIAL_1MM']
        @param num: [60 60 60 40]
        @param difference: 库存数量-生产总量
        @param material_stock: 库存数量
        @param block_num: 生产块数
        @param states: 一键出库是否成功。成功则显示success，失败显示failed
    """   
    path=request.args.get('path')       #保存的csv路径
    name=request.args.get('name')       #打开的csv的文件名称
    source_file=path+'/'+name           #资源路径
    df=pd.read_csv(source_file)
    df = df.astype(object).where(pd.notnull(df), None)
    yj=df['元件名'].values          #<class 'numpy.ndarray'>
    fz=df['封装名称'].values        #<class 'numpy.ndarray'>
    num=df['数量'].values           #<class 'numpy.ndarray'>
    difference=[]
    material_stock=[]
    for i,j in zip(yj,fz):
        sql_query=Material.query.filter(and_(Material.name==i,Material.package==j)).first()
        if sql_query:
            if sql_query.stock is None:
                material_stock.append(0)
            else:
                material_stock.append(sql_query.stock)
        else:
            material_stock.append('')
    if '总数' not in df.columns:
        df['总数']=0    
        df.to_csv(source_file,index=False,sep=',')  
    sum_number=list(df['总数'].values)
    for n,s in zip(sum_number,material_stock):
        if s=='':
            difference.append('')
        else:
            difference.append(int(s)-n)
    form=NumForm()
    if form.validate_on_submit():
        difference=[]
        df['总数']=0
        block_num=form.num.data             #生产块数
        df['总数']=df['数量'].map(lambda x:x*int(block_num))
        df.to_csv(source_file,index=False,sep=',')
        sum_number=df['总数'].values
        sums=list(sum_number)
        for n,s in zip(sums,material_stock):
            if s=='':
                difference.append('')
            else:
                difference.append(int(s)-n)
    z=zip(yj,fz,num,sum_number,material_stock,difference)
    states=None
    if request.args.get('d'):
        d=request.args.get('d')
        state=json.loads(d)     #dict
        states=[]
        for v in state.values():
            states.append(v)
        z=zip(yj,fz,num,sum_number,material_stock,difference,states)
    return render_template('opencsv.html',z=z,form=form,name=name,
                            path=path,difference=difference,states=states)
   
          

# 模糊匹配元件名
@api.route('/data_yj',methods=['GET','POST'])
def get_yj():
    """
    描述:上传文件页面的新增数据模块处,当用户想要修改元件名或者新增元件名时，
    删掉你要修改的元件名的数据,再输入你要找的元件名的任意一个字母，就会从物料表中匹配可能的元件名
        @param results: 物料表中元件名属性所有和输入数据匹配的数据
        @param search: 用户输入的搜索数据
    """   
    results=[]
    search=request.args.get('q_yj')
    query=Material.query.filter(Material.name.like('%'+str(search)+'%')).all()
    for item in query:
        results.append(item.name)
    return jsonify(result=results)

# 获取数据fz
@api.route('/data_fz',methods=['GET','POST'])
def get_fz():
    """
    描述:上传文件页面的新增数据模块处,当用户想要修改封装名或者新增封装名时，
    删掉你要修改的封装名的数据,再输入你要找的封装名的任意一个字母，就会从物料表中匹配可能的封装名
        @param results: 物料表中封装名属性所有和输入数据匹配的数据
        @param search: 用户输入的搜索数据
    """   
    results=[]
    search=request.args.get('q_fz')
    query=Material.query.filter(Material.package.like('%'+str(search)+'%')).all()
    for item in query:
        results.append(item.package)
    return jsonify(result=results)

        
    

# 显示csv
@api.route('/csv',methods=['GET','POST'])
def csv():
    """
    描述:显示path路径下的所有csv文件
        @param files: path文件夹下的所有文件名称
        @param form: 搜索框，根据输入内容搜索该路径下的所有匹配的csv文件。
        @param suggestions: 所有与正则表达式定义的规则匹配的项的列表。
    """   
    path=os.path.abspath(os.path.join(os.path.abspath(__file__),"../.."))+"/csv"
    files= os.listdir(path) #得到文件夹下的所有文件名称
    form=SearchForm()
    if form.validate_on_submit():
        words=form.name.data    
        suggestions = []
        pattern = '.*'.join(words) # Converts 'djm' to 'd.*j.*m'   
        regex = re.compile(pattern)     # Compiles a regex.
        for item in files:              #遍历该文件夹查看是否有符合该正则表达式的项在，加入到suggestions中。
            match = regex.search(item.split('.')[0])  # Checks if the current item matches the regex.
            if match:
                suggestions.append(item)
        return render_template("csv.html",suggestions=suggestions,form=form,path=path)
    return render_template("csv.html",files=files,path=path,form=form)

