(function() {
  var converter, daddy, docurl, dsource, receiveMessage, redirect, restoresv, save, saving, throwerror, unchanged;

  window.editor = true;

  window.onerror = function(message, url, linenumber) {
    $(".errorbox").html("<div class=\"error\" style=\"margin: -5px;\">" + linenumber + " : " + message + "</div>");
    return true;
  };

  converter = null;

  saving = false;

  unchanged = true;

  daddy = dsource = null;

  docurl = null;

  $(document).ready(function() {
    $('textarea#editor').on('change keyup', function() {
      $(".errorbox").html("");
      if (unchanged) {
        unchanged = false;
        document.title = "* Quick Edit *";
      }
      if (daddy !== null) {
        daddy.postMessage("c:" + $("#editor").val(), dsource);
      }
    });
    $('#title').on('change keyup', function() {
      unchanged = false;
      document.title = "* Quick Edit *";
      return daddy.postMessage("t:" + $("#title").val(), dsource);
    });
    $("#discard").click(function() {
      if (saving) {
        return;
      }
      return redirect();
    });
    $("#save").click(function() {
      if (daddy === null) {
        return;
      }
      $("#save").html("Saving...");
      return save(restoresv, throwerror);
    });
    $("#saveexit").click(function() {
      if (daddy === null) {
        return;
      }
      $("#saveexit").html("Saving...");
      return save(redirect, throwerror);
    });
    return window.opener.postMessage("o", location.origin);
  });

  receiveMessage = function(e) {
    var event;
    if (!event) {
      event = e;
    }
    if (event.origin !== location.origin) {
      return;
    }
    daddy = event.source;
    dsource = event.origin;
    docurl = e.data.url;
    if (docurl[docurl.length - 1] === "/") {
      docurl += docurl.match("http://(.*)/([^\]*)/")[2];
    }
    $("#title").val(e.data.title);
    return $("#editor").val(e.data.content);
  };

  window.addEventListener("message", receiveMessage, false);

  redirect = function(data) {
    return self.close();
  };

  throwerror = function(data) {
    saving = false;
    alert("Check your console (and logs, if you can)!");
    console.log(data);
  };

  restoresv = function() {
    saving = false;
    $("#save").html("Saved!");
    if (!unchanged) {
      document.title = "Quick Edit";
      unchanged = true;
    }
    setTimeout((function() {
      $("#save").html("Save");
      $("#save").removeClass("disabled");
      $("#saveexit").removeClass("disabled");
      $("#discard").removeClass("disabled");
    }), 2000);
  };

  save = function(okcb, errorcb) {
    var data, name;
    if (saving) {
      return;
    }
    saving = true;
    unchanged = true;
    data = $("#editor").val();
    name = $('input#title').val();
    $("#save").addClass("disabled");
    $("#saveexit").addClass("disabled");
    $("#discard").addClass("disabled");
    ($.post(docurl + "/edit", {
      title: name,
      content: data
    })).done(okcb).error(errorcb);
  };

  $(window).bind('beforeunload', function() {
    if (unchanged) {
      return;
    }
    return 'You have unsaved changes that will be lost if you leave now.';
  });

  $(window).bind('unload', function() {
    return daddy.postMessage("r", dsource);
  });

}).call(this);
