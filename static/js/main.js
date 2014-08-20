﻿$(document).ready(function(){

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

	$('#gamelink_tutor span').click(function(){
		$("#gamelink_tutor").alert('close');
	    $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":""});
    	$('#Gamelink').modal('show');
	});
});

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