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

$(window).load(function() {

    $("#feed_pub").load("/card/global/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()},function(){
        $('.focuspoint').focusPoint();
    });

    $('#btnGamelink, #btnGamelink_s').click(function(){
        $('#GamelinkModal .modal-content').load("/head/gamelink/",{'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val()});
        $('#GamelinkModal').modal('show');
    });

});

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