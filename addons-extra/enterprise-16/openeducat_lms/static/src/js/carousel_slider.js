$(document).ready(function () {
    $(".owl-carousel").owlCarousel({
        loop: false,
        dots: false,
        nav: true,
        pagination: false,
        autoplay: false,
        margin: 20,
        navText: ['<button id="owl-prv" class="btn btn-primary fa fa-angle-left" data-toggle="tooltip" title="Prev"/>',
                  '<button id="owl-nxt" class="btn btn-primary fa fa-angle-right" data-toggle="tooltip" title="Next"/>'],
        responsiveClass: true,
        responsive: {
            768: {
                items: 2
            },
            979: {
                items : 2
            },
            479: {
                items : 1
            },
            320: {
                items : 1
            },
            1199: {
                items : 3
            },
        },
    });
});
