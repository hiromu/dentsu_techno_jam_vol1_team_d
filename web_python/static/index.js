var hostname = 'ws://' + location.hostname + ':' + location.port + '/sp';
var ws;

function init() {
	if (window['ReconnectingWebSocket'] != undefined)
		ws = new ReconnectingWebSocket(hostname);
	else
		ws = new WebSocket(hostname);

	ws.onmessage = function(message) {
		var data = JSON.parse(message.data);
		$('#main').css('background-color', data.color);
	}
}
