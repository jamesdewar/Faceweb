
var fs = require('fs');
var http = require('http');
var https = require('https');
var privKey = fs.readFileSync('server.key', 'utf8');
var certificate  = fs.readFileSync('server.crt', 'utf8');
var path = require('path');
var cred = {key: privKey, cert: certificate};

var express = require('express')
var app = express();
app.use(express.static('public'));
app.set('view engine','ejs');

app.get('/',function(req,res){
res.render('default');
});

app.get('/:name?',function(req,res){
	var name = req.params.name;
	if (!name){
		res.send('No name');
	} else {
		res.send(name + ' was here');
	}
});

var httpsServer = https.createServer(cred,app);

var server = httpsServer.listen(8443, function() {
console.log('Someone connected');
});
