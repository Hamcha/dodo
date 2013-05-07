// Generated by CoffeeScript 1.4.0
(function() {
  var redirect, throwerror;

  window.onerror = function(message, url, linenumber) {
    $(".errorbox").html("<div class=\"error\">" + linenumber + " : " + message + "</div>");
    return true;
  };

  $(document).ready(function() {
    var converter, hidden, horizontal, html;
    hidden = false;
    horizontal = false;
    $('textarea#editor').on('change keyup', function() {
      var html;
      if (hidden) {
        return;
      }
      $(".errorbox").html("");
      html = converter.makeHtml($("#editor").val());
      $("#result").html(html);
    });
    $('textarea#editor').focus();
    if ((location.hash != null) && location.hash !== "") {
      $('input#docname').val(location.hash.replace("#", ""));
    }
    $("#discard").click(redirect);
    $("#save").click(function() {
      var data, name;
      data = $("#editor").val();
      name = $('input#docname').val();
      ($.post(document.URL, {
        title: name,
        content: data
      })).done(redirect).error(throwerror);
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
            width: "935px"
          };
          $('#edcontainer').animate(an);
          $("#hide").text("Show preview");
        });
      } else {
        an = horizontal ? {
          bottom: "51%"
        } : {
          width: "450px"
        };
        $('#edcontainer').animate(an, function() {
          $('#result').fadeIn("fast");
          $("#hide").text("Hide preview");
        });
      }
    });
    $("#switch").click(function() {
      if (hidden) {
        return;
      }
      horizontal = !horizontal;
      if (horizontal) {
        $('#result').animate({
          width: "918px",
          top: "50%"
        });
        return $('#edcontainer').animate({
          width: "938px",
          bottom: "51%"
        });
      } else {
        $('#result').animate({
          width: "460px",
          top: "60px"
        });
        return $('#edcontainer').animate({
          width: "450px",
          bottom: "50px"
        });
      }
    });
    converter = new Showdown.converter();
    html = converter.makeHtml($("#editor").val());
    return $("#result").html(html);
  });

  redirect = function(data) {
    location.href = document.URL.replace(/\/edit(.*)/, "");
  };

  throwerror = function(data) {
    alert("Check your console (and logs, if you can)!");
    console.log(data);
  };

}).call(this);
