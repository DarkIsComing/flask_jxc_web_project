function adjust_num(obj){
    sums=$(obj).attr('sums');
    yj=$(obj).attr('yj');
    fz=$(obj).attr('fz');
    $("#yjm").val(yj);
    $("#fzm").val(fz);
    $("#sums").val(sums);
}


function change_submit(obj){
    var sums=$('#sums').val();
    var num=$('#change_num').val();
    var yj=$('#yjm').val();
    var fz=$('#fzm').val();
    var path=$(obj).attr("path");
    var name=$(obj).attr("name");
    data_json={
        'sums':sums,
        'num':num,
        'yj':yj,
        'fz':fz,
        'path':path,
        'name':name
    }
    $.ajax({
        url:"/changeSum",
        data:jQuery.param(data_json,true),
        success:function(data) {
            if(data['change']=='succeed'){
                alert('修改成功');
                
            }
            if(data['change']=='failed'){
                alert('修改失败');
            }
            window.location=("/opencsv?name="+name+"&path="+path)
            //window.location=("/opencsv?name="+name+"&path="+path+"&yj="+yj+"&fz="+fz+"&sums="+sums+"&num="+num)
            //window.location.href ="{{ url_for('main.material_list',page=page)}}"
        },
        error:function(){
            alert('服务器错误')
        }
    })
    $('#change_modal').modal('hide')
}




function produce_submit(obj){
    
    var path=$(obj).attr("path");
    var name=$(obj).attr("name");
    var mytable = document.getElementById('mytable');
    data_json={
        'path':path,
        'name':name
    }
    $.ajax({
        url:"/produceAll",
        data:jQuery.param(data_json,true),
        async:false,
        success:function(d) {  
            d=JSON.stringify(d)
            window.location=("/opencsv?name="+name+"&path="+path+"&d="+d)
            // for(var i in d){
            //     i=parseInt(i);
            //     if(d[i]=='succeed')
            //     {
            //         mytable.rows[i+1].cells[6].innerText='出库成功';
            //         mytable.rows[i+1].cells[6].setAttribute("style","color:green");
            //     }
            //     else{
            //         mytable.rows[i+1].cells[6].innerText='出库失败';
            //         mytable.rows[i+1].cells[6].setAttribute("style","color:red");
            //     }
            // }
        },
        error:function(){
            alert('服务器错误')
        }
    })
    $('#produce_modal').modal('hide')

}