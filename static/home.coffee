$(document).ready () ->
	$("div#newdocbox").hide()
	$("a#canceldoc").click () ->
		$("div#newdocbox").fadeOut "slow"
	$("a#newdoc").click () ->
		$("span#newurl").html location.origin + "/" + user + "/"
		$("div#newdocbox").fadeIn "slow"
	$("a#dodoc").click () ->
		location.href = location.origin + "/" + user + "/" + $("#surl").val() + "/edit#" + $("#sname").val()