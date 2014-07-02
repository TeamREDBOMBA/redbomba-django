$(document).ready(function(){
  $("body").mousemove(function(e){
    var w = e.pageX/$(document).width()*10;
    var h = e.pageY/$(document).height()*10;
    var t = (($("#img_main_bg_eyes").scrollTop()+168)+h);
    var l = (($("#img_main_bg_eyes").scrollLeft()-430)+w);
    $("#img_main_bg_eyes").css({"top":t,"left":l});
  })
});

$(window).load(function() {
  $('#button_login_signup').click(function(){
   // alert("2014년 4월 25일 정식서비스를 기다려주세요.\nCOMING SOON!");
    
    $("form").each(function(){ if(this.id == "signupForm") this.reset(); });
    $("#div_signup_iderror").text("");
    $("#div_signup_passerror").text("");
    $("#div_signup_passerror2").text("");
    $("#div_signup_nickerror").text("");
    $('#backBG').show();
    $('._aside').show();
    $('._aside').animate({"right":"0%"}, 'slow');
    
    });
    
  $('#button_signup_cancle').click(function(){
    $('._aside').animate({"right":"-800px"}, 'slow', function(){
      $('._aside').hide();
      $('#backBG').hide();
      });
    });
    
  $('._aside #id_email').keyup(function(event){
    $("#div_signup_iderror").load("/auth/fnc/email/?email="+$("._aside #id_email").val());
    });
    
  $('._aside #id_password1').keyup(function(event){
    if($(this).val().length<8) $("#div_signup_passerror").text("비밀번호는 8자리 이상이어야 합니다.");
    else $("#div_signup_passerror").text("");
    });
    
  $('._aside #id_password2').keyup(function(event){
    if($(this).val()!=$('._aside #id_password1').val()) $("#div_signup_passerror2").text("비밀번호가 일치하지 않습니다.");
    else $("#div_signup_passerror2").text("");
    });
    
  $('._aside #id_username').keyup(function(event){
    $("#div_signup_nickerror").load("/auth/fnc/nick/?nick="+$("._aside #id_username").val());
    });
    
  $('#button_signup_complete').click(function(){
    if($("#div_signup_iderror").text()==""&&$("#div_signup_passerror").text()==""&&$("#div_signup_passerror2").text()==""&&$("#div_signup_nickerror").text()==""&&
    $('._aside #id_email').val()!=""&&$('._aside #id_password1').val()!=""&&$('._aside #id_password2').val()!=""&&$('._aside #id_username').val()!=""){
      $('#signupForm').submit();
      }
    });
    
  $('._aside #id_email').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
  $('._aside #id_password1').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
  $('._aside #id_password2').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
  $('._aside #id_username').alphanumeric($.extend({ ichars: " ", nchars: "", allow: "" }));
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
