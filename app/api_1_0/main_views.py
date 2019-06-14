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

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename="output.log",encoding='utf-8')
logger.setLevel(logging.DEBUG)
console_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

#home起始页
@api.route('/',methods=['GET'])
def home():
    return redirect(url_for('api_1_0.index'))           #直接跳转到首页index

#首页
@api.route('/index',methods=['GET','POST'])
def index():
    """
    描述:实例化搜索框表单,如果点击了提交按钮,则跳转到api_1_0.search_material_list所在的路由。
        @type words: string
        @param words: 从搜索表单中获取的用户输入的参数。
    """
    form=SearchForm()                                   
    if form.validate_on_submit():                      
        words=form.name.data      
        return redirect(url_for('api_1_0.search_material_list',words=words))        
    return render_template('index.html',form=form)
        
        
#search列表
@api.route('/search', methods=['GET','POST'])
def search_material_list():
    """
    描述:接收index视图传递过来的参数,与数据库进行匹配,将搜索到的结果按分页条数返回给html页面。
        @type receive_words: string
        @param receive_words: 从搜索表单中获取的用户输入的参数。

        @type page_data: flask_sqlalchemy.Pagination
        @param page_data: Pagination格式的搜索结果,可以根据元件名或者封装名来进行搜索。(不区分大小写)
    """
    receive_words=request.args.get('words')
    words=receive_words.strip()
    logger.info('搜索了单词 %s',words)
    try:
        page = int(request.args.get('page') or 1)
    except (ValueError,TypeError) as e:
        logger.exception(e)
    except Exception as e:
        logger.exception('未知错误:',e)
    page_data=Material.query.filter(or_(Material.name.like("%" + words + "%"),
                            Material.package.like("%" + words + "%")
                            )).paginate(page, 20, False)
    return render_template("search_materials_result.html",page_data=page_data,words=words,page=page)
    
 
#添加物料类型表
@api.route('/addMaterialAttribute',methods=['GET','POST'])
def add_material_attribute():
    """
    描述:根据用户输入的物料类型名称 在数据库中添加同名的物料类型表,并且在添加物料页面的物料类型选项中会加上添加过的物料类型。
    比如用户在添加物料类型表中输入了‘电阻’,那么就会在数据库中添加一个叫做电阻的表，并且物料类型选项中会出现‘电阻’类型。
    如果‘电阻’类型在type表中不存在,那么会在type表中添加一条‘电阻’的记录。

        @type name: string
        @param name: 用户输入的物料类型表的名称。

        @function connect_to_mysql :连接MySQL数据库
        @function table_exists :判断输入的表的名称在数据库的表中是否存在。返回true or false

        @type attr: str
        @param attr: 从type表中搜索是否存在与用户输入的类型名称相同的记录，如果不存在则添加记录,存在则不添加返回。
    """
    name=request.args.get('attr')
    con=connect_to_mysql()
    cursor=con.cursor()
    d={}
    if table_exists(cursor,name) is False:
        try:                           
            cursor.execute("create table %s (ids integer AUTO_INCREMENT,ID integer,primary key(ids),FOREIGN KEY (ID) REFERENCES materials(ID))"%name)     
            flash('类型表添加成功')  
            d['table']='succeed' 
        except:
            flash('类型表添加失败')
            d['table']='failed' 
    cursor.execute("SELECT type_name FROM type WHERE type_name='%s'"%name)
    attr=cursor.fetchone()
    #print('属性内容：',attr)
    if attr is None:
        try:
            cursor.execute("INSERT INTO type (type_name) VALUES ('%s')"%name)       
            flash('表格记录添加成功') 
            d['record']='succeed' 
        except:
            flash('表格记录添加失败')  
            d['record']='failed'
    else:
        flash('该类型已经存在！')
        d['state']='exists'
    con.commit()
    cursor.close()
    con.close()
    return jsonify(d)
    
    
#添加物料
@api.route('/addMaterials',methods=['GET','POST'])
def add_material():
    """
    描述:从type表中查询所有记录的类型的数据并放入names列表中,遍历这个列表，将其中的属性添加到form.material_type.choices中,
    这样就能在页面的物料类型form表单下拉框中显示出所有数据库中已添加的物料类型。接着如果用户点击了提交按钮，先判断用户输入的
    物料名称和封装名称在数据库中是否存在，如果不存在则添加成功，存在则返回重新添加。

        @type names: list
        @param names: type表中所有的物料类型。
        @param material: flask_sqlalchemy实例化Material模型类,可以直接获取该表的所有属性。
    """
    form=AddMaterialForm()
    results = MaterialType.query.all()
    names=[]
    for result in results:
        names.append(result.type_name)
    form.material_type.choices += [(name,name) for name in names]
    if form.validate_on_submit():
        old_material=Material.query.filter(and_(
            Material.name==form.material_name.data,
            Material.package==form.material_package.data)).first()
        if old_material:
            flash('该物料已经存在,请重新添加')
            return redirect(url_for('api_1_0.add_material'))
        material=Material()
        material.name=form.material_name.data
        material.package=form.material_package.data
        material.types=form.material_type.data      #'' str
        material.stock=0
        if material.types=='':
            return redirect(url_for('api_1_0.add_material'))
            flash('物料类型不许为空。')
        db.session.add(material)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash('新的物料添加失败。')
        #flash('新的物料添加成功。')
        return redirect(url_for('api_1_0.material_list'))
    return render_template("add_material.html",form=form)

#物料属性展示
@api.route('/showAttr',methods=['GET','POST'])
def show_attr():
    """
        描述:根据该行的物料属性值查询数据库物料类型表(比如电阻表)中的所有属性,并传给前端显示出来。
        
        @param ID: 物料ID
        @param yj: 物料元件名
        @param fz: 物料封装名
        @param mtype: 物料类型
        @param col1: 查询该物料类型表中所有的列属性信息
        @param value_dict: 这张物料类型表(比如电阻表)中所有的列名组成的列表
        @param value: 这张物料类型表(比如电阻表)中所有的物料id+属性组成的列表，将value传给前端。
    """
    ID=request.values.get('ID')
    yj=request.args.get('yj')
    fz=request.args.get('fz')
    mtype=request.values.get('mtype')
    con=connect_to_mysql()
    cursor=con.cursor()
    if table_exists(cursor,mtype) is True:
        cursor.execute("select * from %s where ID=%s"%(mtype,ID))
        col1=cursor.description
        data_dict=[]                #这张表中所有的列名组成的列表
        for field in col1:
            if field[0] !='ID':
                data_dict.append(field[0])
        #print(data_dict)
        value_dict=[]
        val=cursor.fetchone()   #元组    
        print(val)              
        if val:
            value=list(val[1:])
        else:
            value=None
        con.commit()
        cursor.close()
        con.close()
        return render_template('show_attr.html',data_dict=data_dict,value=value,fz=fz,yj=yj,ID=ID,mtype=mtype)
    else:
        con.commit()
        cursor.close()
        con.close()
        #flash('表格不存在,请先添加表')
    return render_template('show_attr.html',fz=fz,yj=yj,ID=ID,mtype=mtype)

#添加物料属性
@api.route('/addAttr',methods=['GET','POST'])
def add_attr():
    """
        描述:首先判断该物料类型表是否存在,如果存在的话,接着查询物料类型表中该物料ID对应的记录。
        在该记录不存在的条件下,如果需要添加的属性不在该物料类型表的属性当中,那么先往该物料类型表中添加这条属性，再插入一条该属性值对应的记录。
        如果属性已经存在，则直接插入一条记录。 
        在该记录存在的条件下，如果添加的属性在该物料类型表中存在,那么更新该属性值对应的记录。
        如果属性不存在,那么先添加属性再添加记录。
        @param ID: 物料ID
        @param attribute: 物料属性名称
        @param value: 物料属性值
        @param yj: 元件名称
        @param fz: 封装名称
        @param mtype: 物料类型
        @param query_info: 查询物料类型表(比如电阻表)中该物料ID对应的记录
        @param data_dict: 该表列名集合
    """
    ID=request.args.get('ids')
    attribute=request.args.get('attr')
    value=request.args.get('value')
    yj=request.args.get('yj')
    fz=request.args.get('fz')
    mtype=request.args.get('types')
    con=connect_to_mysql()
    cursor=con.cursor()
    if table_exists(cursor,mtype) is True:         #如果该物料类型表存在
        cursor.execute("SELECT ID FROM %s WHERE ID=%s"%(mtype,ID))         #查询物料类型表中该物料ID对应的记录
        query_info=cursor.fetchone()
        cursor.execute("select * from %s where ID=%s"%(mtype,ID))
        col=cursor.description
        data_dict=[]
        for field in col:
            data_dict.append(field[0])        #该表列名集合
        if query_info is None:                  #如果该记录不存在
            if attribute not in data_dict:
                cursor.execute("ALTER TABLE %s ADD %s varchar(32)"%(mtype,attribute))         #在mtype表中添加attribute属性
            cursor.execute("INSERT INTO %s (ID,%s) VALUES ('%s','%s')"%(mtype,attribute,ID,value))       #在mtype表中插入一条记录为ID和attribute的值        
            flash('添加成功')
        else:                   #如果有和该物料ID匹配的一条数据存在
            if attribute in data_dict:          #如果该属性名在物料类型表的属性中已经存在,则更新该条记录
                cursor.execute("UPDATE %s set %s='%s',ID='%s' where ID='%s'"%(mtype,attribute,value,ID,ID))                   
                flash('更新成功')
            else:       #否则添加属性并且更新记录
                cursor.execute("ALTER TABLE %s ADD %s varchar(32)"%(mtype,attribute))          
                cursor.execute("UPDATE %s set %s='%s',ID='%s' where ID='%s'"%(mtype,attribute,value,ID,ID))                                 
                flash('添加成功')
        con.commit()
        cursor.close()
        con.close()
        return jsonify({'msg':'succeed'})
    else:
        con.commit()
        cursor.close()
        con.close()
        flash('表格不存在,请先添加表')
        return jsonify({'msg':'failed'})

#添加备注
@api.route('/addRemark',methods=['GET','POST'])
def add_remark():
    """
        描述:根据物料ID查询物料表,如果该条记录存在，则更新备注属性的值。
        @param ID: 物料ID
        @param remark: 用户输入的备注信息
        @param query_info: 物料表中与物料ID对应的一条记录
    """
    ID=request.args.get('ids')
    remark=request.args.get('remark')
    query_info=Material.query.filter(Material.ID==ID).first()
    if query_info:
        query_info.remark=remark
    try:
        db.session.commit()
        flash('添加备注成功')
        return jsonify({'msg':'succeed'})
    except:
        db.session.rollback()
        flash('添加备注失败')
        return jsonify({'msg':'failed'})

#显示物料列表
@api.route('/materialList', methods=['GET','POST'])
def material_list():
    """
        描述:分页显示物料列表
        @param page: 当前所在的页数,默认为1
        @param page_data: pagination对象,第一个参数表示当前页,第二个参数代表每页显示的数量,
        第三个参数error_out=True的情况下如果指定页没有内容将出现404错误,False则返回空的列表
    """
    page = int(request.args.get('page') or 1)
    page_data=Material.query.paginate(page, 20, False)
    return render_template("material_list.html",page=page,page_data=page_data)

#删除物料
@api.route('/del',methods=['GET','POST'])
def delete_material():
    words=None
    page=request.args.get('page')
    if request.args.get('words'):
        words=request.args.get('words')
        
    ids=request.args.get('ID')
    del_material=Material.query.filter(Material.ID==ids).first()  
    try:
        db.session.delete(del_material)
        db.session.commit()
        flash('删除成功')
    except:
        db.session.rollback()
        flash('删除失败')
    
    if words is not None:
        return redirect(url_for('api_1_0.search_material_list',words=words,page=page))
    return redirect(url_for('api_1_0.material_list',page=page))


#出货单列表
@api.route('/saleList', methods=['GET','POST'])
def sale_list():
    """
        描述:分页显示出货单列表
        @param page: 当前所在的页数,默认为1
        @param page_data: pagination对象,第一个参数表示当前页,第二个参数代表每页显示的数量,
        第三个参数error_out=True的情况下如果指定页没有内容将出现404错误,False则返回空的列表
    """
    page = int(request.args.get('page') or 1)
    page_data=StockOut.query.paginate(page, 20, False)
    if page_data is None:
        flash('出货表为空')
    return render_template("show_sale_order.html",page_data=page_data)

#进货单列表
@api.route('/buyList', methods=['GET','POST'])
def buy_list():
    """
        描述:分页显示进货单列表
        @param page: 当前所在的页数,默认为1
        @param page_data: pagination对象,第一个参数表示当前页,第二个参数代表每页显示的数量,
        第三个参数error_out=True的情况下如果指定页没有内容将出现404错误,False则返回空的列表
    """
    page = int(request.args.get('page') or 1)
    page_data=StockIn.query.paginate(page, 20, False)
    if page_data is None:
        flash('进货表为空')
    return render_template("show_buy_order.html",page_data=page_data)
    

#进货
@api.route('/buy',methods=['GET','POST'])
def buy():
    """
        描述:进货，根据进货数量对库存进行更新,并将数据记录到入库表和库存流水表。
        @param ids: 物料ID
        @param num: 购买数量
        @param price: 购买价格
        @param query_info: 物料表中物料ID等于当前行的物料的物料ID的第一条数据。
        @param new_order: 入库单模型类实例
        @param inventory_flow: 库存流水单模型类实例
    """
    ids=request.args.get('ids') 
    num=request.args.get('num')
    price=request.args.get('price')
    query_info=Material.query.filter(Material.ID==ids).first()      #查询物料表中属性物料ID等于进货单中进货的物料的物料ID的第一条数据。
    new_order= StockIn()
    new_order.ID= query_info.ID
    new_order.name= query_info.name
    new_order.package= query_info.package
    new_order.number= num
    new_order.price= price
    new_order.date= datetime.now()
    try:
        if query_info:        #如果该条数据存在
            material_inventory_num= query_info.stock        #物料库存数量=查询所得到的库存数量
            if material_inventory_num is None:      #如果该物料库存数量为空，则赋值为0
                material_inventory_num=0            
            material_inventory_num+= int(new_order.number)      #该物料库存数量加上新的进货单的进货数量
            query_info.stock=material_inventory_num    #更新库存表中该物料的库存数量
        else:
            flash('ERROR,该物料ID与数据库中无匹配项')
    except Exception as e:
        logger.info('buy error:',e)

    #库存流水表
    inventory_flow=InventoryFlow()
    inventory_flow.name=new_order.name
    inventory_flow.package=new_order.package
    inventory_flow.ID= new_order.ID
    inventory_flow.price= new_order.price
    inventory_flow.date= new_order.date
    inventory_flow.types='in'
    inventory_flow.occurred_amount=(+int(new_order.number))
    inventory_flow.stock=material_inventory_num

    db.session.add(new_order)
    db.session.add(inventory_flow)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.info('sql rollback error:',e)
        flash('新的购货记录添加失败。')
    flash('新的购货记录添加成功。')
    return redirect(url_for('api_1_0.material_list'))
    


#出货表
@api.route('/sale',methods=["GET",'POST'])
def sale():
    """
        描述:进货，根据进货数量对库存进行更新,并将数据记录到入库表和库存流水表。
        @param ids: 物料ID
        @param num: 销售数量
        @param price: 销售价格
        @param query_info: 物料表中物料ID等于当前行的物料的物料ID的第一条数据。
        @param new_order: 出库单模型类实例
        @param inventory_flow: 库存流水单模型类实例
    """
    ids=request.args.get('ids')
    num=request.args.get('num')
    price=request.args.get('price')
    query_info=Material.query.filter(Material.ID==ids).first()    #查询物料表中物料ID等于出货单中出货的物料的物料ID的第一条数据。
    #销售表
    new_order=StockOut()
    new_order.ID= query_info.ID
    new_order.number=num
    new_order.price=price
    new_order.date=datetime.now()
    new_order.name=query_info.name
    new_order.package=query_info.package

    if query_info:
        if query_info.stock is None or query_info.stock < int(new_order.number):
            return jsonify({'msg':'nothing_or_smaller'})
        else:
            query_info.stock-=int(new_order.number)
            
    else:
        flash('出货失败，库存中没有该物料')
        return jsonify({'msg':'nothing'})
    #库存流水表
    inventory_flow=InventoryFlow()
    inventory_flow.name=new_order.name
    inventory_flow.package=new_order.package
    inventory_flow.ID= new_order.ID
    inventory_flow.price= new_order.price
    inventory_flow.date= new_order.date
    inventory_flow.types='out'
    inventory_flow.occurred_amount=(-int(new_order.number))
    inventory_flow.stock=query_info.stock

    db.session.add(inventory_flow)
    db.session.add(new_order)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.info('sql rollback error:',e)
        flash('新的出货记录添加失败。')
        return jsonify({'msg':'add_failed'})
    return jsonify({'msg':'add_succeed'})
    flash('新的出货记录添加成功。')
    return redirect(url_for('api_1_0.sale_list'))
    


#库存调整
@api.route('/record',methods=['GET','POST'])
def production_record():
    """
        描述:调整库存,作为调整单记录到库存流水表
        @param ids: 物料ID
        @param data: 调整数量,如果为正数,则库存数量加上该数量,如果为负数,则减去该数量
        @param query_info: 物料表中物料ID等于当前行的物料的物料ID的第一条数据。
        @param inventory_flow: 库存流水单模型类实例
    """
    ids=request.args.get('ids')
    data=request.args.get('record') 
    query_info=Material.query.filter(Material.ID==ids).first()
    inventory_flow=InventoryFlow()
    inventory_flow.ID=ids
    inventory_flow.name=query_info.name
    inventory_flow.package=query_info.package
    inventory_flow.types='adjust'
    inventory_flow.date=datetime.now()
    inventory_flow.occurred_amount=(int(data))
    inventory_flow.stock=query_info.stock+int(data)
    query_info.stock=inventory_flow.stock
    db.session.add(inventory_flow)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash('新的调整记录添加失败。')
        return jsonify({'msg':'failed'})
    flash('新的调整记录添加成功。')
    return jsonify({'msg':'succeed'})
    
    
#库存流水详情显示页
@api.route('/inventoryFlow', methods=['GET','POST'])
def inventory_flow():
    """
        描述:分页显示库存流水列表
        @param page: 当前所在的页数,默认为1
        @param page_data: pagination对象,第一个参数表示当前页,第二个参数代表每页显示的数量,
        第三个参数error_out=True的情况下如果指定页没有内容将出现404错误,False则返回空的列表
    """
    page = int(request.args.get('page') or 1)
    page_data=InventoryFlow.query.paginate(page, 20, False)
    return render_template("inventory_flow.html",page_data=page_data)


#库存流水搜索
@api.route('/searchInventoryFlow', methods=['GET','POST'])
def search_inventory_flow():
    """
    描述:实例化搜索框表单,如果点击了提交按钮,则跳转到api_1_0.search_result所在的路由。
        @type words: string
        @param words: 从搜索表单中获取的用户输入的参数。
    """
    form= SearchForm()
    if form.validate_on_submit():
        words=form.name.data
        return redirect(url_for('api_1_0.search_result',words=words))
    return render_template('search_flow.html',form=form)


#流水搜索结果
@api.route('/searchResult', methods=['GET','POST'])
def search_result():   
    """
    描述:实例化搜索框表单,如果点击了提交按钮,则跳转到api_1_0.search_result所在的路由。
        @param words: 从搜索框中接收到的用户输入的数据。
        @param page_data: 从库存流水表中筛选物料名称或者封装名称与输入项匹配的数据前20项，以Pagination格式返回。
    """
    words=request.args.get('words')
    words=words.strip()
    page = int(request.args.get('page') or 1)
    page_data=InventoryFlow.query.filter(or_(InventoryFlow.name.like("%" + words + "%"),
                            InventoryFlow.package.like("%" + words + "%")
                            )).paginate(page, 20, False)
    return render_template("search_result.html",page_data=page_data,words=words)




            