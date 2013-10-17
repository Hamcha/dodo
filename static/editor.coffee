window.editor = true

window.onerror = (message, url, linenumber) ->
	$(".errorbox").html("<div class=\"error\">"+linenumber+" : "+message+"</div>");
	return true

converter = null
saving = false
unchanged = true

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
		if unchanged
			unchanged = false
			document.title = "* " + document.title + " *" 
		html = converter.makeHtml $("#editor").val()
		$("#result").html html
		return
	$('#docname').on 'change keyup', () ->
		unchanged = false
		document.title = "* Editing " + $('#docname').val() + " *" 
	$('textarea#editor').focus()
	if location.hash? and location.hash != ""
		$('input#docname').val(location.hash.replace("#",""))
		document.title = "Editing " + $('#docname').val() 
	$("#discard").click () ->
		return if saving
		redirect()
	$("#save").click () -> 
		$("#save").html "Saving..."
		save restoresv, throwerror
	$("#saveexit").click () -> 
		$("#saveexit").html "Saving..."
		save redirect, throwerror
		
	$("#hide").click () ->
		hidden = !hidden
		if hidden
			$('#result').fadeOut "fast", () ->
				an = if horizontal then {bottom:"50px"} else {right:"10px"}
				$('#edcontainer').animate an
				$("#hide").text("Show preview")
				return
			$('#edcontainer').css { "border-right": "1px solid #ccc" }
		else
			an = if horizontal then {bottom:"51%"} else {right:"55%"}
			$('#edcontainer').animate an, () ->
				$('#result').fadeIn "fast"
				$("#hide").text("Hide preview")
				return
			$('#edcontainer').css { "border-right": "0" }
		return
	$("#switch").click () ->
		return if hidden
		horizontal = !horizontal
		if horizontal
			$("#superwrapper").css { width: "960px", "margin" : "0 auto" }
			$('#result').css { right:"10px", top: "50%", left: "10px" }
			$('#edcontainer').css { right:"10px", bottom: "51%", "border-right" : "1px solid #ccc" }
			$('#previewbox').css { top:"50%" }
		else
			$("#superwrapper").css { width: "100%", "margin" : "0 auto" }
			$('#result').css { width:"auto", top: "60px", left: "45%" }
			$('#edcontainer').css { right:"55%", bottom: "50px", "border-right" : "0" }
			$('#previewbox').css { top:"60px" }

	$("#save_dd").click () ->
		data = $("#editor").val()
		name = $('input#docname').val()
		if !name? or name == ""
			name = "Untitled"
		exports = { "data" : data, "title" : name }
		blob = new Blob [JSON.stringify(exports)], {type: 'application/json'}
		downloadLink = document.createElement "a"
		downloadLink.href = window.webkitURL.createObjectURL blob
		downloadLink.download = name + ".dd";
		downloadLink.click()
		return
	
	$("#save_md").click () ->
		data = $("#editor").val()
		name = $('input#docname').val()
		if !name? or name == ""
			name = "Untitled"
		blob = new Blob [data], {type: 'application/json'}
		downloadLink = document.createElement "a"
		downloadLink.href = window.webkitURL.createObjectURL blob
		downloadLink.download = name + ".md";
		downloadLink.click()
		return

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
	unchanged = true
	saving = false
	location.href = document.URL.replace(/\/edit(.*)/,"")
	return
throwerror = (data) ->
	saving = false
	alert "Check your console (and logs, if you can)!"
	console.log data
	return

restoresv = () ->
	saving = false
	$("#save").html "Saved!"
	if not unchanged
		document.title = document.title.match(/(\*\s)(.*)(\s\*)/)[2]
		unchanged = true
	setTimeout (() -> 
		$("#save").html "Save"
		$("#save").removeClass "disabled"
		$("#saveexit").removeClass "disabled"
		$("#discard").removeClass "disabled"
		return
	), 2000
	return

save = (okcb, errorcb) ->
	return if saving
	saving = true
	data = $("#editor").val()
	name = $('input#docname').val()
	$("#save").addClass "disabled"
	$("#saveexit").addClass "disabled"
	$("#discard").addClass "disabled"
	($.post document.URL, { title: name, content: data }).done(okcb).error errorcb
	return

$(window).bind 'beforeunload', () ->
	return if unchanged
	return 'You have unsaved changes that will be lost if you leave now.'