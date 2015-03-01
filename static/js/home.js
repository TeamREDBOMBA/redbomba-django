$(document).ready(function() {

    $('#signup-aside').hide();

    var wh = $(window).height();
    var ww = $(window).width();

    var rt_join_1 = 1;
    var rt_join_2 = 1;
    var rt_join_3 = 1;
    var rt_join_4 = 1;

    if(location.href.indexOf("www.") != -1 ){
        location.href = location.href.replace("www.","");
    }

    $('#support-game-img').one("load", function() {

    }).each(function() {
        if (ww < 768) {
            var img_h = $(this).height();
            var img_w = $(this).width();
            $(this).css("height", img_h * 2 / 3);
            $(this).css("width", img_w * 2 / 3);
        }
        if(this.complete) $(this).load();
    });


    if (ww < wh){
        $('#hidden-row').height(0);
        $('#content').height('100%');
        $('#aside').height('100%');
        $('#content').css('margin-bottom', '20px');

    } else {
        $('#hidden-row').height(wh / 5);
    }

    if (ww > 1500) {
        $('#love-text').css('font-size', '35px');
    } else if (ww > 768) {
        $('#love-text').css('font-size', '27px');
    } else {
        $('#love-text').css('font-size', '20px');
        $('.join-info').css('font-size', '9px');

    }

    $('#button_login_signup').on("click", function() {
        $("form").each(function(){ if(this.id == "signupForm") this.reset(); });
        $('#button_signup_complete').html("회원가입!");
        $('#signup-aside').effect("slide", {direction: 'up', mode: 'show'}, 460);
        $('#aside').effect("slide", {direction: 'up', mode: 'hide'}, 460);
        if (ww < wh) {
            $('html,body').animate({scrollTop:$('#signup-aside').offset().top}, 500);
        }
        window.mixpanel.track("Try to sign up");
    });

    $('#button_signup_cancel').on("click", function() {
        mixpanel.track("Cancel to sign up");
        $('#signup-aside').effect("slide", {direction: 'down', mode: 'hide'}, 460);
        $('#aside').effect("slide", {direction: 'up', mode: 'show'}, 460);
        $('html,body').animate({scrollTop:$('html,body').offset().top}, 500);
    });

    $('#signup-aside #join_email').keyup(function(event){
        $.post("/home/join/chkEmail/?email=" + $('#signup-aside #join_email').val(), function(data) {
            if (data != "") {
                $('#signup-aside #join_email').tooltip('show');
                rt_join_1 = 0;
            } else {
                $('#signup-aside #join_email').tooltip('hide')
                rt_join_1 = 1;
            }
        });
        $("#div_signup_iderror").load("/home/join/chkEmail/?email="+$("#signup-aside #id_email").val());
    });

    $('#signup-aside #join_pw').keyup(function(event){
        if($(this).val().length<8) {
            $(this).tooltip('show');
            rt_join_2 = 0;
        } else {
            $(this).tooltip('hide');
            rt_join_2 = 1;
        }
    });

    $('#signup-aside #join_pw_confirm').keyup(function(event){
        if($(this).val() != $('#signup-aside #join_pw').val()) {
            $(this).tooltip('show');
            rt_join_3 = 0;
        } else {
            $(this).tooltip('hide');
            rt_join_3 = 1;
        }
    });

    $('#signup-aside #join_nick').keyup(function(event) {
        $.post("/home/join/chkNick/?nick=" + $(this).val(), function(data) {
            if (data != "") {
                $('#signup-aside #join_nick').tooltip('show');
                rt_join_4 = 0;
            } else {
                $('#signup-aside #join_nick').tooltip('hide');
                rt_join_4 = 1;
            }
        });
    });

    $('#button_signup_complete').click(function(){
        var val_username = $('#signup-aside #join_nick').val();
        var val_password1 = $('#signup-aside #join_pw').val();
        var val_email = $('#signup-aside #join_email').val();
        var curr_path = window.location.pathname;
        var path_array = curr_path.split('/');
        var inviter = '';

        if(path_array[0] == 'invite') {
            inviter = path_array[1];
        }

        if (rt_join_1 == 1 && rt_join_2 == 1 && rt_join_3 == 1 && rt_join_4 == 1 &&
            $('#signup-aside #join_email').val() != "" &&
            $('#signup-aside #join_pw').val() != "" &&
            $('#signup-aside #join_pw_confirm').val() != "" &&
            $('#signup-aside #join_nick').val() != "") {
            $('#button_signup_complete').html("<img src='/static/img/ajax-loader_btn.gif'>로딩 중...");
        }


        if($("#div_signup_iderror").text()==""&&$("#div_signup_passerror").text()==""&&$("#div_signup_passerror2").text()==""&&$("#div_signup_nickerror").text()==""&&
            $('._aside #id_email').val()!=""&&$('._aside #id_password1').val()!=""&&$('._aside #id_password2').val()!=""&&$('._aside #id_username').val()!=""){
            $('#button_signup_complete').html("<img src='/static/img/ajax-loader_btn.gif'>로딩 중...");
            $.post("/home/join/", {"csrfmiddlewaretoken":$('input[name=csrfmiddlewaretoken]').val(),"username":val_username,"password1":val_password1,"email":val_email,"inviter":inviter}, function(){
                location.href="/";
            });
        }

        $('#signup-aside #join_email').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
        $('#signup-aside #join_pw').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
        $('#signup-aside #join_pw_confirm').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
        $('#signup-aside #join_nick').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
    });
});

(function ($) {
    $.fn.alphanumeric = function(p) {
        p = $.extend({ ichars: "!@#$%^&*()+=[]\\\';,/{}|\":<>?~`.-_ ", nchars: "", allow: "" }, p);
        return this.each( function() {

            if (p.nocaps) p.nchars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
            if (p.allcaps) p.nchars += "abcdefghijklmnopqrstuvwxyz";
            s = p.allow.split('');
            for ( i=0;i<s.length;i++) if (p.ichars.indexOf(s[i]) != -1) s[i] = "\\" + s[i];
            p.allow = s.join('|');
            var reg = new RegExp(p.allow,'gi');
            var ch = p.ichars + p.nchars;
            ch = ch.replace(reg,'');
            $(this).keypress( function (e) {
                if (!e.charCode) k = String.fromCharCode(e.which);
                else k = String.fromCharCode(e.charCode);
                if (ch.indexOf(k) != -1) e.preventDefault();
                if (e.ctrlKey&&k=='v') e.preventDefault();

            });

            $(this).bind('contextmenu',function () {return false});
        });
    };
})(jQuery);