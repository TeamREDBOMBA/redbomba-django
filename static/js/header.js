$(window).load(function() {

  uid = 0;
  memOnline = 1;

  $('.dropdown-toggle').dropdown();

  socket = io.connect('http://14.63.186.76:8080');
  socket.emit('leaveGroup','leave');
  $.post("/forsocket/",
    {
      "csrfmiddlewaretoken":$("input[name=csrfmiddlewaretoken]").val()
    },
    function(data,status){
      uid = $(data).filter('uid').text();
      var gid = $(data).filter('gid').text();
      socket.emit('joinGroup', gid);
      socket.emit('addUser', uid);
      socket.emit('loadNotification',uid);
  });

  socket.on('html', function (data) {
    $(data.name).html(data.html);
    if($('#noti_value').text()) $("#div_head_icon1 i").css({"color":"RGBA(255,255,255,1)"});
    if($('#field_value').text()) $("#div_head_icon2 i").css({"color":"RGBA(255,255,255,1)"});
  });
  
  socket.on('group', function (data) {
    $("#group").html("<div width='100%' align='center'><img src='/static/img/ajax-loader.gif'></div>");
    $("#group").hide().load("/group/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val()}).fadeIn('500');
  });

  socket.on('leagueReload', function (data) {
    try{
      $("#myarenalist").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
      $("#myarenalist").hide().load("/myarena/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val()}).fadeIn('500');
    }catch(e){}

    try{
      $("#div_right_btn").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
      $("#div_right_btn").hide().load("/cardbtn/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),"lid":$("#div_left #lid").val(),"uid":$("#div_left #uid").val()}).fadeIn('500');
    }catch(e){}
    
  });
  
  socket.on('isOffline', function (data) {
    $(".conn_"+data.id).attr('src','/static/img/stats_group_disconn.png');
  });
  
  socket.on('isOnline', function (data) {
    $(".conn_"+data.id).attr('src','/static/img/stats_group_conn.png');
    if(data.func == "isOnline") memOnline++;
   });

  socket.on('setChat', function (data) {
  	if(data.name == $('#p_head_username').text()) $("#GroupInfo .div_chat").html($("#GroupInfo .div_chat").html()+"<span class='username myname'>"+data.name+"</span> : "+data.con+"<br/>");
    else if(data.name == "redbomba") $("#GroupInfo .div_chat").html($("#GroupInfo .div_chat").html()+"<span class='username myname'><font color='#e74c3c'>RED</font>BOMBA</span> : "+data.con+"<br/>");
    else $("#GroupInfo .div_chat").html($("#GroupInfo .div_chat").html()+"<span class='username'>"+data.name+"</span> : "+data.con+"<br/>");
    $("#GroupInfo .div_chat").scrollTop($("#GroupInfo .div_chat")[0].scrollHeight);
  });
	
	$('#img_head_logo').click(function(){
		location.href="/";
	});
	
	$('#img_head_menu1').click(function(){
		location.href="/stats/";
	});
	
	$('#img_head_menu2').click(function(){
		location.href="/arena/";
	});

	$('.dropdown #Logout').click(function(){
		location.href="/auth/logout/";
	});

  $('#input_search_bar').focus(function(evt){
    if($("#input_search_bar").val() != "") getSearchList();
    evt.stopPropagation();
  });

  $('#input_search_bar').change(function(evt){
    getSearchList();
    evt.stopPropagation();
  });

  $('#input_search_bar').keyup(function(evt){
    getSearchList();
    evt.stopPropagation();
  });

	$('#a_head_gamelink').on('shown.bs.popover', function () {
	  $('#div_linkstep2_body').hide();
	});

	$('#a_head_gamelink').on('show.bs.popover', function () {
		$(this).attr("data-content",$("#div_gamelink_step1").html());
	});

	$('#a_head_noti').on('show.bs.popover', function () {
		$.post('/noti/',{
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        },function(res,status){
            $.post('/db/noti/',{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),'action':'read','uid':uid});
            $("#title_noti_value").hide();
            $("#noti_value").hide();
            $("#div_head_icon1 i").css({"color":"RGBA(255,255,255,0.3)"});
          	$('#div_head_icon1 .popover-content').html($("#div_noti_step1").html()+res);
        });
	});

  $('#a_head_field').on('show.bs.popover', function () {
    $.post('/field/',{
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        },function(res,status){
            $.post('/db/noti/',{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),'action':'check','loc':'field','uid':uid});
            $("#field_value").hide();
            $('#div_head_icon2 .popover-content').html(res);
        });
  });

});

function clickGamelink(iconid) {
  if(iconid == 1){
    $('#div_linkstep2_body').show();
  }
}

function getSearchList(){
  $('#div_head_searchlist').show();
  $('#div_head_searchlist').load('/searchlist/',{
  'csrfmiddlewaretoken':$('#header input[name=csrfmiddlewaretoken]').val(),
  'text':$('#input_search_bar').val()
  });
}

function click_name(username){
  location.href="/stats/"+username;
}