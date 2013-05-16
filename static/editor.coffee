window.onerror = (message, url, linenumber) ->
	$(".errorbox").html("<div class=\"error\">"+linenumber+" : "+message+"</div>");
	return true

converter = null

$(document).ready () ->
	hidden = false
	horizontal = false

	$("#drophide").hide()
	$(document).filedrop { callback : fileDrop }
	$(document).on "dragenter", dragEnter
	$(document).on "dragleave", dragLeave

	$('textarea#editor').on 'change keyup', () ->
		return if hidden
		$(".errorbox").html ""
		html = converter.makeHtml $("#editor").val()
		$("#result").html html
		return
	$('textarea#editor').focus()
	if location.hash? and location.hash != ""
		$('input#docname').val(location.hash.replace("#",""))
	$("#discard").click redirect
	$("#save").click () ->
		data = $("#editor").val()
		name = $('input#docname').val()
		($.post document.URL, { title: name, content: data }).done(redirect).error throwerror
		return
	$("#hide").click () ->
		hidden = !hidden
		if hidden
			$('#result').fadeOut "fast", () ->
				an = if horizontal then {bottom:"50px"} else {width:"935px"}
				$('#edcontainer').animate an
				$("#hide").text("Show preview")
				return
		else
			an = if horizontal then {bottom:"51%"} else {width:"450px"}
			$('#edcontainer').animate an, () ->
				$('#result').fadeIn "fast"
				$("#hide").text("Hide preview")
				return
		return
	$("#switch").click () ->
		return if hidden
		horizontal = !horizontal
		if horizontal
			$('#result').animate { width:"918px", top: "50%" }
			$('#edcontainer').animate { width:"938px", bottom: "51%" }
		else
			$('#result').animate { width:"460px", top: "60px" }
			$('#edcontainer').animate { width:"450px", bottom: "50px" }

	converter = new Showdown.converter()
	html = converter.makeHtml $("#editor").val()
	$("#result").html html

dragging = 0

dragEnter = () ->
	dragging += 1
	$("#drophide").fadeIn "fast"
	return false

dragLeave = () ->
	dragging -= 1
	if dragging <= 0
		dragging = 0
		$("#drophide").fadeOut "fast"
	return false
	
fileDrop = (fileData) ->
	$("#drophide").fadeOut "fast"
	try
		doc = JSON.parse fileData
	catch error
		alert "Not a valid Dodo home document"
		return
	$("#editor").val(doc.data)
	$('input#docname').val(doc.title)
	html = converter.makeHtml $("#editor").val()
	$("#result").html html

redirect = (data) ->
	location.href = document.URL.replace(/\/edit(.*)/,"")
	return
throwerror = (data) ->
	alert "Check your console (and logs, if you can)!"
	console.log data
	return