window.popup = null

sendData = () ->
	console.log "SENDING DATA"
	obj =
		title: $("#title").html()
		url:location.href
		content: content
	window.popup.postMessage obj, location.origin

qepopup = () ->
	left= screen.width-750;
	window.popup = open "/qe.html", "Popup", "width=500,height=600,top=200,left="+left
	window.addEventListener "message", receiveMessage, false
	return

receiveMessage = (e) ->
	return if event.origin != location.origin
	switch e.data.substr(0,1)
		when "c" then window.update e.data.substr 2
		when "t" then $("#title").html e.data.substr 2
		when "r" then location.reload()
		when "o" then sendData()
	return

window.update = (data) ->
	html = window.converter.makeHtml data
	$("content").html html

content = null
$(document).ready () ->
	$("#gohome").attr "href", location.origin
	window.converter = new Showdown.converter()
	content = $("#content").val()
	window.update content
	
	if window.chrome?
		$("#quickedit").click qepopup
	else
		$("#quickedit").remove()
	$("#pin").click () ->
		$.post document.URL + "/pin", (data) ->
			if data == "pinned"
				restxt = "pinned!"
				restore = () -> ($("#pin").html "unpin").removeClass "pinned"
			else
				restxt = "unpinned!"
				restore = () -> ($("#pin").html "pin").removeClass "pinned"

			$("#pin").html(restxt).addClass "pinned"
			setTimeout restore, 1000