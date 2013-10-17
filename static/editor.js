(function() {
  var converter, curw, dragEnter, dragLeave, dragging, fileDrop, redirect, restoresv, save, saving, throwerror, unchanged;

  window.editor = true;

  window.onerror = function(message, url, linenumber) {
    $(".errorbox").html("<div class=\"error\">" + linenumber + " : " + message + "</div>");
    return true;
  };

  converter = null;

  saving = false;

  unchanged = true;

  curw = 960;

  $(document).ready(function() {
    var hidden, horizontal, html;
    hidden = false;
    horizontal = false;
    $("#drophide").hide();
    $(document).filedrop({
      callback: fileDrop
    });
    $(document).on("dragenter", dragEnter);
    $(document).on("dragleave", dragLeave);
    $(document).on("drop", function() {
      return $("#drophide").hide();
    });
    $('textarea#editor').on('change keyup', function() {
      var html;
      if (hidden) {
        return;
      }
      $(".errorbox").html("");
      if (unchanged) {
        unchanged = false;
        document.title = "* " + document.title + " *";
      }
      html = converter.makeHtml($("#editor").val());
      $("#result").html(html);
    });
    $('#docname').on('change keyup', function() {
      unchanged = false;
      return document.title = "* Editing " + $('#docname').val() + " *";
    });
    $('textarea#editor').focus();
    if ((location.hash != null) && location.hash !== "") {
      $('input#docname').val(location.hash.replace("#", ""));
      document.title = "Editing " + $('#docname').val();
    }
    $("#discard").click(function() {
      if (saving) {
        return;
      }
      return redirect();
    });
    $("#save").click(function() {
      $("#save").html("Saving...");
      return save(restoresv, throwerror);
    });
    $("#saveexit").click(function() {
      $("#saveexit").html("Saving...");
      return save(redirect, throwerror);
    });
    $("#hide").click(function() {
      var an;
      hidden = !hidden;
      if (hidden) {
        $('#result').fadeOut("fast", function() {
          var an;
          an = horizontal ? {
            bottom: "50px"
          } : {
            right: "10px"
          };
          $('#edcontainer').animate(an);
          $("#hide").text("Show preview");
        });
        $('#edcontainer').css({
          "border-right": "1px solid #ccc"
        });
      } else {
        an = horizontal ? {
          bottom: "51%"
        } : {
          right: "55%"
        };
        $('#edcontainer').animate(an, function() {
          $('#result').fadeIn("fast");
          $("#hide").text("Hide preview");
        });
        $('#edcontainer').css({
          "border-right": "0"
        });
      }
    });
    $("#switch").click(function() {
      if (hidden) {
        return;
      }
      horizontal = !horizontal;
      if (horizontal) {
        $("#superwrapper").css({
          width: "960px",
          "margin": "0 auto"
        });
        $('#result').css({
          right: "10px",
          top: "50%",
          left: "10px"
        });
        $('#edcontainer').css({
          right: "10px",
          bottom: "51%",
          "border-right": "1px solid #ccc"
        });
        return $('#previewbox').css({
          top: "50%"
        });
      } else {
        $("#superwrapper").css({
          width: "100%",
          "margin": "0 auto"
        });
        $('#result').css({
          width: "auto",
          top: "60px",
          left: "45%"
        });
        $('#edcontainer').css({
          right: "55%",
          bottom: "50px",
          "border-right": "0"
        });
        return $('#previewbox').css({
          top: "60px"
        });
      }
    });
    $("#save_dd").click(function() {
      var blob, data, downloadLink, exports, name;
      data = $("#editor").val();
      name = $('input#docname').val();
      if ((name == null) || name === "") {
        name = "Untitled";
      }
      exports = {
        "data": data,
        "title": name
      };
      blob = new Blob([JSON.stringify(exports)], {
        type: 'application/json'
      });
      downloadLink = document.createElement("a");
      downloadLink.href = window.webkitURL.createObjectURL(blob);
      downloadLink.download = name + ".dd";
      downloadLink.click();
    });
    $("#save_md").click(function() {
      var blob, data, downloadLink, name;
      data = $("#editor").val();
      name = $('input#docname').val();
      if ((name == null) || name === "") {
        name = "Untitled";
      }
      blob = new Blob([data], {
        type: 'application/json'
      });
      downloadLink = document.createElement("a");
      downloadLink.href = window.webkitURL.createObjectURL(blob);
      downloadLink.download = name + ".md";
      downloadLink.click();
    });
    converter = new Showdown.converter();
    html = converter.makeHtml($("#editor").val());
    return $("#result").html(html);
  });

  dragging = 0;

  dragEnter = function() {
    dragging += 1;
    $("#drophide").fadeIn("fast");
    return false;
  };

  dragLeave = function() {
    dragging -= 1;
    if (dragging <= 0) {
      dragging = 0;
      $("#drophide").fadeOut("fast");
    }
    return false;
  };

  fileDrop = function(fileData) {
    var doc, error, html;
    $("#drophide").fadeOut("fast");
    try {
      doc = JSON.parse(fileData);
    } catch (_error) {
      error = _error;
      alert("Not a valid Dodo home document");
      return;
    }
    $("#editor").val(doc.data);
    $('input#docname').val(doc.title);
    html = converter.makeHtml($("#editor").val());
    return $("#result").html(html);
  };

  redirect = function(data) {
    unchanged = true;
    saving = false;
    location.href = document.URL.replace(/\/edit(.*)/, "");
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
      document.title = document.title.match(/(\*\s)(.*)(\s\*)/)[2];
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
    data = $("#editor").val();
    name = $('input#docname').val();
    $("#save").addClass("disabled");
    $("#saveexit").addClass("disabled");
    $("#discard").addClass("disabled");
    ($.post(document.URL, {
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

}).call(this);
