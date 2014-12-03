$(document).ready(function(){
    var ran_no = Math.floor((Math.random() * 621) + 1);
    $("#profile").css({"background-image":"url(http://re01-xv2938.ktics.co.kr/stat_lol_"+ran_no+".jpg)"});
    $("#profileBG").css({"background-image":"url(http://re01-xv2938.ktics.co.kr/stat_lol_"+ran_no+".jpg)"});
});

$(window).load(function() {

     $("#profileBG").css({"top":$("#header").height()+"px"});

    memOnline--;
    $('#div_gamelink_gameadd').click(function(){
        $('#Gamelink .modal-content').load("/gamelink/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});
        $('#Gamelink').modal('show');
    });

    $('.div_gamelink_game.game_1').click(function(){
        var sid = $(this).find(".p_gamelink_name").text();
        $('#Gamelink .modal-content').load("/gamelink/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},function(){
            $("#div_tutor_right").html('<img src="/static/img/ajax-loader_s.gif" style="margin-top:160px">');
            $("#div_tutor_right").load("http://redbomba.net/gamelink/load/",{
                "csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),
                "sid":sid
            });
        });
        $('#Gamelink').modal('show');
    });

    $("#group").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
    $("#group").hide().load("/getgroup/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),"username":$("#p_profile_username").text()}).fadeIn('500');

    $("#myarenalist").html("<div style='width:100%;text-align:center'><img src='/static/img/ajax-loader.gif'></div>");
    $("#myarenalist").hide().load("/myarena/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val(),"username":$("#p_profile_username").text()}).fadeIn('500');

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