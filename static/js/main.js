$(document).ready(function(){
  feed_pri_len = 10;
  readFeed("#feed_pri", "pri", feed_pri_len, 0);
  feed_pub_len = 10;
  readFeed("#feed_pub", "pub", feed_pub_len, 0);
});

$(window).load(function() {

	var userArray = $('#header #groupmem_uid').map(function() { return $(this).val(); }).get();
  socket.emit('isOnline',userArray);

	$('#btnGamelink').click(function(){
	    $('#gamelink_tutor').hide();
	    $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":""});
    	$('#Gamelink').modal('show');
	 });

	$('.div_link_game.game_1').click(function(){
	    var userid = $(this).find(".p_gamelink_name").text();
	    $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":""},function(){
	      str = userid.replace(/\s+/g, '');
	      str = str.toLowerCase();
	      $('#Gamelink #div_gamelink_panelbody').html("<div width='100%' align='center'><img src='/static/img/ajax-loader_s.gif'></div>");
	      $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":str});
	    });
	    $('#Gamelink').modal('show');
	  });

	$('#btn_feedInput_post').click(function(){
	  var csrfmiddlewaretoken = $("#header input[name=csrfmiddlewaretoken]").val();
	  var utotype = $("#div_profile_feedInput #btn_feedInput_to").val();
	  var tag = $("#div_profile_feedInput #btn_feedInput_game").val();
	  var img = 0;
	  var txt = $("#div_profile_feedInput #textarea_feedinput_input").val();
	  var vid = 0;
	  var log = 0;
	  var hyp = 0;
	  var uid = 0;
	  if(txt!=""){
	    $.post("/forsocket/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val()},function(data,status){uid = $(data).filter('uid').text();});
	    $("#feed_pri").html("<div width='100%' align='center'><img src='/static/img/ajax-loader.gif'></div>");
  	  $("#feed_pri").hide().load("/db/feed/",{"action":"insert","csrfmiddlewaretoken":csrfmiddlewaretoken,"utotype":utotype,"tag":tag,"img":img,"txt":txt,"vid":vid,"log":log,"hyp":hyp},function(response, status) {
        //socket.emit('sendNotification', {'ufrom':uid,'uto':uid,'tablename':'home_feed'});
        $("form").each(function(){ if(this.id == "div_feedInput_form") this.reset(); });
      }).fadeIn('500');
	  }
	});

	$('#gamelink_tutor span').click(function(){
		$("#gamelink_tutor").alert('close');
	    $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":""});
    	$('#Gamelink').modal('show');
	});
});

function readFeed(loc, type, len, fid){
  $(loc).html("<div width='100%' align='center'><img src='/static/img/ajax-loader.gif'></div>");
  if(type == "pri") $(loc).hide().load("/feed/private/?len="+len+"&fid="+fid).fadeIn('500');
  else if(type == "pub") $(loc).hide().load("/feed/public/?len="+len+"&fid="+fid, function(){
  	if($(loc).html()=="") $(loc).html("<div width='100%' align='center'><img src='/static/img/main_global_bg.png'></div>");
  }).fadeIn('500');
}

function findId(from){
  var str = $('#input_gamelink_searchbar').val();
  str = str.replace(/\s+/g, '');
  str = str.toLowerCase();
  $('#div_gamelink_panelbody').html("<div width='100%' align='center'><img src='/static/img/ajax-loader_s.gif'></div>");
  $('#div_gamelink_panelbody').hide().load("/s/?from="+from,{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":str}, function(){
  	$('#input_gamelink_searchbar').attr("disabled","disabled");
  	$('.input_gamelink_btn').show();
  }).fadeIn('500');
}