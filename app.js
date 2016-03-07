var bodyparser = require('body-parser');
var zerorpc = require('zerorpc');
var fs = require('fs');
var http = require('http');
var https = require('https');
var privKey = fs.readFileSync('server.key', 'utf8');
var certificate  = fs.readFileSync('server.crt', 'utf8');
var path = require('path');
var cred = {key: privKey, cert: certificate};
var express = require('express')
var app = express();
var client = new zerorpc.Client();
client.connect('tcp://127.0.0.1:4242');


app.use(bodyparser.json());
app.use(bodyparser.urlencoded({extended:false}));
//app.use(json());
app.use(express.static('public'));
app.set('view engine','ejs');

//Default home route
app.get('/',function(req,res){
res.render('default');
});

var toggleCount = 0;
//Training route
app.post('/train', function(req,res){
	var name = req.body.type,
	val = req.body.val;
	console.log(name + ' ' + val);
	client.invoke("trainingToggle",val,function(error,res,more){
		toggleCount++;
	});
	if (val && toggleCount>1){

		client.invoke("trainSVM",function(error,res,more){
		console.log("SVm being trained");
		});
	}
});

//Add person to train
app.post('/person', function(req,res){
	var type = req.body.type,
	name  = req.body.val;
console.log(type + ' ' + name);
client.invoke("addPerson",name,function(error,res,more){
});
res.send("yes");
});

var frameDetails= 'unidentified';
//Image processing
app.post('/image', function(req,res){
	var type = req.body.type,
	dataURL  = req.body.dataURL,
	identity = req.body.identity;

console.log('Received image ');
//Run python that does the recognition
client.invoke("processFrame",dataURL,identity,function(error,res,more){
//	console.log(typeof res);
	console.log("Type of res[0]" + typeof res[0]);
	frameDetails =res;

});
console.log(frameDetails);
res.send(frameDetails);
});
  // received a message sent from the Python script (a simple "print" statement) 

var httpsServer = https.createServer(cred,app);

var server = httpsServer.listen(8443, function() {
console.log('Someone connected');
});
