// Generated by CoffeeScript 1.4.0
(function() {
  var content, qepopup, receiveMessage, sendData;

  window.popup = null;

  sendData = function() {
    var obj;
    console.log("SENDING DATA");
    obj = {
      title: $("#title").html(),
      url: location.href,
      content: content
    };
    return window.popup.postMessage(obj, location.origin);
  };

  qepopup = function() {
    var left;
    left = screen.width - 750;
    window.popup = open("/qe.html", "Popup", "width=500,height=600,top=200,left=" + left);
    window.addEventListener("message", receiveMessage, false);
  };

  receiveMessage = function(e) {
    if (event.origin !== location.origin) {
      return;
    }
    switch (e.data.substr(0, 1)) {
      case "c":
        window.update(e.data.substr(2));
        break;
      case "t":
        $("#title").html(e.data.substr(2));
        break;
      case "r":
        location.reload();
        break;
      case "o":
        sendData();
    }
  };

  window.update = function(data) {
    var html;
    html = window.converter.makeHtml(data);
    return $("content").html(html);
  };

  content = null;

  $(document).ready(function() {
    $("#gohome").attr("href", location.origin);
    window.converter = new Showdown.converter();
    content = $("#content").val();
    window.update(content);
    if (window.chrome != null) {
      $("#quickedit").click(qepopup);
    } else {
      $("#quickedit").remove();
    }
    return $("#pin").click(function() {
      return $.post(document.URL + "/pin", function(data) {
        var restore, restxt;
        if (data === "pinned") {
          restxt = "pinned!";
          restore = function() {
            return ($("#pin").html("unpin")).removeClass("pinned");
          };
        } else {
          restxt = "unpinned!";
          restore = function() {
            return ($("#pin").html("pin")).removeClass("pinned");
          };
        }
        $("#pin").html(restxt).addClass("pinned");
        return setTimeout(restore, 1000);
      });
    });
  });

}).call(this);
