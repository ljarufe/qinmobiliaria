$(document).ready(function() {
    $("#recuperar_pass").jqm({
        trigger: $(".recuperar_link")
    });
    $("#recuperar_pass").jqmHide();
    $('.closeClass').click(function() {
        $('.jqmWindow').jqmHide();
    });
});