$(function() {

    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});

function action_trigger(event_type, $this) {
    'use strict';
    
    var data_action = $this.data("action-" + event_type)
    var data_trigger = $this.prop("id")
    data_trigger = (data_trigger.startsWith("id_")) ? data_trigger.slice(3) : data_trigger

    $("[data-trigger*='" + data_trigger + "']").each(function() {
      var action_criteria = $(this).data(data_action)
      var criteria_match = true
      var group = $(this).data("group")
      var $target = (group) ? $(this).closest(group) : $(this)
      for (var id in action_criteria) {
        criteria_match = false
        var criteria = action_criteria[id]
        var id_value = $("[name='" + id + "']").val()
        for (var i = 0; i < criteria.length; i++) {
          if (criteria[i] == id_value) {
            criteria_match = true;
            break
          }
        }
        if (!criteria_match) break
      }
      if (criteria_match) {
        $target.show()
      } else {
        $target.hide()
      }
    })
  }

function sortable_initialize() {
    var fixHelper = function(e, tr) {
        var $originals = tr.children();
        var $helper = tr.clone();
        $helper.children().each(function(index)
        {
          $(this).width($originals.eq(index).width())
        });
        return $helper;
    };
    $(".sortable").sortable({
        helper: fixHelper,
        update: function( event, ui ) {
            $(this).children().each(function(i) {
                $(this).children("td#seed").html(i+1);
            });
        }
    }).disableSelection();
}

(function ($) {
    // Define the function here
    $.fn.copyAllAttributes = function (sourceElement) {
        // 'that' contains a pointer to the destination element
        var that = this;

        // Place holder for all attributes
        var allAttributes = $(sourceElement).prop("attributes");

        if (allAttributes && $(that).length == 1) {
            $.each(allAttributes, function () {
                // Ensure that class names are not copied but rather added
                if(this.name == "class"){
                    that.addClass(this.value);
                } else {
                    that.attr(this.name, this.value);
                }
            });
        }
        return that;
    };
})(jQuery);

function getWidthOfText(txt, fontname, fontsize){
    // Create a dummy canvas (render invisible with css)
    var c=document.createElement('canvas');
    // Get the context of the dummy canvas
    var ctx=c.getContext('2d');
    // Set the context.font to the font that you are using
    ctx.font = fontsize + 'px' + fontname;
    // Measure the string
    // !!! <CRUCIAL>  !!!
    var length = ctx.measureText(txt).width;
    // !!! </CRUCIAL> !!!
    // Return width
    return length;
}

function properCase (str) {
  if ((str===null) || (str==="")) {
       return false;
  } else {
   str = str.toString();
  }

 return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

(function($) {
  $.fn.hasProp = function(prop_name) {
    var data_regex = /^data-([_-\w]+)$/;
    if (data_regex.test(prop_name)) {
        var data_name = prop_name.match(data_regex);
        var prop_val = $(this).data(data_name[1]);
    } else {
        var prop_val = $(this).prop(prop_name);
    }

    return (prop_val !== null && prop_val !== "");
  };
})(jQuery);

(function($) {
  $.fn.outerHTML = function(s) {
      return (s) ? this.before(s).remove() : $("<p>").append(this.eq(0).clone()).html();
  };
})(jQuery);

(function ($) {
    $.fn.customToggle = function (toggle,effect,delay) {

        delay = (delay === null) ? 0 : delay;

        if (toggle == null) {
            toggle = !($(this).is(":visible"));
        }

        if ($(this).hasProp("data-transition")) {
            effect = (effect == null) ? $(this).data("transition") : effect;
        }

        var options = {};

        switch (effect) {
            case "slideDown":
            case "slideUp":
            case "slideRight":
            case "slideLeft":
                options = { direction: effect.slice(5).toLowerCase() };
                effect = "slide";
            default:

        }

        if (toggle) {
            $(this).addClass("visible").removeClass("hidden");
        }

        if (effect == null) {
            if (toggle) {
                $(this).delay(delay).show(500);
            } else {
                $(this).delay(delay).hide(500);
            }
        } else {
            if (toggle) {
                $(this).delay(delay).show(effect,options,500);
            } else {
                $(this).delay(delay).hide(effect,options,500);
            }
        }

        if (!toggle) {
            setTimeout(function() {
                $(this).removeClass("visible").addClass("hidden");
            }, 500);
        }
    };
})(jQuery);

(function ($) {
    $.each(['show', 'hide', 'slideDown', 'slideUp', 'fadeIn', 'fadeOut','effect'], function (i, ev) {
        var el = $.fn[ev];
        $.fn[ev] = function () {
            this.trigger(ev);
            return el.apply(this, arguments);
        };
    });
})(jQuery);

(function ($) {
    $.fn.validateCriteria = function () {
        var criteria_str = $(this).data("criteria");
        var hasCriteria = (criteria_str !== null && criteria_str !== "optional" && criteria_str);
        if (hasCriteria) {
            if ($(this).is("select")) {
                $(this).children("option").each(function() {
                    if (!check_criteria($(this).val(),criteria_str)) {
                        $(this).prop("disabled",true);
                    } else {
                        $(this).prop("disabled",false);
                    }
                });
            }

            if (!check_criteria($(this).val(),criteria_str)) {
                $(this).val("");
            }
        } else {
            if ($(this).is("select")) {
                $(this).children("option").prop("disabled",false);
            }
        }
    };
})(jQuery);

function check_criteria(value,criteria) {
    var inequality_regex = /^(!?)\[(<|>)(-?[\d]+)\]$/;
    var range_regex = /^(!?)\[(-?[\d]+)-(-?[\d]+)\]$/;
    var list_regex = /^(!?)\[([-\d\w]+(?:\s*,\s*[-\d\w]+)*)\]$/;
    var regex_pattern = /^\/(\S+)\/$/;

    if (criteria == null) {
        return true;
    } else if (value == null || value == "") {
        return false;
    } else if (inequality_regex.test(criteria)) {
        var matches = criteria.match(inequality_regex);
        return eval(matches[1] + "(" + value + matches[2] + matches[3] + ")");
    } else if (range_regex.test(criteria)) {
        var matches = criteria.match(range_regex);
        return eval(matches[1] + "(" + value + " >= " + matches[2] + " && " + value + " <= " + matches[3] + ")");
    } else if (list_regex.test(criteria)) {
        var matches = criteria.match(list_regex);
        var list_vals = matches[2].split(/\s*,\s*/);
        var inverse = matches[1];
        var list_match = eval(inverse + false);
        for (i = 0; i < list_vals.length; i++) {
            if (list_vals[i] == value) {
                list_match = eval(inverse + true);
                break;
            }
        }
        return list_match;
    } else if (regex_pattern.test(criteria)) {
        var matches = criteria.match(regex_pattern);
        var regex_criteria = new RegExp(matches[1]);
        return regex_criteria.test(value);
    } else if (criteria != null) {
        if (criteria.slice(0,1) == "!") {
            return (criteria.slice(1) != value);
        } else {
            return (criteria == value);
        }

    }
}

function parse_action_class(action_class) {

    var action_args = new Array();
    var action_initializer = "(?:d|i)-action";
    var action_name = ":([-\\d\\w]+)";
    var action_criteria = "(?:==(?:\\/\\S+\\/|!?\\[(?:(?:<|>)\\-?\\d+|\\-?\\d+\\-\\-?\\d+|[-\\d\\w]+(?:,[-\\d\\w]+)*)\\]|!?[-\\d\\w]+))?";
    var action_source = "((?::_[-\\d\\w]+" + action_criteria + ")+)";
    var action_variables = "(?::(\\[[-\\d\\w]+=[^,\\s]+(?:,[-\\d\\w]+=[^,\\s]+)*\\]))?";

    var action_parse_regex = new RegExp(action_initialize + action_name + action_source + action_variables);

    var action_parsed = action_class.match(action_parse_regex);

    action_args["action_name"] = action_parsed[1];

    var conditions = action_parsed[2];
    var condition_regex = new RegExp(":_([-\\d\\w]+)(?:==(\\/\\S+\\/|!?\\[(?:(?:<|>)\\-?\\d+|\\-?\\d+\\-\\-?\\d+|[-\\d\\w]+(?:,[-\\d\\w]+)*)\\]|!?[-\\d\\w]+))?");
    var condition = {};
    action_args["conditions_met"] = true;

    while (condition = condition_regex.exec(conditions)) {
        if (condition[0] != null) {
            action_args["conditions_met"] = check_criteria($("#" + condition[0]).val(), condition[1]);
        }
        if (!action_args["conditions_met"]) break;
    }

    if (action_parsed[3]) {
        var action_vars = action_parse[3].split(",");
        var action_var_regex = /^([-\d\w]+)=([^,\s]+)$/;
        for (i = 0; i < action_vars.length; i++) {

            var action_var = action_vars[i].match(action_var_regex);
            action_var[2] = action_var[2].replace("&sp;"," ");

            try {
                action_var[2] = eval(action_var[2]);
            }
            catch (err) {}
            finally {
                action_args[action_var[1]] = action_var[2];
            }
        }
    }

    return action_args;
}

function action_sweep(target_classes,target_action_args) {

    var action_criteria = "(?:==(?:\\/\\S+\\/|!?\\[(?:(?:<|>)\\-?\\d+|\\-?\\d+\\-\\-?\\d+|[-\\d\\w]+(?:,[-\\d\\w]+)*)\\]|!?[-\\d\\w]+))?";
    var action_source = "(?::_[-\\d\\w]+" + action_criteria + ")+";
    var action_variables = "(?::\\[[-\\d\\w]+=[^,\\s]+(?:,[-\\d\\w]+=[^,\\s]+)*\\])?";

    var d_action_regex = /("d-action" + target_action_args["action_name"] + action_source + action_variables,"g")/;
    var i_action_regex = /("i-action" + target_action_args["action_name"] + action_source + action_variables,"g")/;

    var conditions_met = false;
    var action_class = {};

    while (action_class = i_action_regex.exec(target_classes)) {
        var action_args = parse_action_class(action_class[0]);

        if (action_args["conditions_met"]) {
            conditions_met = true;
            break;
        }
    }

    if (!conditions_met) {
        while (action_class = d_action_regex.exec(target_classes)) {
            conditions_met = true;
            var action_args = parse_action_class(action_class[0]);

            if (!action_args["conditions_met"]) {
                conditions_met = false;
                break;
            }
        }
    }

    return conditions_met;
}


(function ($) {
    $.fn.triggerAction = function () {

        var action_valid = true;
        var error_message;

        if ($(this).hasClass("input-validate")) {
            action_valid = validate_inputs($(this).closest("form"));
        }

        $(this).closest("form").find(".alert").customToggle(!action_valid,"fade");

        if (action_valid) {
            var action_id = $(this).prop("id");

            $("[class*='" + action_id + "']").each(function() {

                var action_initializer = "(?:d|i)-action";
                var action_name = ":[-\\d\\w]+";
                var action_criteria = "(?:==(?:\\/\\S+\\/|!?\\[(?:(?:<|>)\\-?\\d+|\\-?\\d+\\-\\-?\\d+|[-\\d\\w]+(?:,[-\\d\\w]+)*)\\]|!?[-\\d\\w]+))?";
                var action_source = "(?::_[-\\d\\w]+" + action_criteria + ")*";
                var action_variables = "(?::\\[[-\\d\\w]+=[^,\\s]+(?:,[-\\d\\w]+=[^,\\s]+)*\\])?";

                var target_classes = $(this).prop("class");
                var target_class_regex = /(action_initializer + action_name + action_source + ":_" + action_id + action_criteria + action_source + action_variables,"g")/;

                var target_class = target_classes.match(target_class_regex);
                if (target_class == null) {
                    alert("Invalid action class.\n\n" + $(this).outerHTML());
                }
                var action_args = parse_action_class(target_class[0]);

                var action_criteria_match = action_sweep(target_classes,action_args);

                switch (action_args["action"]) {
                    case "toggle":
                        $(this).customToggle(action_criteria_match,action_args["transition"]);
                        break;
                    case "display":
                        if (action_criteria_match) {
                            $(this).customToggle(true,action_args["transition"]);
                        }
                        break;
                    case "dismiss":
                        if (action_criteria_match) {
                            $(this).customToggle(false,action_args["transition"]);
                        }
                        break;
                    case "criteria":
                        if (action_criteria_match && action_args["input_criteria"] != null) {
                            $(this).data("criteria",action_args["input_criteria"]);
                            $(this).validateCriteria();
                        } else {
                            if (action_args["default_val"] == null) {
                                $(this).removeData("criteria");
                            } else {
                                $(this).data("criteria",action_args["default_val"]);
                            }
                            $(this).validateCriteria();
                        }
                        break;
                    case "add-prop":
                        if (action_criteria_match && action_args["prop"] != null && action_args["prop_val"] != null) {
                            if(action_args["prop"] == "class"){
                                $(this).addClass(action_args["prop_val"]);
                                if (action_args["default_val"] != null) {
                                    $(this).removeClass(action_args["default_val"]);
                                }
                            } else if (action_args["prop"].slice(0,5) == "data-") {
                                $(this).data(action_args["prop"].slice(5), action_args["prop_val"]);
                            } else {
                                $(this).prop(action_args["prop"], action_args["prop_val"]);
                            }
                        } else if (action_args["prop"] != null && action_args["prop_val"] != null) {
                            if(action_args["prop"] == "class") {
                                $(this).removeClass(action_args["prop_val"]);
                                if (action_args["default_val"] != null) {
                                    $(this).addClass(action_args["default_val"]);
                                }
                            } else if (action_args["prop"].slice(0,5) == "data-") {
                                if (action_args["default_val"] == null) {
                                    $(this).removeData(action_args["prop"]);
                                } else {
                                    $(this).data(action_args["prop"], action_args["default_val"]);
                                }
                            } else {
                                if (action_args["default_val"] == null) {
                                    $(this).removeProp(action_args["prop"]);
                                } else {
                                    $(this).prop(action_args["prop"], action_args["default_val"]);
                                }
                            }
                        }
                        break;
                    case "clone-build":
                        if (action_criteria_match) {
                            $(this).cloneBuild(action_args["clones"],action_args["clone_stem"],action_args["clone_leaf"]);
                        }
                        break;
                    case "re-number-inputs":
                        if (action_criteria_match) {
                            var input_count = {};
                            var collection_name = $(this).prop("id");
                            var collect_name_regex = new RegExp("^" + collection_name + "\\d+_([\\w\\d]+)$");
                            $(this).find("input[name*='" + collection_name + "'],select[name*='" + collection_name + "'],textarea[name*='" + collection_name + "']").each(function () {
                                var input_name = $(this).prop("name");
                                if (collect_name_regex.test(input_name)) {
                                    var input_name_match = input_name.match(collect_name_regex);
                                    if (input_count[input_name_match[1]] == null) {
                                        input_count[input_name_match[1]] = 1;
                                    } else {
                                        input_count[input_name_match[1]]++;
                                    }
                                    $(this).prop("name", collection_name + input_count[input_name_match[1]] + input_name_match[1])
                                }
                            });
                        }
                        break;
                    default:
                        if (action_criteria_match) {
                            eval("$(this)." + action_args["action"] + "(action_args['function_vals']);");
                        } else {
                            if (action_args["default_vals"] !== null) {
                                eval("$(this)." + action_args["action"] + "(action_args['default_vals']);");
                            }
                        }
                        break;
                }
            });
        }
    };
})(jQuery);

(function ($) {
    $.fn.cloneBuild = function (clones,clone_stem,clone_leaf) {
        if ($(this).hasClass("clone-build")) {
            var clone_html = $(this).clone().addClass("clone").removeClass("clone-build").outerHTML();
            var stem_leaf_regex = new RegExp(clone_stem + clone_leaf,"g");

            if (clones != null) {
                $(this).siblings(".clone").remove();
            } else {
                clones = $(this).siblings().length + 1;
            }

            var clone_start = $(this).siblings().length + 1;

            for (i = clone_start; i < clones; i++) {

                var clone = clones - i + clone_start;
                var append_html = clone_html;

                append_html = append_html.replace(stem_leaf_regex, clone_stem + clone);

                $(this).after(append_html);
                $(this).next().find(".equation").each( function() {
                    $(this).html(eval($(this).data("eval")));
                });

            }
        }
    };
})(jQuery);

(function ($) {
    $.fn.numberSelect = function () {
        $(this).each(function() {
            if ($(this).hasProp("max")) {
                var number_max = parseInt($(this).prop("max"));
                var number_select_html = "<select class='numberSelect'></select>";
                $(this).after(number_select_html);
                $("select.numberSelect").copyAllAttributes($(this));
                $("select.numberSelect").append("<option value=''>" + $(this).prop("title") + "</option>");
                var text_options = $(this).data("text-options");
                if (text_options != null && text_options !== "") {
                    text_options = text_options.split(",");
                    for (i = 0; i < text_options.length; i++) {
                        $("select.numberSelect").append("<option value='" + text_options[i] + "'>" + properCase(text_options[i]) + "</option>");
                    }
                }
                var number_min = ($(this).hasProp("min")) ? parseInt($(this).prop("min")) : 0;
                var number_step = ($(this).hasProp("step")) ? parseInt($(this).prop("step")) : 1;
                for (i = number_min; i <= number_max; i += number_step) {
                    $("select.numberSelect").append("<option value='" + i + "'>" + i + "</option>");
                }

                $("select.numberSelect").removeClass("numberSelect");
                $(this).remove();
            }
        });
    };
})(jQuery);

(function ($) {
    $.fn.timeSelect = function () {
        $(this).each(function() {

            var number_select_html = "<select class='timeSelect'></select>";
            $(this).after(number_select_html);
            $("select.timeSelect").copyAllAttributes($(this));
            var options = $(this).data("options");
            if (options != null && options != "") {
                options = options.split(",");
                for (i = 0; i < options.length; i++) {
                    $("select.timeSelect").append("<option value='" + options[i] + "'>" + options[i] + "</option>");
                }
            } else {
                var time_step_regex = /^(?:([1|2|3|4|6])h)?\s?(?:([1-5]?\d)m)?$/,
                    time_step = $(this).data("time-step"),
                    time_regex = /^([1-9]|10|11|12):([0-5]?\d)\s(AM|PM)$/,
                    start_time = $(this).data("start-time");
                time_step = (time_step !== undefined && time_step_regex.test(time_step)) ? time_step : "1h";
                start_time = (start_time !== undefined && time_regex.test(start_time)) ? start_time : "12:00 AM";
                var time_steps = time_step.match(time_step_regex),
                    start_time_matches = start_time.match(time_regex),
                    hour = parseInt(start_time_matches[1]),
                    minutes = parseInt(start_time_matches[2]),
                    am_pm = start_time_matches[3].toUpperCase(),
                    time_value = (hour + ((am_pm == "AM") ? 0: 12)) + ":" + ((minutes < 10) ? "0" + minutes : minutes) + ":00";
                
                $("select.timeSelect").append("<option value=''>Select a time...</option><option value='" + time_value + "'>" + start_time + "</option>");

                if (time_steps[1] != null || time_steps[2] != null) {
                    var hour_step = (time_steps[1] == null) ? 0 : parseInt(time_steps[1]),
                        min_step = (60 * hour_step) + ((time_steps[2] == null) ? 0 : parseInt(time_steps[2])),
                        time_option;
                    
                    hour = (hour + Math.floor((minutes + min_step)/60)) % 12;
                    minutes = (minutes + min_step) % 60;
                    if (am_pm == "AM") {
                        while (hour < 12) {
                            time_option = ((minutes < 10) ? ((hour == 0) ? 12 : hour) + ":0" + minutes : ((hour == 0) ? 12 : hour) + ":" + minutes) + " AM";
                            time_value = hour + ":" + ((minutes < 10) ? "0" + minutes : minutes) + ":00";
                            $("select.timeSelect").append("<option value='" + time_value + "'>" + time_option + "</option>");
                            hour += Math.floor((minutes + min_step)/60);
                            minutes = (minutes + min_step) % 60;
                        }
                    }
                    hour = hour % 12;
                    while (hour < 12) {
                        time_option = ((minutes < 10) ? ((hour == 0) ? 12 : hour) + ":0" + minutes : ((hour == 0) ? 12 : hour) + ":" + minutes) + " PM";
                        time_value = (hour + 12) + ":" + ((minutes < 10) ? "0" + minutes : minutes) + ":00";
                        $("select.timeSelect").append("<option value='" + time_value + "'>" + time_option + "</option>");
                        hour += Math.floor((minutes + min_step)/60);
                        minutes = (minutes + min_step) % 60;
                    }
                }
            }

            $("select.timeSelect").removeClass("timeSelect");
            $(this).remove();
        });
    };
})(jQuery);

function build_calendar(month,year) {
   $("#calendar>tbody").empty();

    var date = new Date();
    var wk_day = date.getDay() + 1;
    var curr_day = date.getDate();

    if (month === undefined) {
        month = date.getMonth() + 1;
    }
    if (year === undefined) {
        year = date.getFullYear();
    }

    var month_beg_date = new Date(year, month - 1, 1);
    var month_end_date = new Date(year, month, 0);
    var last_day = month_end_date.getDate();
    var first_wk_day = month_beg_date.getDay() + 1;

    var day = 1;
    var weeks = Math.ceil((last_day - (7 - first_wk_day + 1)) / 7);

    $("#calendar-header").html(month_names[month - 1] + " | " + year);
    $("#calendar_month").val(month);
    $("#calendar_year").val(year);

    row_html = "<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>";

    $("#calendar>tbody").append(row_html);

    for (i = first_wk_day; i <= 7; i++) {
        $("#calendar>tbody>tr>td:nth-child(" + i + ")").append("<label class='calendar-day'>" + day + "</label>");
        $("#calendar>tbody>tr>td:nth-child(" + i + ")").prop("id","day" + day);
        day++;
    }

    for (i = 1; i <= weeks; i++) {
        $("#calendar>tbody").append(row_html);
        for (n = 1; n <= 7; n++) {
            if (day > last_day) {
                break;
            } else {
                $("#calendar>tbody>tr:nth-child(" + (i+1) + ")>td:nth-child(" + n + ")").append("<label class='calendar-day'>" + day + "</label>");
                $("#calendar>tbody>tr:nth-child(" + (i+1) + ")>td:nth-child(" + n + ")").prop("id","day" + day);
                day++;
            }
        }
    }
}

function validate_inputs($this) {
    var validated = true;

    $this.find("input:visible").each(function() {
        var criteria = $(this).data("criteria");
        var $form_group = $(this).closest(".form-group");

        if(criteria !== null && criteria != "optional" && !check_criteria($(this).val(),criteria)) {
            $form_group.addClass("has-error");
            validated = false;
        } else {
            $form_group.removeClass("has-error");
        }
    });
    $this.find("select:visible").each(function() {
        var criteria = $(this).data("criteria");
        var $form_group = $(this).closest(".form-group");

        if(criteria !== null && criteria != "optional" && !check_criteria($(this).val(),criteria)) {
            $form_group.addClass("has-error");
            validated = false;
        }  else {
            $form_group.removeClass("has-error");
        }
    });

    return validated;
}

var fixHelper = function(e, tr) {
  var $originals = tr.children();
  var $helper = tr.clone();
  $helper.children().each(function(index)
                          {
    $(this).width($originals.eq(index).width())
  });
  return $helper;
};

$(".sortable input").dblclick(function(){
    $(this).prop("readonly",false);
    $(this).prop("placeholder","Search for a user...");
});

$(".sortable input").blur(function(){
    $(this).prop("readonly",true);
    $(this).prop("placeholder","Double click to edit...");
});


(function() {
    var draggedItem;

    function dragstart(event) {
        event.target.className += ' dragged';
        event.dataTransfer.setData('text/html', event.target.id);
        draggedItem = event.target;
    }

    function dragenter(event) {
        var sourceNode = draggedItem;
        var targetNode = event.target;
        var sourceIndex = Array.prototype.indexOf.call(sourceNode.parentNode.childNodes, sourceNode);
        var targetIndex = Array.prototype.indexOf.call(targetNode.parentNode.childNodes, targetNode);
        if (targetIndex > sourceIndex) {
            targetNode.parentNode.insertBefore(targetNode, sourceNode);
        } else {
            targetNode.parentNode.insertBefore(sourceNode, targetNode);
        }
    }

    function dragend(event) {
        event.target.className = event.target.className.replace(' dragged', '');
    }

    function setDraggedItem(event) {
        draggedItem = event.target;
    }

    function sortDraggedItem(event) {
        var $sourceNode = $(draggedItem);
        var $targetNode = $(event.target);
        if ($targetNode.hasClass("sort-target")) {
          var child_index = $targetNode.index();
          var $sourceParent = $sourceNode.parent();
          $sourceNode.insertAfter($targetNode.siblings(":nth-child(" + child_index + ")"));
          $targetNode.insertAfter($sourceParent.children(":nth-child(" + child_index + ")"));
        }
    }

    function unsetDraggedItem(event) {
        $(draggedItem).removeClass("active");
        draggedItem = null;
    }

  $("table.column-sort").each(function() {
    var sort_column = parseInt($(this).data("sort-column"));
    $(this).find("tr>td:nth-child(" + sort_column + ")").each(function() {
        $(this).prop("draggable", true);
        $(this).attr("ondragstart","setDraggedItem(event)");
        $(this).attr("ondragenter","sortDraggedItem(event)");
        $(this).attr("ondragend","unsetDraggedItem(event)");
        $(this).addClass("sort-target");
    });
  });
})();

var month_names = new Array();
month_names[0] = "January";
month_names[1] = "February";
month_names[2] = "March";
month_names[3] = "April";
month_names[4] = "May";
month_names[5] = "June";
month_names[6] = "July";
month_names[7] = "August";
month_names[8] = "September";
month_names[9] = "October";
month_names[10] = "November";
month_names[11] = "December";

function form_init($parent) {
    'use strict';
    $parent = $parent || $("body")
    var selector = "[data-action-"
    var events = ["change", "click", "mouseover"]
    for (var i = 0; i < events.length; i++) {
        $parent.find(selector + events[i] + "]").each(function () { 
            action_trigger(events[i], $(this))
        })
    }
    $parent.find("textarea").each(function () {
        $(this).css("max-height", "35px")
    })
    $parent.find(".datepicker").each(function () {
        var min_date = $(this).data("mindate") || 0
        var max_date = $(this).data("maxdate") || "+1y"
        $(this).datepicker(
            {minDate: min_date, 
             maxDate: max_date}
        )
    })
    $parent.find('.combobox').combobox()
} 


$(document).ready(function () {
    $(".numberpicker").numberSelect();
    $(".timepicker").timeSelect();
    $("#id_player_search").popover();
    build_calendar();
    form_init();
    $("body").on("focus", "textarea", function() {
        $(this).css("max-height", "none");
    }).on("click", "#calendar_back", function() {
        if ($("#calendar_month").val() == 1) {
            build_calendar(12,parseInt($("#calendar_year").val()) - 1);
        } else {
            build_calendar(parseInt($("#calendar_month").val()) - 1,parseInt($("#calendar_year").val()));
        }
    }).on("click", "#calendar_next", function() {
        if ($("#calendar_month").val() == 12) {
            build_calendar(1,parseInt($("#calendar_year").val()) + 1);
        } else {
            build_calendar(parseInt($("#calendar_month").val()) + 1,parseInt($("#calendar_year").val()));
        }
    }).on("show hide slideDown slideUp fadeIn fadeOut", "[data-toggle-opp]", function(event) {
        var selectors = $(this).data("toggle-opp").split(/\s+/);
        switch (event.type) {
            case "hide":
            case "slideUp":
            case "fadeOut":
                for (i = 0; i < selectors.length; i++) {
                    $(selectors[i]).show();
                }
                break;
            case "show":
            case "slideDown":
            case "fadeIn":
                for (i = 0; i < selectors.length; i++) {
                    $(selectors[i]).hide();
                }
                break;
        }
    }).on("keyup", "textarea.char-count, input[type='text'].char-count", function(e) {
        var max_chars = $(this).prop("maxlength");
        if (max_chars < 524288 && max_chars > 0) {
            var chars_left = max_chars - this.value.length;

            if ($(this).parent().hasClass("wrap")) {
                $(this).unwrap();
            }

            $(this).next(".chars-left").remove();
            $(this).wrap("<div class='wrap'></div>");

            $(this).focus();

            var chars_html = "<span class='chars-left'>" + chars_left + " character" + ((chars_left == 1) ? "" : "s") + " left</span>"
            $(this).after(chars_html);

            if (this.value.length == max_chars) {
                e.preventDefault();
            } else if (this.value.length > max_chars) {
                this.value = this.value.substring(0, max_chars);
            }

            $(this).next(".chars-left").show().delay(500).queue(function(n) {
                $(this).fadeOut();
                n();
            });
        }
    });
    $("[data-criteria='optional']").each(function () {
        if ($(this).hasProp("placeholder")) {
            $(this).prop("placeholder",$(this).prop("placeholder") + " (Optional)");
        } else {
            $(this).prop("placeholder","(Optional)");
        }

        if ($(this).hasProp("title")) {
            $(this).prop("title",$(this).prop("title") + " (Optional)");
        }
    });
    
    $("table.column-sort").each(function() {
        var sort_column = parseInt($(this).data("sort-column"));
        $(this).find("tr>td:nth-child(" + sort_column + ")").each(function() {
          $(this).prop("draggable", true);
          $(this).attr("ondragstart","setDraggedItem(event)");
          $(this).attr("ondragenter","sortDraggedItem(event)");
          $(this).attr("ondragend","unsetDraggedItem(event)");
          $(this).addClass("sort-target");
        });
    });
    $(".table-columned").each(function() {
        var $table_cells = $(this).find(".table-cell");
        $table_cells.css("min-height","initial");
        var heights = $table_cells.map(function() {
          return $(this).outerHeight();
        }).get();

        var maxHeight = Math.max.apply(null, heights);
        $table_cells.css("min-height",maxHeight);
     });
    $("body").on("mouseenter", ".sort-target", function() {
      var $this = $(this),
        timeoutId = setTimeout(function() {
          var ph_height = $this.outerHeight();
          var ph_width = $this.outerWidth();

          $this.find(".sort-pop").each(function() {
            $(this).children().unwrap();
          });
          if (!$this.children().hasClass("sort-pop")) {
            $this.css("height", ph_height);
            $this.children().wrapAll("<div class='sort-pop'></div>")
            var $sort_pop = $this.children(".sort-pop");
            $sort_pop.css({
              "left": 0,
              "top": 0,
              "height": ph_height,
              "width": ph_width
            });
            $sort_pop.animate({
              height: "+=10",
              width: "+=20",
              left: "-=10",
              top: "-=5"
            }, "fast");
          }
          $this.removeData('timeoutId');
        }, 150);
      $this.data('timeoutId', timeoutId);
    }).on("mouseleave", ".sort-target", function() {
      var timeoutId = $(this).data('timeoutId');
      if (timeoutId == null || typeof timeoutId == undefined || timeoutId == "") {
        $(this).children(".sort-pop").children().unwrap();
      } else {
        clearTimeout(timeoutId);
      }
    }).on("mousedown", ".sort-pop>*", function() {
      $(this).unwrap();
    });
});

$(function () {
    $('.button-checkbox').each(function () {

        // Settings
        var $widget = $(this),
            $button = $widget.find('button'),
            $checkbox = $widget.find('input:checkbox'),
            color = $button.data('color'),
            settings = {
                on: {
                    icon: 'glyphicon glyphicon-check'
                },
                off: {
                    icon: 'glyphicon glyphicon-unchecked'
                }
            };

        // Event Handlers
        $button.on('click', function () {
            $checkbox.prop('checked', !$checkbox.is(':checked'));
            $checkbox.triggerHandler('change');
            updateDisplay();
        });
        $checkbox.on('change', function () {
            updateDisplay();
        });

        // Actions
        function updateDisplay() {
            var isChecked = $checkbox.is(':checked');

            // Set the button's state
            $button.data('state', (isChecked) ? "on" : "off");

            // Set the button's icon
            $button.find('.state-icon')
                .removeClass()
                .addClass('state-icon ' + settings[$button.data('state')].icon);

            // Update the button's color
            if (isChecked) {
                $button
                    .removeClass('btn-default')
                    .addClass('btn-' + color + ' active');
            }
            else {
                $button
                    .removeClass('btn-' + color + ' active')
                    .addClass('btn-default');
            }
        }

        // Initialization
        function init() {

            updateDisplay();

            // Inject the icon if applicable
            if ($button.find('.state-icon').length == 0) {
                $button.prepend('<i class="state-icon ' + settings[$button.data('state')].icon + '"></i> ');
            }
        }
        init();
    });
});