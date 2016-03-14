var vid = document.querySelector("#videoel");

window.URL = window.URL ||
    window.webkitURL ||
    window.msURL ||
    window.mozURL;
 
window.requestAnimFrame = (function() {
    return window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame ||
        window.oRequestAnimationFrame ||
        window.msRequestAnimationFrame ||
        function(/* function FrameRequestCallback */ callback, /* DOMElement Element */ element) {
            return window.setTimeout(callback, 1000/60);
        };
})();
navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;
 
if (navigator.getUserMedia) {       
	    navigator.getUserMedia({video: true}, handleVideo, videoError);
}
 
function handleVideo(stream) {
	    vid.src = window.URL.createObjectURL(stream);
}
 
function videoError(e) {

}


// http://stackoverflow.com/questions/6524288
$.fn.pressEnter = function(fn) {

	return this.each(function() {
		$(this).bind('enterPress', fn);
		$(this).keyup(function(e){
			if(e.keyCode == 13)
			{
				$(this).trigger("enterPress");
			}
		})
	});
};

function registerHbarsHelpers() {
    // http://stackoverflow.com/questions/8853396
    Handlebars.registerHelper('ifEq', function(v1, v2, options) {
    	if(v1 === v2) {
    		return options.fn(this);
    	}
    	return options.inverse(this);
    });
}
var listRectangle = [];
function sendFrameLoop() {
if (tok > 0) {
	var canvas = document.createElement('canvas');
	canvas.width = vid.width;
	canvas.height = vid.height;
	var cc = canvas.getContext('2d');
	cc.drawImage(vid, 0, 0, vid.width, vid.height);
	var apx = cc.getImageData(0, 0, vid.width, vid.height);

	var dataURL = canvas.toDataURL('image/jpeg', 0.6)
	var tempRect;

	var msg = {
		'type': 'FRAME',
		'dataURL': dataURL,
		'identity': defaultPerson
	};
		$.post("https://localhost:8443/image",msg,function(data){
		$("#detectedFaces").html("Identity : " + data[0]);
		tempRect = add_rect('red',{x1:data[1][0] , y1:data[2][1]  , x2: data[2][0], y2:data[1][1] })
		//console.log(data);
	});
	//tok--;
}

if (listRectangle.length>0)
{       
 $container.children('div:last-child').remove();
 listRectangle.pop();

}
listRectangle.push(tempRect);
setTimeout(function() {requestAnimFrame(sendFrameLoop)}, 1000);
//setTimeout(sendFrameLoop,1000);
}


var $container = $("#container");
//adapted fromm http://stackoverflow.com/questions/15651953/drawing-rectangles-on-an-image-in-javascript
var add_rect = function(color, rect) {
    $('<div class="child"/>')
    .appendTo($container)
    .css("left", 250 - rect.x1 + "px")
    .css("top", 70 +rect.y1 + "px")
    .css("width", (rect.x2-rect.x1)+"px")
    .css("height", (rect.y2-rect.y1)+"px")
    .css("border", "1px solid " + color);
};

// var remove_last_rect = function() {
//     if (new_rects.length > 0) {
//         $container.children('div:last-child').remove();
//         new_rects.pop();
//     }
// }
_.map(rects, _.partial(add_rect, 'red'));

function getPeopleInfoHtml() {
	var info = {'-1': 0};
	var len = people.length;
	for (var i = 0; i < len; i++) {
		info[i] = 0;
	}

	var len = images.length;
	for (var i = 0; i < len; i++) {
		id = images[i].identity;
		info[id] += 1;
	}

	var h = "<li><b>Unknown:</b> "+info['-1']+"</li>";
	var len = people.length;
	for (var i = 0; i < len; i++) {
		h += "<li><b>"+people[i]+":</b> "+info[i]+"</li>";
	}
	return h;
}

function redrawPeople() {
	var context = {people: people, images: images};
    //$("#peopleTable").html(peopleTableTmpl(context));

    var context = {people: people};
  //  $("#defaultPersonDropdown").html(defaultPersonTmpl(context));

   // $("#peopleInfo").html(getPeopleInfoHtml());
}

function getDataURLFromRGB(rgb) {
	var rgbLen = rgb.length;

	var canvas = $('<canvas/>').width(96).height(96)[0];
	var ctx = canvas.getContext("2d");
	var imageData = ctx.createImageData(96, 96);
	var data = imageData.data;
	var dLen = data.length;
	var i = 0, t = 0;

	for (; i < dLen; i +=4) {
		data[i] = rgb[t+2];
		data[i+1] = rgb[t+1];
		data[i+2] = rgb[t];
		data[i+3] = 255;
		t += 3;
	}
	ctx.putImageData(imageData, 0, 0);

	return canvas.toDataURL("image/png");
}

function updateRTT() {
	var diffs = [];
	for (var i = 5; i < defaultNumNulls; i++) {
		diffs.push(receivedTimes[i] - sentTimes[i]);
	}
	$("#rtt-"+socketName).html(
		jStat.mean(diffs).toFixed(2) + " ms (σ = " +
		jStat.stdev(diffs).toFixed(2) + ")"
		);
}

function sendState() {
	var msg = {
		'type': 'ALL_STATE',
		'images': images,
		'people': people,
		'training': training
	};
	socket.send(JSON.stringify(msg));
}



function umSuccess(stream) {
	if (vid.mozCaptureStream) {
		vid.mozSrcObject = stream;
	} else {
		vid.src = (window.URL && window.URL.createObjectURL(stream)) ||
		stream;
	}
	vid.play();
	vidReady = true;
	sendFrameLoop();
}

function addPersonCallback(el) {
	defaultPerson = people.length;
	var newPerson = $("#addPersonTxt").val();
	if (newPerson == "") return;
	people.push(newPerson);
	$("#addPersonTxt").val("");
		var msg = {
			'type': 'ADD_PERSON',
			'val': newPerson
		};
	$.post("https://localhost:8443/person",msg,function(data){
		console.log(data);
	});	
	redrawPeople();
}

function trainingChkCallback() {
	training = $("#trainingChk").prop('checked');
	var msg = {
		'type': 'TRAINING',
		'val': training
	};
	$.post("https://localhost:8443/train",msg,function(data){
		console.log(data);
	});
	sendFrameLoop();
}

function findImageByHash(hash) {
	var imgIdx = 0;
	var len = images.length;
	for (imgIdx = 0; imgIdx < len; imgIdx++) {
		if (images[imgIdx].hash == hash) {
			console.log("  + Image found.");
			return imgIdx;
		}
	}
	return -1;
}

function changeServerCallback() {
	$(this).addClass("active").siblings().removeClass("active");
	switch ($(this).html()) {
		case "Local":
		socket.close();
		redrawPeople();
		createSocket("ws:192.168.99.100:9000", "Local");
		break;
		case "CMU":
		socket.close();
		redrawPeople();
		createSocket("ws://facerec.cmusatyalab.org:9000", "CMU");
		break;
		case "AWS East":
		socket.close();
		redrawPeople();
		createSocket("ws://54.159.128.49:9000", "AWS-East");
		break;
		case "AWS West":
		socket.close();
		redrawPeople();
		createSocket("ws://54.188.234.61:9000", "AWS-West");
		break;
		default:
		alert("Unrecognized server: " + $(this.html()));
	}
}
   