var express = require('express')
var request = require('request')
var app = express()

app.use(function(req, res, next) {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

app.use(express.static('public'));
// app.use(bodyParser.json());
// app.use(bodyParser.urlencoded({extended: true}));

app.get('/index', function (req, res) {
  var url = "http://localhost:8080/df" + "/" + req.query['iDisplayStart'] + "/" + req.query['iDisplayLength'];

  request(url, function(err, resp, body) {
    var parsedBody = JSON.parse(body);
    parsedBody['aaData'] = JSON.parse(parsedBody['aaData']);
    res.json(parsedBody);
  });
})

app.get('/extended', function (req, res) {
  console.log(req.query);
  var url = "http://localhost:8080/df";
  console.log(url);

  request(url, function(err, resp, body) {
    var parsedBody = JSON.parse(JSON.parse(body));
    // parsedBody['aaData'] = JSON.parse(parsedBody['aaData']);
    // console.log('error:', err);         // Print the error if one occurred
    // console.log('statusCode:', resp && resp.statusCode); // Print the response status code if a response was received
    console.log('parsedBody:', parsedBody);   // Print the json
    res.json(parsedBody);   // This breaks with invalid JSON response
  });
})

app.listen(8081, function () {
  console.log('App listening on port 8081!')
})
