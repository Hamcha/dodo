(function() {
  $(document).ready(function() {
    $("div#newdocbox").hide();
    $("a#canceldoc").click(function() {
      return $("div#newdocbox").fadeOut("slow");
    });
    $("a#newdoc").click(function() {
      $("span#newurl").html(location.origin + "/" + user + "/");
      return $("div#newdocbox").fadeIn("slow");
    });
    return $("a#dodoc").click(function() {
      return location.href = location.origin + "/" + user + "/" + $("#surl").val() + "/edit#" + $("#sname").val();
    });
  });

}).call(this);
