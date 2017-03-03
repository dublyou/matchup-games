$(document).ready(function () {
    'use strict';
    $("body").on("dblclick", ".matchup-member.competitor", function () {
        advance_competitor($(this));
    }).on("mousedown", ".matchup-member.competitor", function (e) {
        e.preventDefault();
    }).on("click", "#build_bracket", function () {
        var tourney_type = $("[name=tourney_type]:checked").val(),
            tourney_seeds = $("[name=tourney_seeds]:checked").val(),
            competitors = $("#competitors").val() == "" ? [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] : $("#competitors").val().trim().split(/\s*\n\s*/);
        build_bracket(tourney_type, tourney_seeds, competitors);
    }).on("change", "[name=view_options]", function () {
        if ($(this).is(":checked")) {
            $("." + $(this).val()).show();
        } else {
            $("." + $(this).val()).hide();
        }
    }).on("click", ".matchup-member.competitor>.advance-competitor", function () {
        advance_competitor($(this).parent(".matchup-member.competitor"));
    }).on("click", ".ui-slider-handle button", function (e) {
        var slider_range = $("#slider-range"),
            values = slider_range.slider("values"),
            bound = parseInt($(this).data("bound")),
            increment = parseInt($(this).data("increment")),
            new_value = values[bound] + increment,
            difference = values[bound] - values[Math.abs(bound - 1)];
        if (difference === 0) {
            values[Math.max(increment, 0)] = new_value;
            slider_range.slider("values", values);
        } else if (Math.max(difference * bound, difference * (bound - 1)) > 0) {
            values[bound] = new_value;
            slider_range.slider("values", values);
        }
    });
});
