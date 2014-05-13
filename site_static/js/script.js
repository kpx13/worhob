$(function () {
    var slide = $(".content__slider__i");
    var slideSize = slide.size();
    var speed = 1000; //время появления слайда
    var time = 6000; // промежуток времени,через которое меняются слайды
    var slideNext = $(".content__slider__next");
    var slidePrev = $(".content__slider__prev");
    slide.not(":first").hide();

    function rotate() {
        var k = $(".content__slider__i.active").index();
        if (k < slideSize - 1) {
            slide.eq(k).fadeOut(speed).removeClass("active").next().dequeue().fadeIn(speed).addClass("active");
        }
        else {
            slide.eq(k).fadeOut(speed).removeClass("active");
            slide.eq(0).dequeue().fadeIn(speed).addClass("active");
        }

    }

    var autoplay = setInterval(rotate, time);

    var title = $(".block__title");
    title.click(function () {
        var switchBlock = $(this).parent().find(".block__hidden");
        if (switchBlock.is(":visible")) {
            switchBlock.slideUp();
            $(this).removeClass("active");
        }
        else {
            switchBlock.slideDown();
            $(this).addClass("active");
        }
    });
    slideNext.click(function () {
        clearInterval(autoplay);
        if (!slide.is(":animated")) {
            rotate();
            autoplay = setInterval(rotate, time);
        }
    });
    slidePrev.click(function () {
        clearInterval(autoplay);
        if (!slide.is(":animated")) {
            var k = $(".content__slider__i.active").index();
            if (k > 0) {
                slide.eq(k).fadeOut(speed).removeClass("active").prev().dequeue().fadeIn(speed).addClass("active");
            }
            else {
                slide.eq(k).fadeOut(speed).removeClass("active");
                slide.eq(-1).dequeue().fadeIn(speed).addClass("active");
            }
            autoplay = setInterval(rotate, time);
        }
    });

    $(".search-switch").click(function(){
        $(".search__block-items__hidden").slideToggle();
        $(".search-switch").toggleClass("opened")
    })


});