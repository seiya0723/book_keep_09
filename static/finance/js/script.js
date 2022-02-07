window.addEventListener("load" , function (){

  

    let config_pay_date   = {
        "locale": "ja"
    }
    flatpickr("[name='pay_date']", config_pay_date);

    $('.tab-content>div').hide();
    $('.tab-content>div').first().slideDown();

    $('.tab-buttons>span').click(function(){
        var thisclass=$(this).attr('class');
        $('#lamp').removeClass().addClass('#lamp').addClass(thisclass);
        $('.tab-content>div').each(function(){
            if($(this).hasClass(thisclass)){
                $(this).fadeIn(500);
            }
            else{
                $(this).hide();
            }
        });

        $(".tab-buttons > span").css({"background":""});    
        $(this).css({"background":"gray"});

    });
    
    /*
    $('.tab-buttons > span').click(function(){
        $(".tab-buttons > span").removeClass("tab_selected");    
        $(this).addClass("tab_selected");
    });
    */
    
    //DjangoMessageFrameWorkの削除機能
    $(".message_delete").on("click", function(){ $(this).parent(".message").remove(); });

    document.getElementById('#free').style.visibility = 'visible';

});
