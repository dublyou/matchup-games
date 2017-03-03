(function() {
  "use strict";

  var selector = "[data-action-"
  var events = ["change", "click", "mouseover"]
  var event_type

  var action = function(e) {
    event_type = e.type || event_type
    var $this = $(this)
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

  for (var i = 0; i < events.length; i++) {
    event_type = events[i]
    $(selector + event_type + "]").each(action)
    $(document).on(event_type, selector + event_type + "]", action)
  }

})();
