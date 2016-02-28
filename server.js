var https = require('https');
var fs = require('fs');
var app = require('express')();


var options = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.crt')
};

app.get('/', function(req,res){
	res.send('hello world');
});




https.createServer(options,app).listen(8000,  function () {
	console.log('started');
});
