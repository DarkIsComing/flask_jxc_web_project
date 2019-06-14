from . import db
from datetime import datetime


#类型表
class MaterialType(db.Model):
    __tablename__='type'
    ID=db.Column(db.Integer,primary_key=True)
    type_name=db.Column(db.String(64))  
    __table_args__ = {
          'mysql_charset':'UTF8MB4'
      }
#物料表
class Material(db.Model):
    __tablename__='materials'       
    ID=db.Column(db.Integer,primary_key=True)                       #物料ID
    name=db.Column(db.String(64),nullable=False)           #物料名称
    package=db.Column(db.String(64))                           #物料型号
    types=db.Column(db.String(64))                          #物料类型
    stock=db.Column(db.Integer)                            #物料库存
    remark=db.Column(db.String(64))                                 #备注
    __table_args__ = {
          'mysql_charset':'UTF8MB4'
      }
    # stockin_info = db.relationship('Stock_In',backref="materials")
    # stockout_info = db.relationship('Stock_Out',backref="materials")
    # buy_order = db.relationship('Buy_Order',backref="materials")
    # sale_order = db.relationship('Sale_Order',backref="materials")

# #物料详情表
# class MaterialDetail(db.Model):
#     __tablename__='material_detail'
#     编号=db.Column(db.Integer,primary_key=True)
#     物料ID=db.Column(db.Integer,db.ForeignKey('materials.ID'),nullable=False,unique=True)

    

# #库存信息表
# class Inventory(db.Model):
#     __tablename__='inventory'
#     库存编号=db.Column(db.Integer,primary_key=True)
#     类型=db.Column(db.Enum('in','out','adjust'))
#     #发生数量=db.Column(db.Integer)
#     库存数量=db.Column(db.Integer)
#     物料名称=db.Column(db.String(64))
#     物料ID=db.Column(db.Integer,db.ForeignKey('materials.ID'),nullable=False)

#入库表 
class  StockIn(db.Model):
    __tablename__='stock_in'
    ids=db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    number=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    date=db.Column(db.DateTime(),default=datetime.now)   
    name=db.Column(db.String(64))
    package=db.Column(db.String(64))
    ID=db.Column(db.Integer,db.ForeignKey('materials.ID'))
    __table_args__ = {
          'mysql_charset':'UTF8MB4'
      }

#出库单 
class  StockOut(db.Model):
    __tablename__='stock_out'
    ids=db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    number=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    date=db.Column(db.DateTime(),default=datetime.now)
    name=db.Column(db.String(64))
    package=db.Column(db.String(64))
    ID=db.Column(db.Integer,db.ForeignKey('materials.ID'))
    __table_args__ = {
          'mysql_charset':'UTF8MB4'
      }






#库存流水表 
class  InventoryFlow(db.Model):
    __tablename__='inventory_flow'
    ids=db.Column(db.Integer,primary_key=True,nullable=False,autoincrement=True)
    name=db.Column(db.String(64))
    package=db.Column(db.String(64))
    ID=db.Column(db.Integer,db.ForeignKey('materials.ID'))
    #价格=db.Column(db.Float,nullable=False)
    date=db.Column(db.DateTime(),default=datetime.now)
    types=db.Column(db.String(32))
    occurred_amount=db.Column(db.Integer,nullable=False)
    stock=db.Column(db.Integer,nullable=False)
    __table_args__ = {
          'mysql_charset':'UTF8MB4'
      }
    




# #物料生产信息表
# class MaterialsInfo(db.Model):
#     __tablename__='materials_product_info'       
#     ID=db.Column(db.Integer,primary_key=True)       #编号
#     封装名称=db.Column(db.String(64),nullable=False)             #封装名称                          #物料类型
#     封装数量=db.Column(db.String(64))                            #封装数量
#     倍率=db.Column(db.String(64)) 
#     生产数量=db.Column(db.String(64)) 
#     __table_args__ = {
#           'mysql_charset':'utf8'
#       }


# #供应商
# class Supplier(db.Model):
#     __tablename__='supplier'        
#     supplier_id=db.Column(db.Integer,primary_key=True)   #供应商ID
#     material_id           
#     supplier_name=db.Column(db.String(64))                          #供应商名字
#     package_type=db.Column(db.String(64))                           #包装类型



