var bodyparser = require('body-parser');
var fs = require('fs');
var http = require('http');
var https = require('https');
var privKey = fs.readFileSync('server.key', 'utf8');
var certificate  = fs.readFileSync('server.crt', 'utf8');
var path = require('path');
var cred = {key: privKey, cert: certificate};

var express = require('express')
var app = express();
app.use(bodyparser.json());
app.use(bodyparser.urlencoded({extended:false}));
//app.use(json());
app.use(express.static('public'));
app.set('view engine','ejs');

//Default home route
app.get('/',function(req,res){
res.render('default');
});

//Test route
app.get('/:name?',function(req,res){
	var name = req.params.name;
	if (!name){
		res.send('No name');
	} else {
		res.send(name + ' was here');
	}
});

//Training route
app.post('/train', function(req,res){
	var name = req.body.type,
	val = req.body.val;
console.log(name + ' ' + val);
res.send("yes");
});

//Add person to train
app.post('/person', function(req,res){
	var type = req.body.type,
	name  = req.body.val;
console.log(type + ' ' + name);
res.send("yes");
});

//Image processing
app.post('/image', function(req,res){
	var type = req.body.type,
	dataURL  = req.body.dataURL,
	identity = req.body.identity;

console.log('Received image' + dataURL + ' ' + identity);
res.send("yes");
});
var httpsServer = https.createServer(cred,app);

var server = httpsServer.listen(8443, function() {
console.log('Someone connected');
});
