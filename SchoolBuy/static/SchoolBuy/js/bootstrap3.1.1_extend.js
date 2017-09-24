/**
 *  bootstrap扩展功能、公用方法、全局变量
 */


//全局变量
var G_V = {
	tabid : 0,                  //动态添加tab时，生成ID
	modal_head : "提示信息",    //提示框头部信息
	modal_ico: "",                   //根据type值定义提示框图标样式
	alert_type: ""                  //定义提示框显示类型
};

/* 回调的调用
 * @param call_back: 回调函数（可以是函数名，也可以是函数对象）
 */
function invoke_c_b(call_back){
	if(call_back){
		if($.isFunction(call_back)){
			call_back.call();
		}else{
			window[call_back];
		}
	}
}
//bootstrap-modal plugin
var Modal = function (content, options) {
    this.options = options;
    this.$element = $(content)
      .delegate('[data-dismiss="modal"]', 'click.dismiss.modal', $.proxy(this.hide, this));
  }

  Modal.prototype = {

      constructor: Modal

    , toggle: function () {
        return this[!this.isShown ? 'show' : 'hide']()
      }

    , show: function () {
        var that = this
          , e = $.Event('show');

        this.$element.trigger(e);

        if (this.isShown || e.isDefaultPrevented()) return;

        $('body').addClass('modal-open');

        this.isShown = true;

        escape.call(this);
        backdrop.call(this, function () {
          var transition = $.support.transition && that.$element.hasClass('fade');

          if (!that.$element.parent().length) {
            that.$element.appendTo(document.body); //don't move modals dom position
          }

          that.$element.show();

          if (transition) {
            that.$element[0].offsetWidth; // force reflow
          }

          that.$element.addClass('in');

          transition ? that.$element.one($.support.transition.end, function () { that.$element.trigger('shown') }) : that.$element.trigger('shown');

        })
      }

    , hide: function (e) {
        e && e.preventDefault();

        var that = this;

        e = $.Event('hide');

        this.$element.trigger(e);

        if (!this.isShown || e.isDefaultPrevented()) return;

        this.isShown = false;

        $('body').removeClass('modal-open');

        escape.call(this);

        this.$element.removeClass('in');

        $.support.transition && this.$element.hasClass('fade') ? hideWithTransition.call(this) : hideModal.call(this);
      }

  }


 //modal内部函数定义

  function hideWithTransition() {
    var that = this
      , timeout = setTimeout(function () {
          that.$element.off($.support.transition.end)
          hideModal.call(that)
        }, 500);

    this.$element.one($.support.transition.end, function () {
      clearTimeout(timeout);
      hideModal.call(that);
    })
  }

  function hideModal(that) {
    this.$element
      .hide()
      .trigger('hidden');

    backdrop.call(this);
  }

  function backdrop(callback) {
    var that = this
      , animate = this.$element.hasClass('fade') ? 'fade' : '';

    if (this.isShown && this.options.backdrop) {
      var doAnimate = $.support.transition && animate;

      this.$backdrop = $('<div class="modal-backdrop ' + animate + '" />')
        .appendTo(document.body);

      if (this.options.backdrop != 'static') {
        this.$backdrop.click($.proxy(this.hide, this));
      }

      if (doAnimate) this.$backdrop[0].offsetWidth; // force reflow

      this.$backdrop.addClass('in');

      doAnimate ? this.$backdrop.one($.support.transition.end, callback) : callback();

    } else if (!this.isShown && this.$backdrop) {
      this.$backdrop.removeClass('in');

      $.support.transition && this.$element.hasClass('fade')?
        this.$backdrop.one($.support.transition.end, $.proxy(removeBackdrop, this)) :
        removeBackdrop.call(this);

    } else if (callback) {
      callback();
    }
  }

  function removeBackdrop() {
    this.$backdrop.remove();
    this.$backdrop = null;
  }

  function escape() {
    var that = this;
    if (this.isShown && this.options.keyboard) {
      $(document).on('keyup.dismiss.modal', function ( e ) {
        e.which == 27 && that.hide();
      })
    } else if (!this.isShown) {
      $(document).off('keyup.dismiss.modal');
    }
  }


 //modal插件定义 
  $.fn.modal = function (option) {
    return this.each(function () {
      var $this = $(this)
        , data = $this.data('modal')
        , options = $.extend({}, $.fn.modal.defaults, $this.data(), typeof option == 'object' && option);
      if (!data) $this.data('modal', (data = new Modal(this, options)));
      if (typeof option == 'string') data[option]();
      else if (options.show) data.show();
    })
  }

  $.fn.modal.defaults = {
      backdrop: true
    , keyboard: true
    , show: true
  }

  $.fn.modal.Constructor = Modal;



/**
 * 自定义alert消息
 * @param   msg               需要显示的信息
 *          type              0: info(普通信息提示)
 *                1: help(帮助)
 *                2: success(成功)
 *                3: warning(警告)
 *                4: error(错误)
 */

//根据type值，定义消息框样式和图标
function alert_message(type){
  if(!type){
    G_V.modal_ico = "glyphicon glyphicon-info-sign";
    G_V.alert_type = "alert-info";
    G_V.modal_head="提示信息";
  }else if(type==1){
    G_V.modal_ico = "glyphicon glyphicon-question-sign";
    G_V.alert_type = "alert-help";
    G_V.modal_head="帮助信息";
  }else if(type==2){
    G_V.modal_ico = "glyphicon glyphicon-ok-sign";
    G_V.alert_type = "alert-success";
    G_V.modal_head="完成信息";
  }else if(type==3){
    G_V.modal_ico = "glyphicon glyphicon-exclamation-sign";
    G_V.alert_type = "alert-warning";
    G_V.modal_head="警告";
  }else if(type==4){
    G_V.modal_ico = "glyphicon glyphicon-remove-circle";
    G_V.alert_type = "alert-danger";
    G_V.modal_head="错误信息";
  }
}


/* 自定义alert消息(消息框有背景色)
 * @param  msg:       消息内容
 * @param  type:      消息类型
 * @param  call_back:   点击“确定”后的回调,可以是函数对象，也可以是函数名,但是不能但参数
 */
//function alert_msg(msg,type,call_back){
//  alert_message(type);
//  var $this = $(this)
//       , target_div = "<div class='modal hide '><div class='modal-header p_all'>"+
//      "<button class='close' data-dismiss='modal'>&times;</button>"+
//      "<h3>"+G_V.modal_head+"</h3></div>" + 
//      ("<div class='modal-body t_br "+G_V.alert_type+"'><p><span class='"+G_V.modal_ico+" mtr'></span>"+(typeof(msg)=="function"?msg.call():msg)+"</p></div>")+
//      "<div class='modal-footer'><a href='###' class='btn pull-right' data-dismiss='modal' onclick='invoke_c_b("+ call_back +");'>确定</a></div></div>"   //strip for ie7
//        , option = $(target_div).data('modal') ? 'toggle' : $.extend({}, $(target_div).data(), $this.data())  
//   $(target_div).modal(option);
//    
//}
function alert_msg(msg,type,call_back){
	  alert_message(type);
	  var $this = $(this)
	       , target_div = "<div class='modal fade'>" +
	       		"<div class='modal-dialog'>" +
	       		"<div class='modal-content'>" +
	       		"<div class='modal-header p_all'>"+
	      "<button class='close' data-dismiss='modal'><span aria-hidden='true'>&times;</span><span class='sr-only'>Close</span></button>"+
	      "<h4  class='modal-title'>"+G_V.modal_head+"</h4></div>" + 
	      ("<div class='modal-body t_br "+G_V.alert_type+"'><p><span class='"+G_V.modal_ico+" mtr'></span>"+(typeof(msg)=="function"?msg.call():msg)+"</p></div>")+
	      "<div class='modal-footer' style='margin-top: 0px;'>" +
	      "<button type='button' class='btn btn-box btn-primary' data-dismiss='modal' onclick='invoke_c_b("+ call_back +");'>确定</button></div></div></div></div>"   //strip for ie7
	        , option = $(target_div).data('modal') ? 'toggle' : $.extend({}, $(target_div).data(), $this.data())  
	   $(target_div).modal(option);   
}

//自定义alert消息，有背景色的消息框
/*function alert_msg_back(msg,type){
  alert_message(type);
    var $this = $(this)
    , target_div = "<div class='modal hide '> <div class='modal-header p_all'>"+
    "<button class='close' data-dismiss='modal'>&times;</button>"+
    "<h3>"+G_V.modal_head+"</h3></div>"+
    "<div class='modal-body "+G_V.alert_type+"'><p><span class='"+G_V.modal_ico+" mtr'></span>"+(typeof(msg)=="function"?msg.call():msg)+"</p></div>"+
    "<div class='modal-footer'><a href='###' class='btn pull-right' data-dismiss='modal'>确定</a></div></div>"   //strip for ie7
    , option = $(target_div).data('modal') ? 'toggle' : $.extend({}, $(target_div).data(), $this.data())

    $(target_div).modal(option);
}*/

//自定义提示信息的消息框
function show_msg(msg,type){
  alert_message(type);
  var lay_position
    , $msg_div=$("<div class='show_message  '></div>");
  //根据type值，定义提示信息的显示位置
  $msg_div.attr("class","top_center");
  if(!type){
//    $msg_div.attr("class","top_left");
    lay_position="top:"+document.body.scrollTop+"px";
  }else if(type==1){
//    $msg_div.attr("class","top_right");
    lay_position="top:"+document.body.scrollTop+"px";
  }else if(type==2){
//    $msg_div.attr("class","bottom_left");
    if(!document.body.scrollTop){
      lay_position="top:"+document.body.clientHeight+document.body.scrollTop-this.clientHeight+"px";
    }else{
      lay_position="bottom:-"+document.body.scrollTop+"px";
    }
  }else if(type==3){
//    $msg_div.attr("class","bottom_right");
    if(!document.body.scrollTop){
      lay_position="top:"+document.body.clientHeight+document.body.scrollTop-this.clientHeight+"px";
    }else{
      lay_position="bottom:-"+document.body.scrollTop+"px";
    }
  }else if(type==4){
//    $msg_div.attr("class","top_center");
    lay_position="top:"+document.body.scrollTop+"px";
  }else if(type==5){
//    $msg_div.attr("class","bottom_center");
    if(!document.body.scrollTop){
      lay_position="top:"+document.body.clientHeight+document.body.scrollTop-this.clientHeight+"px";
    }else{
      lay_position="bottom:-"+document.body.scrollTop+"px";
    }
  }
  var div_content = "<div class='alert t_br "+G_V.alert_type+"'><span class='"+G_V.modal_ico+" help-inline m_t4'></span>"+(typeof(msg)=="function"?msg.call():msg)+"</div>";
//  $msg_div.attr('style',lay_position);
  $msg_div.html(div_content);
  $msg_div.appendTo('body').show();
  //消息显示一定时间后自动隐藏
  setTimeout(function(){$msg_div.fadeOut();},2000);
}

/**
 * confirm（确认）
 * @param   msg           confirm的消息
 * @param   call_b_no               取消事件回调函数对象
 * @param   call_b_yes              确认事件回调函数对象
 */
//自定义confirm弹出框
//function bk_confirm(msg,call_b_no,call_b_yes){
//  alert_message(1);
//    var $this = $(this)
//    , $div_content = $("<div class='modal hide'> <div class='modal-header p_all'>"+
//      "<button class='close' data-dismiss='modal'>&times;</button>"+
//      "<h3>"+G_V.modal_head+"</h3></div>"+
//      "<div class='modal-body t_br'><p><span class='"+G_V.modal_ico+" mtr'></span>"+(typeof(msg)=="function"?msg.call():msg)+"</p></div>")
//    , $div_footer = $("<div class='modal-footer'></div>")  //strip for ie7
//    , option = $div_content.data('modal') ? 'toggle' : $.extend({}, $div_content.data(), $this.data())
//
//  //绑定取消回调函数
//  $("<a class='btn pull-right' data-dismiss='modal'>取消</a>").appendTo($div_footer)
//                                .click(function(){call_b_no.call(this);});
//    
//  //绑定确定回调函数
//  $("<a class='btn btn-primary pull-right mr15' data-dismiss='modal'>确定</a>").appendTo($div_footer)
//                                .click(function(){call_b_yes.call(this);});
//
//  //确认消息添加到body
//  $div_footer.appendTo($div_content);
//  $div_content.modal(option);
//}
function bk_confirm(msg,call_b_no,call_b_yes){
	  alert_message(1);
	    var $this = $(this)
	    , $div_content = $("<div class='modal fade'></div>") 
	    , $div_dialog = $("<div class='modal-dialog'></div>")
	    , $div_modal_content =$("<div class='modal-content'>" +
	        "<div class='modal-header p_all'>"+
	        "<button class='close' data-dismiss='modal'><span aria-hidden='true'>&times;</span><span class='sr-only'>Close</span></button>"+
	        "<h4  class='modal-title'>"+G_V.modal_head+"</h4></div>" + 
	        ("<div class='modal-body t_br "+G_V.alert_type+"'><p><span class='"+G_V.modal_ico+" mtr'></span>"+(typeof(msg)=="function"?msg.call():msg)+"</p></div></div>"))
	    , $div_footer = $("<div class='modal-footer' style='margin-top: 0px;'></div>")  //strip for ie7

	  //绑定取消回调函数
	  $("<button type='button' class='btn btn-box' data-dismiss='modal' >取消</button>").appendTo($div_footer)
	                                .click(function(){call_b_no.call(this);});
	    
	  //绑定确定回调函数
	  $("<button type='button' class='btn btn-box btn-primary' data-dismiss='modal'>确定</button>").appendTo($div_footer)
	                                .click(function(){call_b_yes.call(this);});

	  //确认消息添加到body
	  $div_footer.appendTo($div_modal_content);
	  $div_modal_content.appendTo($div_dialog);
	  $div_dialog.appendTo($div_content);
	  var option = $div_content.data('modal') ? 'toggle' : $.extend({}, $div_content.data(), $this.data())
	  $div_content.modal(option);
}


//生成tabid
function get_tabid(){
	return ++G_V.tabid;
}

/**
 * 调用add_tab插件
 * @param   title_id            添加页签显示内容的id
 * @param   tab_title           添加页签的title
 * @param   tab_obj              ul的对象值
 * @param   tab_con_obj          点击此页签显示div内容的id属性
 */
 function add_tab(title_id,tab_title,tab_obj,tab_con_obj){
	 //删除激活状态li的active样式
	 $(tab_obj+" > li[class*='active']").removeClass('active');
	 //删除激活tab相关的div的active样式
	 $(tab_con_obj+" > div[class*='active']").removeClass('in active');   
	 if($(tab_obj+" > li").find('a[href="#'+title_id+'"]').attr('href')){
		//如果要添加的tab标签已经存在
		$(tab_obj+" > li a[href='#"+title_id+"']").parent().attr('class','active');
		$('#'+title_id).attr('class','tab-pane in active');
	 }else{
		//要添加的标签不存在，则创建新的tab添加到已有tab列的后面
		$('<li class="active"><a href="#'+title_id+'" data-toggle="tab">'+tab_title+'<span class="close ml10" data-dismiss="alert" onclick="close_tab(this)">&times;</span></a></li>').appendTo($(tab_obj));
		//添加此tab关联的div内容
		$('<div class="tab-pane fade in active" id="'+title_id+'"><p>显示动态添加页签的数据内容。</p></div>').appendTo($(tab_con_obj));
	 }
	 //再次激活动态添加的tab时自动隐藏其相关内容
	 $(function(){
		if($(tab_obj+" > li a[href='#"+title_id+"']").parent().attr('class')!='active'){
			$('#'+title_id).removeClass('in active');
		}
	 });
 }

/**  每次点击添加tab
 * @param   title_prefix			添加页签显示内容的前缀
 * @param   tab_title				添加页签的title
 * @param   tab_obj					ul的对象值
 * @param   tab_con_obj				点击此页签显示div内容的id属性
 * @param   callback				添加tab内容的函数对象，或者字符串
 * @param   is_active				标记添加的tab是否激活
 */
 function dy_add_tab(title_prefix,tab_title,tab_obj,tab_con_obj,callback,is_active){
	var title_id = title_prefix+"_"+get_tabid();
	if(!is_active){
		//创建新的tab添加到已有tab列的后面
		$('<li><a href="#'+title_id+'" data-toggle="tab">'+tab_title+'<span class="close ml10" data-dismiss="alert" onclick="close_tab(this)">&times;</span></a></li>').appendTo($(tab_obj));
		//添加此tab关联的div内容
		$('<div class="tab-pane fade" id="'+title_id+'">'+(typeof(callback)=="function"?callback.call():callback)+'</div>').appendTo($(tab_con_obj));
	}else{
		 //删除激活状态li的active样式
		 $(tab_obj+" > li[class*='active']").removeClass('active');
		 //删除激活tab相关的div的active样式
		 $(tab_con_obj+" > div[class*='active']").removeClass('in active');   
		 //创建新的tab添加到已有tab列的后面
		 $('<li class="active"><a href="#'+title_id+'" data-toggle="tab">'+tab_title+'<span class="close ml10" data-dismiss="alert" onclick="close_tab(this)">&times;</span></a></li>').appendTo($(tab_obj));
		 //添加此tab关联的div内容
		 $('<div class="tab-pane fade in active" id="'+title_id+'">'+(typeof(callback)=="function"?callback.call():callback)+'</div>').appendTo($(tab_con_obj));
		 //再次激活动态添加的tab时自动隐藏其相关内容
		 $(function(){
			if($(tab_obj+" > li a[href='#"+title_id+"']").parent().attr('class')!='active'){
				$('#'+title_id).removeClass('in active');
			}
		 });
	}
 }

 //关闭tab时，删除其相关的div，并激活前一个tab及其关联内容
 function close_tab(obj){
	//获取此tab的父亲节点li
	var parent_node=$(obj).parent('a').parent('li');
	//此tab前没有tab页签，则关闭当前tab并激活其后的tab
	if(!$(parent_node).prev().html()){
		//此tab未处于激活状态，则直接移除此tab
		if(!parent_node.attr('class')){
			//移除此tab关联的div
			$($(obj).parent('a').attr('href')).remove();
			//所有的tab都未激活
			if(!$(parent_node).parent().children('li[class*="active"]').length){
				//激活此tab后面的tab及其关联的div
				$(parent_node).next().attr('class','active');
				$($(parent_node).next().children('a').attr('href')).addClass('in active');
			}
		}else{
			//移除此tab的class属性
			$(parent_node).removeAttr('class');
			//此tab处于激活状态，移除此tab关联的div
			$($(obj).parent('a').attr('href')).remove();
			//激活此tab后面的tab及其关联的div
			$(parent_node).next().attr('class','active');
			$($(parent_node).next().children('a').attr('href')).addClass('in active');
		}
	}else{
		//关闭此tab并激活其前的tab和相关联的div

		//此tab未处于激活状态，则直接移除此tab
		if(!parent_node.attr('class')){
			//移除此tab的class属性
			$(parent_node).removeAttr('class');
			//移除此tab关联的div
			$($(obj).parent('a').attr('href')).remove();
			//所有的tab都未激活
			if(!$(parent_node).parent().children('li[class*="active"]').length){
				//激活此tab后面的tab及其关联的div
				$(parent_node).prev().attr('class','active');
				$($(parent_node).prev().children('a').attr('href')).addClass('in active');
			}
		}else{
			//此tab处于激活状态，移除此tab关联的div
			$($(obj).parent('a').attr('href')).remove();
			//激活此tab后面的tab及其关联的div
			$(parent_node).prev().attr('class','active');
			$($(parent_node).prev().children('a').attr('href')).addClass('in active');
		}
		//移除该tab
		$(obj).parent('a').parent('li').remove();
		$(obj).remove();
	}
 }