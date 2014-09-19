$(document).ready(function(){

});
$(window).load(function() {

    if(location.href.indexOf("www.") != -1 ){
            location.href = location.href.replace("www.","");
     }

	socket = io.connect('http://redbomba.net:3000/');
	socket.emit('leaveGroup','leave');
	socket.emit('leaveRound','leave');

	var userArray = $('#header #groupmem_uid').map(function() { return $(this).val(); }).get();
  	socket.emit('isOnline',userArray);

	$.post("/forsocket/",
	{
		"csrfmiddlewaretoken":$("input[name=csrfmiddlewaretoken]").val()
	},
		function(data,status){
		var uid = $(data).filter('uid').text();
		var gid = $(data).filter('gid').text();
		socket.emit('joinRound', {'round_id':$('#round_id').val(),'side':$('#side').val()});
		socket.emit('joinGroup', gid);
		socket.emit('addRoundUser', uid);

		var userArray = $('.uid').map(function() { return $(this).val(); }).get();
		socket.emit("EnterRound",userArray);
	});

	socket.on('html', function (data) {
		$(data.name).html(data.html);
	});

	socket.on('refresh', function (data) {
		location.reload(true);
	});

	socket.on('isRoundOffline', function (data) {
		$(".conn_"+data).attr('src','/static/img/stats_group_disconn.png');
	});

	socket.on('isRoundOnline', function (data) {
		$(".conn_"+data).attr('src','/static/img/stats_group_conn.png');
	});

	socket.on('setChat', function (data) {
  	if(data.name == $('#content > #username').val()) $("#Chatting .div_chat").html($("#Chatting .div_chat").html()+"<span class='username myname'>"+data.name+"</span> : "+data.con+"<br/>");
    else $("#Chatting .div_chat").html($("#Chatting .div_chat").html()+"<span class='username'>"+data.name+"</span> : "+data.con+"<br/>");
    $("#Chatting .div_chat").scrollTop($("#Chatting .div_chat")[0].scrollHeight);
  });

	socket.on('setResult', function (data){
		if(data){
			$('#result').hide();
		}else{
			$('#result #title').show();
			$('#result #subtitle').show();
			$('#result #result_win').removeClass('grayimg');
			$('#result #result_lose').removeClass('grayimg');
		}
	});

	socket.on('state', function (data) {
		switch(data.state){
			case 0:
				$('#container #content #simpleMsg').html("대회 진행을 도와줄<br/>호스트를 기다리는 중 입니다.<br/><br/>빨리 그룹장이 오도록<br/>독촉하여 주세요.");
				break;
			case 1:
				$('#state').val('1');
				$('#container #content #simpleMsg').html("지금 호스트가 대회 진행을 위해<br/>커스텀 게임을 생성 중 입니다.<br/><br/>창이 뜰 때까지 잠시만 기다려 주세요.");
				$('.modal').modal('hide');
				$('#state_1').modal('show');
				$('.modal-backdrop.fade').css({'background-color': 'rgba(0,0,0,0)'});
				break;
			case 2:
				if(data.roomtitle){
					$('#state_2 #roomtitle').val(data.roomtitle);
					$('#state_2 #roompass').val(data.roompass);
				}
				$('#state').val('2');
				$('#container #content #simpleMsg').html("");
				$('.modal').modal('hide');
				$('#state_2').modal('show');
				$('.modal-backdrop.fade').css({'background-color': 'rgba(0,0,0,0)'});
				break;
			case 3:
				$('#state').val('3');
				$('#container #content #simpleMsg').html("양팀의 준비를 기다리는 중입니다.<br/>준비가 완료되면 자동으로 진행됩니다.");
				if(data.side||data.result){
					if(data.side == 'A'||data.result == 'A') $("#img_ready_A").show();
					else if(data.side == 'B'||data.result == 'B') $("#img_ready_B").show();
				}
				if(data.side== $('#side').val()||data.result== $('#side').val()){
					$('.modal').modal('hide');
				}else{
					$('#state_2').modal('show');
				}
				break;
			case 4:
				$('#container #content #simpleMsg').html("");
				if(data.side){
					if(data.side == 'A') $("#img_ready_A").show();
					else if(data.side == 'B') $("#img_ready_B").show();
				}
				$('#state').val('4');
				$('.modal').modal('hide');
				$("#countdown").show();
				var time_i = 3;
				var timer = setInterval(function(){
				  time_i--;
				  if(time_i==0){
				    clearInterval(timer);
				    $("#countdown").hide();
				    socket.emit("state",{'state':4,'lid':$('#round_id').val()});
				    $("#img_ready_A").hide();
				    $("#img_ready_B").hide();
				    $('#container #content #simpleMsg').html("");
				  }else $('#p_text').text(time_i);
				}, 1000);
				break;
			case 5:
				$('#state').val('5');
				$('#container #content #simpleMsg').html("");
				$('#Chatting').hide();
				time = new Date(Number(data.result));
				ready_timer = setInterval(function (){
				    // The number of milliseconds in one day
				    var ONE_MIN = 1000 * 60;

				    // Convert both dates to milliseconds
				    var date1_ms = new Date(Date.now()).getTime();
				    var date2_ms = time.getTime();

				    // Calculate the difference in milliseconds
				    var difference_ms = Math.abs(date1_ms - date2_ms);

				    difference = Math.round(difference_ms/ONE_MIN)

				    // Convert back to days and return
				    if(difference >= 10 && $('#state').val()=='5'){
				    	clearInterval(ready_timer);
				    	$('#lock #title').hide();
				    	$('#lock #title').hide();
				    	$('#btn_lock_ready').show();
				    	socket.emit("state",{'state':5,'lid':$('#round_id').val()});
				    }
				},1000);
				$('#result').show();
				$('#lock').fadeIn(1000);
				break;
			case 6:
				$('#state').val('6');
				$('#container #content #simpleMsg').html("");
				$('#Chatting').hide();
				$('#title').hide();
    			$('#subtitle').hide();
				$('#result').show();
				$('#lock').show();
				$('#btn_lock_ready').show();
				break;
			case 7:
				if(!data.side){
					$('#container #content #simpleMsg').html("");
					$('#Chatting').hide();
					$('#title').hide();
    				$('#subtitle').hide();
					$('#result').show();
					$('#lock').fadeIn(1000);
					$('#btn_lock_ready').fadeIn(1000);
					$('#btn_lock_ready').button('loading');
					$('#state').val('7');
				}else{
					$('#state').val('6');
				}
				break;
			case 8:
				$('#container #content #simpleMsg').html("각 그룹장들이<br/>승/패를 처리 중입니다.<br/>잠시만 기다려주세요.");
				$('#Chatting').hide();
				$('#state').val('8');
				$('#result').show();
				$('#lock').hide();
				break;
			case 10:
				$('#Chatting').hide();
				$('#container #content #simpleMsg').html("");
				if ($('#side').val() == data.result){
					$('#winner').modal('show');
				}else{
					$('#loser').modal('show');
				}
				break;
		}
	});
});