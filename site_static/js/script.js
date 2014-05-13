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


    //-----------------Корзина-----------------//


    $(".cart-item__amount").on('MozMousePixelScroll mousewheel', function (event, delta) {
        var cur_value = $(this).val();
        var delta = event.originalEvent.wheelDelta;
        var deltaMoz = event.originalEvent.detail;
        if (event.type === "mousewheel") {
            if (delta > 0) {
                cur_value = parseInt(cur_value) + 1;
                $(this).attr('value', cur_value);
                $(this).val(cur_value);

            } else {
                if (cur_value > 1) {
                    cur_value = parseInt(cur_value) - 1;
                    $(this).attr('value', cur_value);
                    $(this).val(cur_value);
                }

            }
        }
        if (event.type === "MozMousePixelScroll") {
            if (deltaMoz < 0) {
                if (cur_value > 0) {
                    cur_value = parseInt(cur_value) - 1;
                    $(this).attr('value', cur_value);
                    $(this).val(cur_value);
                }

            } else {
                cur_value = parseInt(cur_value) + 1;
                $(this).attr('value', cur_value);
                $(this).val(cur_value);
            }
        }
        sumCart();
        return false;

    });
    $(".cart-item__remove").click(function () {
        var totalSize = 0;
        var price = parseInt($(this).parents(".cart-item").find(".cart-item__price_all").html());
        var size = $(this).parents(".cart-item").find(".cart-item__amount").val();
        $(".cart-item__amount").each(function () {
            totalSize += parseInt($(this).val());
        });
        var newSize = totalSize - size;
        $(".cart-side__items-amount").html(newSize);
        var total = parseInt($(".tovar-price._sum").html().replace(/\s+/g, ''));
        var newTotalPrice = total - price + '';
        var totalNew = newTotalPrice.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
        $(".tovar-price._sum").html(totalNew);
        $(".cart-side__items-sum").html(totalNew);
        $(this).parents(".cart-item").remove();
        checkNumber()
    });


    $(".cart-item__amount").on('change blur keyup input mousewheel', function () {
        this.value = this.value.replace(/[^0-9+()]/g, '');
        var amount = parseInt($(this).val() * 1);
        var price = parseInt($(this).parents('.cart-item').find(".cart-item__price").html());
        var sum = amount * price;
        $(this).parents('.cart-item').find(".cart-item__price_all").html(sum);
        sumCart();

    });

    function sumCart() {
        var count = 0;
        var size = 0;
        $(".cart-item__price_all").each(function () {
            count += parseInt($(this).html());

        });
        $(".cart-item__amount").each(function () {
            size += parseInt($(this).val());
        });
        count = count + '';
        var countNew = count.replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
        $(".tovar-price._sum").html(countNew);
        $(".cart-side__items-sum").html(countNew);
        $(".cart-side__items-amount").html(size);
        checkNumber()
    }

    sumCart();

    function checkNumber() {
        var term = $(".cart-side__items-amount").html();

        var num = term.slice(-1);
        if (num == 1) {
            $(".cart-side__items-amount").html(term + ' товар');
        }
        else if (num == 2 || num == 3 || num == 4) {
            $(".cart-side__items-amount").html(term + ' товара');
        }

        else {
            $(".cart-side__items-amount").html(term + ' товаров');
        }

        if (term > 10 && term < 20) {
            $(".cart-side__items-amount").html(term + ' товаров');
        }
    }

    $(".search-switch").click(function(){
        $(".search__block-items__hidden").slideToggle();
        $(".search-switch").toggleClass("opened")
    })


});