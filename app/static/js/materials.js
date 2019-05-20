function buy(obj){
    num=$(obj).attr('num');
    $("#buy_mid").val(num);
    //alert(num);
}

function sale(obj){
    num=$(obj).attr('num');
    $("#sale_mid").val(num);
    //alert(num);
}

function add(obj){
    num=$(obj).attr('num');
    yj=$(obj).attr('yj');
    fz=$(obj).attr('fz');
    types=$(obj).attr('types');
    $("#add_mid").val(num);
    $("#yj").val(yj);
    $("#fz").val(fz);
    $("#types").val(types);
}

function add_remark(obj){
    num=$(obj).attr('num');
    content=$(obj).attr('mark');
    $("#remark_mid").val(num);
    if(content!='None'){
        $("#remark").val(content);
    }
    else{
        $("#remark").val('');
    }
}


function adjust_record(obj){
    num=$(obj).attr('num');
    $("#record_mid").val(num);
}

function buy_submit(obj){
    var ids=$('#buy_mid').val();
    var num=$('#buy_number').val();
    var price=$('#buy_price').val();
    var page=$(obj).attr("page");
    data_json={
        'ids':ids,
        'num':num,
        'price':price
    }
    $.ajax({
        url:"/buy",
        data:jQuery.param(data_json,true),
        cache:false, 
        success:function() {
            alert('进货成功!')
            window.location=("/materialList?page="+page);
        },
        error:function(){
            alert('服务器错误!!')
        }
    })
    $('#buy_modal').modal('hide')
}


function sale_submit(obj){
    var ids=$('#sale_mid').val();
    var num=$('#sale_number').val();
    var price=$('#sale_price').val();
    var page=$(obj).attr("page");
    data_json={
        'ids':ids,
        'num':num,
        'price':price
    }
    $.ajax({
        url:"/sale",
        data:jQuery.param(data_json,true),
        success:function(data) {
            if(data['msg']=='nothing_or_smaller') {
                alert('出货失败，该物料没有库存或者库存数量小于出货数量')
            }
            if(data['msg']=='nothing') {
                alert('出货失败，库存中没有该物料')
            }
            if(data['msg']=='add_failed') {
                alert('新的出货记录添加失败。')
            }
            if(data['msg']=='add_succeed') {
                alert('出货成功!')
            }
            window.location=("/materialList?page="+page);
        },
        error:function(){
            alert('服务器错误')
        }
    })
    $('#sale_modal').modal('hide')
}

function add_submit(obj){
    var ids=$('#add_mid').val();
    var attr=$('#attribute').val();
    var value=$('#value').val();
    var yj=$('#yj').val();
    var fz=$('#fz').val();
    var types=$('#types').val();
    data_json={
        'ids':ids,
        'attr':attr,
        'value':value,
        'yj':yj,
        'fz':fz,
        'types':types
    }
    $.ajax({
        url:"/addAttr",
        data:jQuery.param(data_json,true),
        success:function(data) {
            if(data['msg']=='succeed')
            {
                alert('添加成功!')
            }

            if(data['msg']=='failed')
            {
                alert('表格不存在,请先添加表!')
                
            }
            //window.location.href ="{{ url_for('main.show_attr',ID=ids,yj=yj,fz=fz,mtype=types)}}"
            window.location =("/showAttr?ID="+ids+'&yj='+yj+'&fz='+fz+'&mtype='+types)
        },
        error:function(){
            alert('服务器错误')
        }
    })
    $('#add_modal').modal('hide')
}

function remark_submit(obj){
    var ids=$('#remark_mid').val();
    var remark=$('#remark').val();
    var page=$(obj).attr("page");
    data_json={
        'ids':ids,
        'remark':remark
    }
    $.ajax({
        url:"/addRemark",
        data:jQuery.param(data_json,true),
        success:function(data) {
            if(data['msg']=='succeed'){
                alert('添加成功')
            }
            if(data['msg']=='failed'){
                alert('添加失败')
            }
            window.location=("/materialList?page="+page);
        },
        error:function(){
            alert('服务器错误')
        }
    })
    $('#remark_modal').modal('hide')
}

function record_submit(obj){
    var ids=$('#record_mid').val();
    var record=$('#record_num').val();
    var page=$(obj).attr("page");
    data_json={
        'ids':ids,
        'record':record
    }
    $.ajax({
        url:"/record",
        data:jQuery.param(data_json,true),
        success:function(data) {
            if(data['msg']=='succeed'){
                alert('添加成功')
            }
            if(data['msg']=='failed'){
                alert('添加失败')
            }
            window.location=("/materialList?page="+page);
            //window.location.href ="{{ url_for('main.material_list',page=page)}}"
        },
        error:function(){
            alert('服务器错误')
        }
    })
    $('#record_modal').modal('hide')
}