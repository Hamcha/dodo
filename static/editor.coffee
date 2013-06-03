window.editor = true

window.onerror = (message, url, linenumber) ->
	$(".errorbox").html("<div class=\"error\">"+linenumber+" : "+message+"</div>");
	return true

converter = null
saving = false

curw = 960

$(document).ready () ->
	hidden = false
	horizontal = false

	$("#drophide").hide()
	$(document).filedrop { callback : fileDrop }
	$(document).on "dragenter", dragEnter
	$(document).on "dragleave", dragLeave
	$(document).on "drop", () ->
		$("#drophide").hide()

	$('textarea#editor').on 'change keyup', () ->
		return if hidden
		$(".errorbox").html ""
		html = converter.makeHtml $("#editor").val()
		$("#result").html html
		return
	$('textarea#editor').focus()
	if location.hash? and location.hash != ""
		$('input#docname').val(location.hash.replace("#",""))
	$("#discard").click () ->
		return if saving
		redirect()
	$("#save").click () ->
		return if saving
		saving = true
		data = $("#editor").val()
		name = $('input#docname').val()
		$("#save").css { "color" : "#777" }
		$("#discard").css { "color" : "#777" }
		$("#save").html "Saving..."
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
			$("#superwrapper").css { width: "960px", "margin" : "0 auto" }
			$('#result').css { width:"918px", top: "50%", left: "auto" }
			$('#edcontainer').css { width:"918px", bottom: "51%", "border-right" : "1px solid #ccc" }
			$('#previewbox').css { top:"50%" }
		else
			$("#superwrapper").css { width: "auto", "margin" : "0 20px" }
			$('#result').css { width:"auto", top: "60px", left: "45%" }
			$('#edcontainer').css { width:"auto", bottom: "50px", "border-right" : "0" }
			$('#previewbox').css { top:"60px" }

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