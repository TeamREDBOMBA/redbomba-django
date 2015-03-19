var query_no=0;
var feedSize = [
    ["30%","30%","40%"],
    ["50%","50%"],
    ["30%","30%","40%"],
    ["50%","50%"],
    ["30%","30%","40%"],
    ["50%","50%"],
    ["30%","30%","40%"],
    ["50%","50%"],
    ["30%","30%","40%"],
    ["50%","50%"],
    ["30%","30%","40%"],
    ["50%","50%"]
];

var reg = new RegExp('(#)([a-z0-9ㄱ-ㅎㅏ-ㅣ가-힣_]+)', 'gi');
var yt_reg = /((http:\/\/)|(https:\/\/))?(www.)?((youtube.com)|(youtu.be))\/(watch\?v=)?(\w+-?\w+)/;
var video_url = '';
var loadtime = '';
var pagex, pagey;
var dropzone;
var image_files = [];

$(document).ready(function() {

    moment.locale("ko");
    loadtime = moment().format("YYYY-MM-DD HH:mm:ss");

    $('#video-view').hide();

    //Dropzone.autoDiscover = false;
    //dropzone = new Dropzone("#dropzone", {url:'/main/add_post_image/', autoProcessQueue:false});
    //

    $('#dropzone').sortable({
        items: 'canvas',
        cursor: 'move',
        opacity: 0.5,
        containement: 'parent',
        distance: 20,
        tolerance: 'pointer'
    });

    $('#dropzone').on('click', function() {
        $('#hidden-file-input').click();
    });

    $('#hidden-file-input').fileupload({
        url: '/main/add_post_image/',
        sequentialUploads: true,
        dataType: 'json',
        autoUpload: false,
        acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
        maxFileSize: 5000000,
        disableImageResize: /Android(?!.*Chrome)|Opera/
            .test(window.navigator.userAgent),
        previewMaxWidth: 500,
        previewMaxHeight: 500,
        previewCrop: true
    }).on('fileuploadadd', function(e, data) {
        $.each(data.files, function(index, file) {
            console.log(file);
            image_files.push(file);
        });
    }).on('fileuploadprocessalways', function(e, data) {
        var index = data.index;
        var file = data.files[index];
        var node = $('#dropzone');
        if (file.preview) {
            if (node.find('p').length) { node.html(''); }
            node.append(file.preview);
        }
    }).on('fileuploadprogressall', function(e, data) {
    });


    loadPost('#col-2', 6);

    $('.stream-row').load('/load/stream/', {
        'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()
    });


    $('#input-textarea').on('click', function() {
        makeInputBoxWide();
    });

    $('#input-textarea').on('keyup', function() {
        if (video_url == '') {
            var urls = $(this).val().match(yt_reg);
            if (urls) {
                video_url = 'http://www.youtube.com/embed/' + urls[9];

                var yt_tag = '<div class=\"video-wrapper\"><iframe class=\"video-frame\" src=\"' + video_url + '\" frameborder=\"0\" allowfullscreen></iframe></div>';
                $('#video-view').show();
                $('#video-view').append(yt_tag);
            }
        }
    });

    $('.fa-camera').on('click', function() {
        makeInputBoxWide();
        $('#dropzone').removeClass('hidden');

    });


    $('#post-cancel-btn').on('click', function() {
        $(this).hide();
        $('#post-btn').hide();
        $('#input-box').hide();
        $('#dropzone').addClass('hidden');
        $('#dropzone').html('<p style="margin-top: 35px; font-size: 20px; font-weight: bold; color: gray;">여기를 클릭하거나 이미지를 끌어다 놓으세요.</p>');
        $('#input-box').appendTo($('#col-1').children('.row'));
        $('#input-box').show();
        if (video_url != '') {
            $('#input-box').find('.video-wrapper').remove();
            video_url = '';
            $('#video-view').hide();
        }
    });


    $('.fa').on('hover', function() {
        $(this).css('color', 'green');
    });


    $('#post-btn').on('click', function() {
        var text = $('#input-textarea').val();
        var tags = text.match(reg);
        for (var i in tags) {
            tags[i] = tags[i].slice(2,tags[i].length);
        }

        $.post('/main/new_post/', {
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),
            'content': $('#input-textarea').val(),
            'tags': tags,
            'gametag': $('#game-input').val(),
            'video': video_url
        }, function(res) {
            $('#hidden-file-input').fileupload({url:'/main/add_post_image/' + res});
            uploadFiles();
            //dropzone.options.url = '/main/add_post_image/' + res;
            //dropzone.processQueue();
            //alert(res);
        });
    });

    $('.game-list').on('click', function() {
        $('#game-input').val('#leagueoflegends');
    });

});

function uploadFiles() {
    uploadFile(image_files.pop());
}

function uploadFile(file) {
    if (file == null) {
        console.log('잉 파일이없잖아!!');
        return;
    }

    $('#hidden-file-input').fileupload('send', {files: [file]})
    .success(function(res, text, jqXHR) {
        console.log('성공');
        uploadFile(image_file.pop());
    }).error(function(res, text, jqXHR) {

    }).complete(function(res, text, jqXHR) {
        console.log('완료');
    });
}


$(document).on('mousemove', function(e) {
    pagex = e.pageX;
    pagey = e.pageY;
});


$(window).load(function() {
    $("#feed_pub").load("/card/global/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},function(){
        $('.focuspoint').focusPoint();
    });

    $("#feed_private").load("/card/private/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});

    $('#btnGamelink, #btnGamelink_s').click(function(){
        $('#GamelinkModal .modal-content').load("/head/gamelink/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});
        $('#GamelinkModal').modal('show');
    });

});

function makeInputBoxWide() {
    if ($('#input-box').parent().attr('id') != 'hidden-row') {
        $('#input-box').hide();
        $('#input-box').appendTo($('#hidden-row'));
        $('#input-box').show();
        $('#input-textarea').focus();
        $('#post-cancel-btn').show();
        $('#post-btn').show();
        $('.fa-camera').show();
        $('.fa-video-camera').show();
    }
}


function loadPost(ele, num) {
    var card = $('<div class=\"row\"><i class="fa fa-circle-o-notch fa-4x fa-spin"></i></div>');
    $(ele).append(card);

    card.load('/load/post/', {
            'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),
            'loadtime' : loadtime
        }, function() {

            if (card.find('#not-found').text()) return;

            $('.card .row .reply-btn').hide();
            $('.card .row .reply-cancel-btn').hide();
            $('.card .row .reply-profile-icon').hide();

            var from_now = moment($(this).find('#post-date').text(), "YYYY-MM-DD HH:mm:ss").fromNow();
            $(this).find('#post-date').text(from_now);
            from_now = moment($(this).find('#reply-time').text(), "YYYY-MM-DD HH:mm:ss").fromNow();
            $(this).find('#reply-time').text(from_now);

            var content = $(this).children('.card').children('.div-card-content').children('p').text();
            content = content.replace(reg, '<a href=\"#\">$1$2</a>');
            content = content.replace(yt_reg, function(x) {
                return '<a href=\"' + x + '\" target=\"_blank\" >' + x + '</a>';
            });
            $(this).find('.div-card-content').children('p').html(content);

            $(this).find('.smile-btn').on('click', function () {
                var count_btn = $(this).parent().children('.count-btn');

                if ($(this).hasClass('btn-warning')) {
                    $(this).removeClass('btn-warning');
                    count_btn.text(Number(count_btn.text()) - 1);
                    $.post('/main/del_smile/', {
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                        'postid': $(this).parent().parent().parent().attr('id')
                    });
                } else {
                    $(this).addClass('btn-warning');
                    count_btn.text(Number(count_btn.text()) + 1);
                    $.post('/main/new_smile/', {
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                        'postid': $(this).parent().parent().parent().attr('id')
                    });
                }
            });

            $(this).find('.input-reply').on('click', function () {
                $(this).css('height', '4em');
                $(this).addClass('input-reply-short');
                $(this).parent().children('.reply-btn').show();
                $(this).parent().children('.reply-cancel-btn').show();
                $(this).parent().children('.reply-profile-icon').show();
            });

            $(this).find('.reply-cancel-btn').on('click', function () {
                $(this).parent().children('.input-reply').css('height', '2.5em');
                $(this).parent().children('.input-reply').removeClass('input-reply-short');
                $(this).parent().children('.reply-btn').hide();
                $(this).parent().children('.reply-profile-icon').hide();
                $(this).hide();
            });

            $(this).find('.reply-btn').on('click', function () {
                var content = $(this).parent().children('.input-reply').val();

                $.post('/main/new_reply/', {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                    'postid': $(this).parent().parent().attr('id'),
                    'content': content
                });
            });

            $(this).find('.num-replys').on('click', function() {
                var rows = $('<div></div>');
                var post = $(this).parent().parent();
                rows.load('/load/reply/', {
                    'postid': post.attr('id')
                }, function(res) {
                    if (res == 'not more') {
                        post.find('.num-replys').removeClass('num-replys');
                    } else {
                        var replys = post.children('.div-card-reply').children(':first');
                        replys.before(rows);
                    }
                });
            });

            var timer;
            $(this).find('#post-icon, #post-username, #reply-icon, #reply-username').on('mouseenter', function() {
                var icon = $(this);
                var caller = '';
                var id;
                var popover;

                if($(this).attr('id').search('post') == -1) {
                    caller = 'reply';
                    id = icon.parent().parent().attr('id');
                    popover = icon.parent().parent().parent().parent().find('.profile-popover');
                } else {
                    caller = 'post';
                    id = icon.parent().parent().parent().attr('id');
                    popover = icon.parent().parent().parent().find('.profile-popover');
                }

                timer = setTimeout(function() {
                    popover.show();
                    popover.css('left', pagex - 5 + 'px');
                    popover.css('top', pagey - 5 - $(document).scrollTop() + 'px');
                    popover.load('/load/' + caller + '_profile/', {
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                        'id': id
                    }, function() {
                        $(this).find('.followed-btn').on('mouseenter', function() {
                            $(this).html('<i class="fa fa-user-times"></i> | 팔로우 끊기');
                        }).on('mouseleave', function() {
                            $(this).html('<i class="fa fa-check"></i> | 팔로우 중');
                        }).on('click', function() {
                            var paren = $(this).parent();
                            var btn = $(this);
                            var user_id = btn.parent().attr('id');
                            btn.replaceWith('<button class="btn btn-default" disabled><i class="fa fa-spin fa-spinner"></i> 요청 중..</button>');
                            btn = paren.find('.btn-default');
                            $.post('/main/unfollow/', {
                                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                                'userid': user_id
                            }, function() {
                                btn.replaceWith('<button class="btn btn-default" disabled><i class="fa fa-check"></i> 완료</button>');
                            });
                        });

                        $(this).find('.follow-btn').on('click', function() {
                            var paren = $(this).parent();
                            var btn = $(this);
                            var user_id = btn.parent().attr('id');
                            btn.replaceWith('<button class="btn btn-default" disabled><i class="fa fa-spin fa-spinner"></i> 요청 중..</button>');
                            btn = paren.find('.btn-default');
                            $.post('/main/follow/', {
                                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                                'userid': user_id
                            }, function() {
                                btn.replaceWith('<button class="btn btn-default" disabled><i class="fa fa-check"></i> 완료</button>');
                            });
                        });
                    });
                }, 1000);
            }).on('mouseleave', function() {
                clearTimeout(timer);
            });

            $(this).find('.profile-popover').on('mouseleave', function() {
                $(this).hide();
            });


            loadtime = $(this).find('#hidden-datetime').text();
            if (num > 1) {
                loadPost('#col-' + (num % 3 + 1), num - 1);
            }
        }
    );

}



function setSize(box_size){
    var count = 0;
    var arr = new Array();
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

