 var feed_card_len = 10;

$(document).ready(function(){
  
});

$(window).load(function() {
	var userArray = $('#header #groupmem_uid').map(function() { return $(this).val(); }).get();
  socket.emit('isOnline',userArray);
	
	$(".card_line").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
  	$(".card_line").hide().load("/card/").fadeIn('500');

  	$("#btnTutorialOk").click(function(){
  		$.post("/db/tutorial/",{"csrfmiddlewaretoken":$("input[name=csrfmiddlewaretoken]").val(),"is_pass":"arena"});
  		$('#Tutorial').modal('hide');
  	});

  	$('#arenaAd').carousel({
	  interval: 20000
	})
});

function drawCal(ySA,mSA,dSA,yEA,mEA,dEA,ySR,mSR,dSR,yER,mER,dER){
	var start_apply = new Date(ySA,mSA-1,dSA);
	var daySA = start_apply.getDay();
	var dateSA = start_apply.getDate();
	var monthSA = start_apply.getMonth();
	var yearSA = start_apply.getYear()+1900;

	var end_apply = new Date(yEA,mEA-1,dEA);
	var dayEA = end_apply.getDay();
	var dateEA = end_apply.getDate();
	var monthEA = end_apply.getMonth();
	var yearEA = end_apply.getYear()+1900;

	var start_round = new Date(ySR,mSR-1,dSR);
	var daySR = start_round.getDay();
	var dateSR = start_round.getDate();
	var monthSR = start_round.getMonth();
	var yearSR = start_round.getYear()+1900;

	var end_round = new Date(yER,mER-1,dER);
	var dayER = end_round.getDay();
	var dateER = end_round.getDate();
	var monthER = end_round.getMonth();
	var yearER = end_round.getYear()+1900;

	var weekName = new Array("<font style='color:#de4646'>S</font>","M","T","W","TH","F","<font style='color:#467fde'>S</font>");
	var monthName = new Array("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC");

	var day_Num = new Array(31,28,31,30,31,30,31,31,30,31,30,31);
	if(yearSA%4==0 || yearSA%400==0) day_Num = new Array(31,29,31,30,31,30,31,31,30,31,30,31);

	var n=0;
	var d=0;
	var calDay = new Array(35);
	if(daySA==6) daySA=-1;
	for(i=-(daySA+7);i<28-daySA;i++){
		d = (((dateSA+i-1)%day_Num[monthSA])+1); // 해달 일
		if(d<=0) d = d+day_Num[monthSA-1];
		// ----------- 신청기간 ----------- //
		if(d==dateSA) calDay[n++] = "<td class='cal-apply cal-apply-first' title='신청기간'>"+d+"</td>";
		else if(d==dateEA) calDay[n++] = "<td class='cal-apply cal-apply-last' title='신청기간'>"+d+"</td>";
		else if(d>dateSA&&d<dateEA) calDay[n++] = "<td class='cal-apply' title='신청기간'>"+d+"</td>";
		// ----------- 대회기간 ----------- //
		else if(i>0){
			if(d==dateSR) calDay[n++] = "<td class='cal-round cal-round-first' title='대회기간'>"+d+"</td>";
			else if(d==dateER) calDay[n++] = "<td class='cal-round cal-round-last' title='대회기간'>"+d+"</td>";
			else if(d>dateSR&&d<dateER) calDay[n++] = "<td class='cal-round' title='대회기간'>"+d+"</td>";
			else calDay[n++] = "<td>"+d+"</td>";
		}else calDay[n++] = "<td>"+d+"</td>";
	}

	var str="";
	var n=0;

	str += "<table class='cal-table'><caption class='cal-caption'>";
	str += monthName[monthSA]+" "+yearSA;
	str += "</caption><tbody class='cal-body'>";
	str += "<tr>";
	for(j=0;j<7;j++) str += "<td>"+weekName[j]+"</td>";
	str += "</tr>";
	for(i=0;i<5;i++){
		str += "<tr>";
		for(j=0;j<7;j++){
			str += calDay[n++];
		}
		str += "</tr>";
	}
	str += "</tbody></table>";
	return str
}