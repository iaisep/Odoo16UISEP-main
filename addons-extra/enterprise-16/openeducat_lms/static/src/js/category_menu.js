$(document).ready(function () {
    var elemWidth, fitCount, varWidth = 0, ctr,
        $menu = $("ul#menu"), $collectedSet;

    ctr = $menu.children().length;
    $menu.children().each(function() {
        varWidth += $(this).outerWidth();
    });

    collect();
    $(window).resize(collect);

    function collect() {
        elemWidth = $menu.width();
        fitCount = Math.floor((elemWidth / varWidth) * ctr) - 1;
        $menu.children().css({"display": "block", "width": "auto"});
        $collectedSet = $menu.children(":gt(" + fitCount + ")");
        if($collectedSet.length >= 1){
            $('.category-menu__link').find('ol').removeAttr("style");
        }
        $("#submenu").empty().append($collectedSet.clone());
        //$collectedSet.css({"display": "none", "width": "0"});
    }
    // Get the modal
    var modal = document.getElementById('id01');

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }


/*See More And Lees More Button JS*/
    var text_height = $('.text-overflow').height();
    if(text_height > 330){

        var text = $('.text-overflow'),
         btn = $('.btn-overflow'),
           h = text[0].scrollHeight;
         $('.text-overflow').css('height', '330px');

        if(h > 120) {
            btn.addClass('less');
            btn.css('display', 'block');
        }

        btn.click(function(e)
        {
          e.stopPropagation();

          if (btn.hasClass('less')) {
              btn.removeClass('less');
              btn.addClass('more');
              btn.text('Show less');

              text.animate({'height': h});
          } else {
              btn.addClass('less');
              btn.removeClass('more');
              btn.text('Show more');
              text.animate({'height': '330px'});
          }
        });
    }
    var src_link = $(".audio").attr("src");
    $('.videoToggleOff').on('hidden.bs.modal',function(){
        $('audio').attr('src','');
        $('audio').attr('src',src_link);
    });
});
