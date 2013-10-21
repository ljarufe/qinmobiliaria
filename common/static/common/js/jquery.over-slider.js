(function($){
    $.fn.OverSlider = function(user_options) {
        // Opciones del usuario
        var options;
        // TODO: Autocalcular la altura de los divs
        options = {
            controls_container: $(this),
            height: 280,
            speed: 400
        };
        options = $.extend(options, user_options);

        // Cambiar el tamaño al slider
        $(this).css("height", options.height);

        // Cantidad de elementos en el slider sin contar al navegador
        var elem_selector = "div:not('." + options.controls_container.attr("class") + "')";
        var num_elem = $(this).children(elem_selector).size();

        // Coloca los botones de prev y next
        options.controls_container.append(
            "<div class='nav prev'><</div>" +
            "<div class='nav next'>></div>"
        );

        // Posición actual
        var position = 1;

        // Elementos
        var next = options.controls_container.children(".next");
        var prev = options.controls_container.children(".prev");
        var slider = $(this);

        next.click(function() {
            if(position < num_elem) {
                slider.animate({"scrollTop": "+=" + options.height}, options.speed);
                position++;
            }
            else{
                slider.animate({"scrollTop": "-=" + num_elem*options.height}, options.speed);
                position = 1;
            }
        });

        prev.click(function() {
            if(position > 1) {
                slider.animate({"scrollTop": "-=" + options.height}, options.speed);
                position--;
            }
            else{
                slider.animate({"scrollTop": "+=" + num_elem*options.height}, options.speed);
                position = num_elem;
            }
        });
    }
})(jQuery);
