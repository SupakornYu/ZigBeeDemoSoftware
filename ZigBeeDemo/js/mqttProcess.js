/**
 * Created by supak on 15/11/2558.
 */
var MQTT_SERVER = '188.166.233.211';
var MQTT_PORT = 9001;
//[{protocolType:'ZigBee',networkId:0,deviceType:'coordinator'},
//{protocolType:'ZigBee',networkId:12566,from:0,deviceType:'router',deviceDuty:'dl',value:0},
//{protocolType:'ZigBee',networkId:1244,from:12566,deviceType:'enddevice',deviceDuty:'multisensor',value:25.3}]
var availableDevice = [];

var nodes = [
    {id: 1, label: 'Node 1'},
    {id: 2, label: 'Node 2'},
    {id: 3, label: 'Node 3'},
    {id: 4, label: 'Node 4'},
    {id: 5, label: 'Node 5'},
    {id: 0, label: 'coor'}
];

          // create an array with edges
var edges = [
    {from: 1, to: 3},
    {from: 1, to: 2},
    {from: 2, to: 4},
    {from: 2, to: 5}
];


removeAvailableDeviceWithNetworkId = function(networkId){
    availableDevice = availableDevice.filter(function (el) {
        return el.networkId !== networkId;
    });
};

addDeviceToTable = function(deviceAddr,defaultValue){

	availableDevice.push(deviceAddr);

	if($('#tableDevice .rowDevice#'+deviceAddr).length==0){

		$('#tableDevice tbody').append('<tr class="rowDevice" id="'+deviceAddr+'"><td>'+deviceAddr+'</td><td><img id="'+defaultValue+'" src="../../img/bulboff.png" class="lightClick"></td></tr>');

	}
	else{

		console.log(deviceAddr+" has already included.");
	}
};

removeDeviceFromTable = function(deviceAddr){

	$('#tableDevice .rowDevice#'+deviceAddr).remove();

};



$(document).ready(function(){


    var $wsStatus = $('.wsStatus');
    // Create a client instance
    client = new Paho.MQTT.Client(MQTT_SERVER, MQTT_PORT , "clientId");

    // set callback handlers
    client.onConnectionLost = onConnectionLost;
    client.onMessageArrived = onMessageArrived;

    // connect the client
    client.connect({onSuccess:onConnect});


    // called when the client connects
    function onConnect() {
      // Once a connection has been made, make a subscription and send a message.
        $wsStatus.attr("class", 'label label-success');
        $wsStatus.text('open');
        console.log("onConnect");
        client.subscribe("/ZigBeeAtmel/toMQTT");
        message = new Paho.MQTT.Message("Hello");
        message.destinationName = "/ZigBeeAtmel/toCi";
        message.retained = true;
        client.send(message);
    }

    // called when the client loses its connection
    function onConnectionLost(responseObject) {
        $wsStatus.attr("class", 'label label-warning');
        $wsStatus.text('error occurred');
        if (responseObject.errorCode !== 0) {
            console.log("onConnectionLost:"+responseObject.errorMessage);
        }
    }

    // called when a message arrives
    function onMessageArrived(message) {
        topologyDiv.clearAllData();
        console.log("onMessageArrived:"+message.payloadString);
        tttt = JSON.parse(message.payloadString);
        console.log(tttt);
        topologyDiv.addNode([{"NWK id": "0", "LQI": "0", "deviceType": "0"}]);
        topologyDiv.addNode(tttt['nodes']);
        topologyDiv.addEdge(tttt['links']);


    }

    function sendMessageToCi(message){
        client.send(message);
    };

    topologyDiv = new TopologyGen(nodes,edges);



});