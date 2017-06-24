const express 			 = require('express');
const app 				 = express();
const cmd 				 = require('node-cmd');
const ngrok 			 = require('ngrok');
const accountSid 	     = 'YOUR ACCOUNTSID HERE';
const authToken 		 = 'YOUR AUTHTOKEN HERE';
const twilio			 = require('twilio')(accountSid, authToken);
const MessagingResponse  = require('twilio').twiml.MessagingResponse;

app.get('/api/sms', function(req, res){
	
	cmd.get(req.query.Body, function(err, data){
		//https://www.twilio.com/docs/guides/how-to-receive-and-reply-in-node-js
		const twiml = new MessagingResponse();
		twiml.message(data);
		res.writeHead(200, {'Content-Type': 'text/xml'});
		res.end(twiml.toString());

	});
});

ngrok.connect(7672, function(err, url){
	if(err){
		console.log("ERROR: "+err);
	}
	console.log(url);
});

app.listen(7672, function(){
	console.log("server running");
});