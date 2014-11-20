$(window).load(function() {

     if(location.href.indexOf("www.") != -1 ){
            location.href = location.href.replace("www.","");
     }

    uid = 0;
    memOnline = 1;

    $("#container").css({"padding-top":$("#header").height()+"px"});

    $('.dropdown-head-toggle').dropdown();

    socket = io.connect('http://redbomba.net:3000/');
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
        if($('#noti_value').text()){
            $("#div_head_icon1 i").css({"color":"RGBA(102,117,127,1)"});
            $('#noti_value').show();
        }
        if($('#field_value').text()){
            $("#div_head_icon2 i").css({"color":"RGBA(102,117,127,1)"});
            $('#field_value').show();
        }
    });

    socket.on('group', function (data) {
        $("#group").html("<div width='100%' align='center'><img src='/static/img/ajax-loader.gif'></div>");
        $("#group").hide().load("/getgroup/",{"csrfmiddlewaretoken":$("#header input[name=csrfmiddlewaretoken]").val()}).fadeIn('500');
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
        data_id = ""+data.id;
        $(".conn_"+data_id).attr('src','/static/img/stats_group_disconn.png');
    });

    socket.on('isOnline', function (data) {
        data_id = ""+data.id;
        $(".conn_"+data.id).attr('src','/static/img/stats_group_conn.png');
        if(data.func == "isOnline") memOnline++;
    });

    socket.on('setChat', function (data) {
        if(data.name == $('#p_head_username').text()) $("#GroupInfo .div_chat").html($("#GroupInfo .div_chat").html()+"<span class='username myname'>"+data.name+"</span> : "+data.con+"<br/>");
        else if(data.name == "redbomba") $("#GroupInfo .div_chat").html($("#GroupInfo .div_chat").html()+"<span class='username myname'><font color='#e74c3c'>RED</font>BOMBA</span> : "+data.con+"<br/>");
        else $("#GroupInfo .div_chat").html($("#GroupInfo .div_chat").html()+"<span class='username'>"+data.name+"</span> : "+data.con+"<br/>");
        $("#GroupInfo .div_chat").scrollTop($("#GroupInfo .div_chat")[0].scrollHeight);
    });

    $('#li_head_home, #li_head_logo').click(function(){
        location.href="/";
    });

    $('#li_head_arena').click(function(){
        location.href="/arena/";
    });

    $('#li_head_profile').click(function(){
        location.href="/stats/";
    });

    $('.dropdown_head #Logout').click(function(){
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

});

$(document).ready(function(){

    $('#a_head_noti').popover();
    $('#a_head_field').popover();

    $(document).on('click',function(){
        $('#a_head_noti').popover('hide');
        $('#a_head_field').popover('hide');
    });

    $('#a_head_noti').click(function(){
        $.post('/noti/',{
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        },function(res,status){
            $.post('/db/noti/',{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),'action':'read','uid':uid});
            $("#title_noti_value").hide();
            $("#noti_value").hide();
            $("#div_head_icon1 i").css({"color":"RGBA(102,117,127,0.3)"});
            $('#div_head_icon1 .popover-content').html($("#div_noti_step1").html()+res);
        });
        return false;
    });

    $('#a_head_field').click(function(){
        $.post('/field/',{
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
        },function(res,status){
            $.post('/db/noti/',{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),'action':'check','loc':'field','uid':uid});
            $("#field_value").hide();
            $('#div_head_icon2 .popover-content').html(res);
        });
        return false;
    });

    setTimeout(function(){
        $("#fchat").show();
        $("#fchat-header-label").css({"font-family":"RixSGo L"});
        $("#fchat").css({"bottom":"-256px"});
    },3000);

     $("#fchat-header").click(function(){
            $("#fchat").css({"bottom":"0"});
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

function goGroupPage(gid){
    $('.modal').modal('hide');
    $('#GroupInfo .modal-content').load('/groupinfo/',{'csrfmiddlewaretoken':$('#header input[name=csrfmiddlewaretoken]').val(),'group':gid});
    $('#GroupInfo').modal('show');
}