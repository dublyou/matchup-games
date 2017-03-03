$(document).ready(function () {
    'use strict';
    var tourney_type = $(".bracket-wrap").data("tourney_type"),
        tourney_seeds = 1,
        competitors = $(".bracket-wrap").data("competitors"),
        winners = $(".bracket-wrap").data("winners"),
        losers = $(".bracket-wrap").data("losers");
    build_bracket(tourney_type, tourney_seeds, competitors, winners, losers);
    $("body").on("change", "[name=view_options]", function () {
        if ($(this).is(":checked")) {
            $("." + $(this).val()).show();
        } else {
            $("." + $(this).val()).hide();
        }
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
