var theInt = null;
var $crosslink, $navthumb;
var curclicked = 0;

theInterval = function(cur){
        clearInterval(theInt);

        if( typeof cur != 'undefined' )
                curclicked = cur;

        $crosslink.removeClass("active-thumb");
        $navthumb.eq(curclicked).parent().addClass("active-thumb");
                $(".stripNav ul li a").eq(curclicked).trigger('click');

        theInt = setInterval(function(){
                    $crosslink.removeClass("active-thumb");
                    $navthumb.eq(curclicked).parent().addClass("active-thumb");
                    $(".stripNav ul li a").eq(curclicked).trigger('click');
                    curclicked++;
                    if( tour_items_count == curclicked ){
                        // clearInterval(theInt);
                        curclicked = 0;
                    }

            }, tour_interval);
};

function run_slider(){
    $navthumb = $(".nav-thumb");
    $crosslink = $(".cross-link");
    $navthumb
    .click(function() {
            var $this = $(this);
            theInterval($this.parent().attr('href').slice(1) - 1);
            return false;
    });

    theInterval(0);
}

$(function(){
    //run_slider();
});
