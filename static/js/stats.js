$(document).ready(function(){
    var ran_no = Math.floor((Math.random() * 270) + 500);
    var ran_no2 = Math.floor((Math.random() * 270) + 500);
    $("#profile").css({"background-image":"url(http://ddragon.leagueoflegends.com/cdn/5.2.1/img/profileicon/"+ ran_no + ".png)"});
    $("#profileBG").css({"background-image":"url(http://ddragon.leagueoflegends.com/cdn/5.2.1/img/profileicon/"+ ran_no2 + ".png)"});

    $("#aside #group").load("/card/group/");

    $("#div_gamelink_gameadd").click(function(){
        $('#GamelinkModal .modal-content').load("/head/gamelink/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});
        $('#GamelinkModal').modal('show');
    });

    $("#img_profile_usericon").click(function() {
       $('#profileAddModal').modal('show');
    });
});