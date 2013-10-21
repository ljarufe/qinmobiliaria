(function($){
	$.fn.SearchBox = function(json_fastquery, on_enter_method, user_options) {
		
		var options;

		options = {	normal_bg_color: '#FFFFFF',
					normal_font_color: '#676767',
					select_bg_color: '#C70F2D',
					select_font_color: 'white',
					box_img: '/servicios/recursos/lupa.png'
				  };
				  
		options = $.extend(options, user_options);

		var items_busqueda = new Array();
		var index_busqueda = 0;
        var old_length = 0;
		var current = 0;
		
		// Changing the id of the input field
		$(this).attr('id', 'search_box_input');
		
		// Autocomplete off
		$(this).attr('autocomplete', 'off');
		
		// Use the options
//        $(this).css('backgroundImage', 'url(' + options.box_img + ')');
        $(this).css('background-position', 'right center');
		
		// Draw result area
		$(this).before("<div class='search_box_all'><ul></ul></div>");

        // Set absolute position
        var top = $(this).offset().top + $(this).height() + 12;
        $(".search_box_all").css("top", top + "px");
        $(".search_box_all").css("left", $(this).offset().left);

        // Set width
        var width = $(this).width() + 6;
        $(".search_box_all").css("width", width);
        $(".search_box_item_name").css("width", width);
		
		// Search
		$(this).keyup(function(event) {
            var buscar = $(this).val();
            if(old_length != buscar.length) {
                old_length = buscar.length;
                var key = event.keyCode;

                var temp_current;
                // down key
                if(key == 38) {
                    temp_current = "#" + current;
                    $(temp_current).parent().css("background-color", options.normal_bg_color);
                    $(temp_current).parent().css("color", options.normal_font_color);
                    current = items_busqueda[(--index_busqueda)%items_busqueda.length];
                    temp_current = "#" + current;
                    $(temp_current).parent().css("background-color", options.select_bg_color);
                    $(temp_current).parent().css("color", options.select_font_color);
                    return false;
                }

                // up key
                if(key == 40){
                    temp_current = "#" + current;
                    $(temp_current).parent().css("background-color", options.normal_bg_color);
                    $(temp_current).parent().css("color", options.normal_font_color);
                    current = items_busqueda[(++index_busqueda)%items_busqueda.length];
                    temp_current = "#" + current;
                    $(temp_current).parent().css("background-color", options.select_bg_color);
                    $(temp_current).parent().css("color", options.select_font_color);
                    return false;
                }

                // Show action - editable
                if(key == 13) {
                    if(current != 0) {
                        $('.search_box_all').slideUp('fast');
                        on_enter_method(current);
                        return false;
                    }
                }

                // Fill the Result area using json responses
                if(buscar == '') {
                    $('.search_box_all').hide();
                }
                else {
                    var index = 0;
                    $('.search_box_all > ul').html('');
                    items_busqueda = new Array();
                    var request = $.ajax({
                        url: json_fastquery,
                        type: "GET",
                        data: {substring: buscar},
                        dataType: "html"
                    });
                    request.done(function(msg) {
                        var items = jQuery.parseJSON(msg);
                        for(i = 0 ; i < items.length ; i++) {
                            $('.search_box_all > ul').append("<li><div class='search_box_item' id='" + items[i].id + "' title='" + items[i].description + "'><img src='" + items[i].image + "' width='40px' height='40px' /><div class='search_box_item_name'><p>" + items[i].name + "</p><div class='search_box_type'>" + items[i].subtitle + "</div></div><div class='clear'></div></div></li>");
                            items_busqueda[index] = items[i].id;
                            index++;
                        }
                    });
                    index_busqueda = Math.pow(index, 4) - 1;
                    $('.search_box_all').slideDown('fast');
                }
            }
		});
		
		// highlight and de-highlight item
		$('.search_box_item').live('mouseover', function(){
			$(this).parent().css("background-color", options.select_bg_color);
			$(this).parent().css("color", options.select_font_color);
		});
		$('.search_box_item').live('mouseleave', function(){
			$(this).parent().css("background-color", options.normal_bg_color);
			$(this).parent().css("color", options.normal_font_color);
		});

		// Show action - editable
		$('.search_box_item').live('click', function(){
			on_enter_method($(this).attr('id'));
			$('.search_box_all').slideUp('fast');
			return false;
		});

		// Close search result
		$('*').not('.search_box_item').click(function(){
			$('.search_box_all').slideUp('fast');
		});
	}
})(jQuery);
