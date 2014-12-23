$(document).ready(function(){
    var ran_no = Math.floor((Math.random() * 621) + 1);
    $("#profile").css({"background-image":"url(http://re01-xv2938.ktics.co.kr/stat_lol_"+ran_no+".jpg)"});
    $("#profileBG").css({"background-image":"url(http://re01-xv2938.ktics.co.kr/stat_lol_"+ran_no+".jpg)"});

    $("#aside #group").load("/card/group/");

});