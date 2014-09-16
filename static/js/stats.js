$(document).ready(function(){
    feed_pri_len = 10;
    readFeed("#feed_pri", feed_pri_len, 0, $("#p_profile_username").text());
    var ran_no = Math.floor((Math.random() * 621) + 1);
    $("#profile").css({"background-image":"url(http://re01-xv2938.ktics.co.kr/stat_lol_"+ran_no+".jpg)"});
    $("#profileBG").css({"background-image":"url(http://re01-xv2938.ktics.co.kr/stat_lol_"+ran_no+".jpg)"});
});

$(window).load(function() {

     $("#profileBG").css({"top":$("#header").height()+"px"});

    memOnline--;
    $('#div_gamelink_gameadd').click(function(){
        $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});
        $('#Gamelink').modal('show');
    });

    $('.div_gamelink_game.game_1').click(function(){
        var str = $(this).find(".p_gamelink_name").text();
        $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},function(){
            //str = str.replace(/\s+/g, '');
            //str = str.toLowerCase();
            $('#Gamelink #div_gamelink_panelbody').html("<div width='100%' align='center'><img src='/static/img/ajax-loader_s.gif'></div>");
            $('#Gamelink .modal-content').load("/s/?from=/stats/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),"sid":str});
        });
        $('#Gamelink').modal('show');
    });

    $("#group").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
    $("#group").hide().load("/group/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),"username":$("#p_profile_username").text()}).fadeIn('500');

    $("#myarenalist").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
    $("#myarenalist").hide().load("/myarena/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),"username":$("#p_profile_username").text()}).fadeIn('500');

    $('#btn_feedInput_post').click(function(){
        var csrfmiddlewaretoken = $("#header input[name=csrfmiddlewaretoken]").val();
        var uto = $("#p_profile_username").text();
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
            $("#feed_pri").hide().load("/db/feed/",{"action":"insert","csrfmiddlewaretoken":csrfmiddlewaretoken,"uto":uto,"utotype":utotype,"tag":tag,"img":img,"txt":txt,"vid":vid,"log":log,"hyp":hyp},function(response, status) {
                //socket.emit('sendNotification', {'ufrom':uid,'uto':uid,'tablename':'home_feed'});
                $("form").each(function(){ if(this.id == "div_feedInput_form") this.reset(); });
            }).fadeIn('500');
        }
    });

    $('#groupaddModal #name').keyup(function(event){
        var str = $('#groupaddModal #name').val();
        str = str.replace(" ","+");
        $("#groupaddModal #name ~ p").hide().load("/group/fnc/name/?name="+str).fadeIn('500');
    });

    $('#groupaddModal #nick').keyup(function(event){
        var str = $('#groupaddModal #nick').val();
        str = str.replace(" ","+");
        $("#groupaddModal #nick ~ p").hide().load("/group/fnc/nick/?nick="+str).fadeIn('500');
    });


    $('#groupaddModal .modal-footer #save').click(function(){
        $.post("/db/group/",{
            "csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),
            "name":$("#groupaddModal #name").val(),
            "nick":$("#groupaddModal #nick").val(),
            "game":$("#groupaddModal #game").val(),
            "action":"insert"
        },function(res,status){
            $("#groupaddModal #name").val("");
            $("#groupaddModal #nick").val("");
            $("#groupaddModal #game").val("");
            $('#groupaddModal').modal('hide');
            location.href="/stats/?get=madegroup&group="+res;
        });
    });

    $('#div_table_add').click(function(){
        location.href = "/arena/";
    });
});

function readFeed(loc, len, fid, username){
    $(loc).load("/feed/private/?len="+len+"&fid="+fid+"&username="+username,function(){
        if($(loc).html()=="") $(loc).html("<div width='100%' align='center'><img src='/static/img/main_global_bg.png'></div>");
    });
}