var query_no=0;
var feedSize = [
    ["size33","size33","size43"],
    ["size33","size33","size43"],
    ["size53","size53"],
    ["size33","size33","size43"],
    ["size33","size33","size43"],
    ["size33","size33","size43"],
    ["size53","size53"],
    ["size33","size33","size43"],
    ["size53","size53"]];

$(document).ready(function(){
    getDisplayContent('');
});

$(window).load(function() {

    $("#feed_pub").load("http://redbomba.net/feed/news/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},function(){
        $('.focuspoint').focusPoint();
    });

    var userArray = $('#header #groupmem_uid').map(function() { return $(this).val(); }).get();
    socket.emit('isOnline',userArray);

    $('#btnGamelink, #btnGamelink_s').click(function(){
        $('#gamelink_tutor').hide();
        $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});
        $('#Gamelink').modal('show');
    });

    $('.div_link_game.game_1').click(function(){
        var str = $(this).find(".p_gamelink_name").text();
        $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},function(){
            //str = str.replace(/\s+/g, '');
            //str = str.toLowerCase();
            $('#Gamelink #div_gamelink_panelbody').html("<div width='100%' align='center'><img src='/static/img/ajax-loader_s.gif'></div>");
            $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"sid":str});
        });
        $('#Gamelink').modal('show');
    });

    $('#gamelink_tutor span').click(function(){
        $("#gamelink_tutor").alert('close');
        $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"user":""});
        $('#Gamelink').modal('show');
    });
});

function getDisplayContent(dir){
    if(dir == "+") query_no+=1;
    if(dir == "-") query_no-=1;
    $('#display_con').hide().load("/league/display/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),'query_no':query_no}).fadeIn(200);
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

function setSize(){
    var count = 0;
    var arr = new Array();
    var box_size = $("#feed_pub .box").size();
    while(1){
        feedSize=shuffle(feedSize);
        for(i=0;i<feedSize.length;i++){
            feedSize[i]=shuffle(feedSize[i]);
            for(j=0;j<feedSize[i].length;j++){
                arr[count++] = feedSize[i][j];
                if (count == box_size) return arr;
            }
        }
    }
}

function shuffle(o){
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
}