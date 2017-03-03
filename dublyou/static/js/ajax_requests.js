(function() {
    "use strict";
    var cache = {};
    var target = ".search-dropdown input[type='text']"
    var search = function(e) {
        var $dropdown = $(this).closest(".search-dropdown").find(".search-results")
        var search_val = $(this).val().toLowerCase()
        if (search_val.length > 3) {
            if (true) {
                $.ajax({
                    type        : 'GET',
                    url         : '/profile/search/',
                    data        : {search_term : search_val},
                    dataType    : 'json'
                }).done(function(results) {
                    $dropdown.html(results)
                })
            } else {
                $dropdown.html($("#id_member").children("option").map(function(option, index) {
                    if (this.text.toLowerCase().includes(search_val)) {
                        return "<li><a>" + this.value + "</a></li>"
                    }
                }).get().join(""))
            }
            $dropdown.show()
        } else {
            $dropdown.empty()
            $dropdown.hide()
        }
    }

    var close_menu = function(e) {
        var $this = $(this)
        setTimeout(function(){
            $this.closest(".search-dropdown").find(".search-results").hide()
        }, 200);
    }

    var set_value = function(e) {
        e.preventDefault()
        var $parent = $(this).parent("li")
        var $search = $(this).closest(".search-dropdown")
        $(this).closest("input[type='hidden']").val($parent.prop("id"))
        $search.find("input[type='text']").val($parent.attr("data-display"))
    }
    $(document).on("keyup", target, search)
        .on("click", ".search-results li.select-option>a", set_value)
        .on("blur", target, close_menu)

})();

$(document).ready(function() {
    $("body").on("submit", "form.ajax", function(e) {
        e.preventDefault();
        var $form = $(this),
            form_data = {},
            form_action = $(this).prop("action"),
            form_method = $(this).prop("method"),
            target = $(this).data("target");

        $(this).find("input,select,textarea").each(function() {
            form_data[$(this).prop("name")] = $(this).val();
        });
        /*$("#popup .modal-content").html('<div class="modal-body"><div class="alert alert-info" role="alert">Loading...</div></div>');
        $('#popup').modal('show');*/
        $.ajax({
            type: form_method,
            url: form_action,
            data: form_data,
            dataType: 'json'
        }).done(function(data) {
            if (form_method.toLowerCase() == "post") {
                $("#popup .modal-content").html('<div class="modal-body"><div class="alert alert-success" role="alert">Success!</div></div>');
                setTimeout(function(){
                    location.reload();
                }, 200);
            } else {
                $("#popup .modal-content").html(data);
                $('#popup').modal('show');
            }
        }).fail(function(data) {
            if (form_method.toLowerCase() == "post") {
                var $error_alert = $(data.responseJSON),
                    $existing_alert = $form.find(".alert");
                if ($existing_alert.length > 0) {
                    $existing_alert.html($error_alert.html());
                } else {
                    $form.append($error_alert);
                }
            } else {
                $("#popup .modal-content").html(data.responseJSON);
                $('#popup').modal('show');
            }
        });
    }).on("click", ".ajax-link", function(e) {
        e.preventDefault();
        var get_url = $(this).prop("href");
        $.ajax({
            type: "get",
            url: get_url
        }).done(function(data) {
            $("#popup .modal-content").html(data);
            form_init($("#popup"));
        }).fail(function() {
            $("#popup .modal-content").html("Request failed.");
        });
        $('#popup').modal('show');
    });
});