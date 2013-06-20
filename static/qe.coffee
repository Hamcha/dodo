window.editor = true

window.onerror = (message, url, linenumber) ->
	$(".errorbox").html("<div class=\"error\" style=\"margin: -5px;\">"+linenumber+" : "+message+"</div>");
	return true

converter = null
saving = false
unchanged = true
daddy = dsource = null
docurl = null

$(document).ready () ->
	$('textarea#editor').on 'change keyup', () ->
		$(".errorbox").html ""
		if unchanged
			unchanged = false
			document.title = "* Quick Edit *" 
		if daddy isnt null
			daddy.postMessage "c:" + $("#editor").val(), dsource
		return
	$('#title').on 'change keyup', () ->
		unchanged = false
		document.title = "* Quick Edit *" 
		daddy.postMessage "t:" + $("#title").val(), dsource
	$("#discard").click () ->
		return if saving
		redirect()
	$("#save").click () ->
		return if daddy is null
		$("#save").html "Saving..."
		save restoresv, throwerror
	$("#saveexit").click () -> 
		return if daddy is null
		$("#saveexit").html "Saving..."
		save redirect, throwerror
	window.opener.postMessage "o", location.origin


receiveMessage = (e) ->
	return if event.origin != location.origin
	daddy = event.source
	dsource = event.origin
	docurl = e.data.url
	if docurl[docurl.length - 1] == "/"
		docurl = docurl.substring 0, docurl.length - 1
	$("#title").val e.data.title
	$("#editor").val e.data.content

window.addEventListener "message", receiveMessage, false

redirect = (data) ->
	self.close()

throwerror = (data) ->
	saving = false
	alert "Check your console (and logs, if you can)!"
	console.log data
	return

restoresv = () ->
	saving = false
	$("#save").html "Saved!"
	if not unchanged
		document.title = "Quick Edit"
		unchanged = true
	setTimeout (() -> 
		$("#save").html "Save"
		$("#save").css { "color" : "inherit" }
		$("#saveexit").css { "color" : "inherit" }
		$("#discard").css { "color" : "inherit" }
		return
	), 2000
	return

save = (okcb, errorcb) ->
	return if saving
	saving = true
	unchanged = true
	data = $("#editor").val()
	name = $('input#title').val()
	$("#save").css { "color" : "#777" }
	$("#saveexit").css { "color" : "#777" }
	$("#discard").css { "color" : "#777" }
	($.post docurl+"/edit", { title: name, content: data }).done(okcb).error errorcb
	return

$(window).bind 'beforeunload', () ->
	return if unchanged
	return 'You have unsaved changes that will be lost if you leave now.'
$(window).bind 'unload', () ->
	daddy.postMessage "r", dsource