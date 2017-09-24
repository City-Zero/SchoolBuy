//全局变量
var  person_model = kendo.data.Model.define({
                                    id: "id",
                                    fields: {
                                        //data type of the field {Number|String|Boolean|Date} default is String
                                        id:{type:"number",editable: false, nullable: true },
                                        english_name: { type: "string",validation: {required: true }},
                                        chinese_name: { type: "string",validation: {required: true }}, 
                                        city: { type: "string",validation: {required: true }},
                                        birthday: { type: "date",validation: {required: true }},
                                        age:{type:"number",validation: {required: true, min: 1 }},
                                        email :{type:"string",nullable:true, validation:{email: true}},//添加验证
                                        tel : {type:"string",nullable:true, validation:{pattern: "\\d{11}"}},//自定义验证（斜杠'\'需要转义）
                                    }
    }) 

var book_model = kendo.data.Model.define({
                                    id: "id",
                                    fields:{
                                        id: {type:"number",editable: false, nullable: true },
                                        author: {type: "string",validation: {required: true }},
                                        publication_date: {type: "date",validation: {required: true }},
                                        price: {type: "number",validation: {required: true }}
                                    }
})

function get_part_by_name(part_name){
    var url = site_url+'kendo_crud/get_part_by_name/';
    var param = {'part_name':part_name};
    $.get(url,param,function(res){
        if(res.result)
        {
            $('#test').html(res.res);
        }
    },'json')
}

function get_from_sample_part(){
    var url = site_url+'kendo_crud/form_sample/';
    $.get(url,function(res){
        $('#test').html(res);
    })
}

/**
 * 时间格式化
 * @param x 时间。如new Date()
 * @param y 格式：如："yyyy-MM-dd hh:mm:ss"
 * @returns 格式化后的时间字符串
 */
function date2str(x,y) {
    var z = {M:x.getMonth()+1,d:x.getDate(),h:x.getHours(),m:x.getMinutes(),s:x.getSeconds()};
    y = y.replace(/(M+|d+|h+|m+|s+)/g,function(v) {return ((v.length>1?"0":"")+eval('z.'+v.slice(-1))).slice(-2)});
    return y.replace(/(y+)/g,function(v) {return x.getFullYear().toString().slice(-v.length)});
    }