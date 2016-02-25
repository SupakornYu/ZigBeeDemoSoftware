/**
 * Created by supak on 15/11/2558.
 */
var MQTT_SERVER = '188.166.233.211';
var MQTT_PORT = 9001;
//[{protocolType:'ZigBee',networkId:0,deviceType:'coordinator'},
//{protocolType:'ZigBee',networkId:12566,from:0,deviceType:'router',deviceDuty:'dl',value:0},
//{protocolType:'ZigBee',networkId:1244,from:12566,deviceType:'enddevice',deviceDuty:'multisensor',value:25.3}]
var availableDevice = [];

var DESCTable;
var GlobalTable = [];
var reportTable;
var zigbeeTopologyTable;
var GBIDNodeClick = 0;

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



sendCMDToCoreSystem = function(message,destination,retained){

    var message = new Paho.MQTT.Message(message);
    message.destinationName = destination;
    message.retained = retained;
    client.send(message);

}


sendOnOffCMD = function(GBID,value){
    CMD_TEMP = JSON.stringify([{"GBID":GBID,"CMD":"0001","VALUE":value}])
    sendCMDToCoreSystem(CMD_TEMP,'multiProtocolGateway/Demo/fromMQTT/CMD',true)
}





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
        client.subscribe("multiProtocolGateway/Demo/toMQTT/Report");
        client.subscribe("multiProtocolGateway/Demo/toMQTT/GlobalDESC");
        client.subscribe("multiProtocolGateway/Demo/toMQTT/GlobalId");


        message = new Paho.MQTT.Message("Hello");
        message.destinationName = "/ZigBeeAtmel/toCi";
        message.retained = true;
        client.send(message);
        topologyDiv.clearAllData();
    };

    // called when the client loses its connection
    function onConnectionLost(responseObject) {
        $wsStatus.attr("class", 'label label-warning');
        $wsStatus.text('error occurred');
        if (responseObject.errorCode !== 0) {
            console.log("onConnectionLost:"+responseObject.errorMessage);
        }
    };

    // called when a message arrives
    function onMessageArrived(message) {
        //console.log("Topic : "+message.destinationName+" ,onMessageArrived : "+message.payloadString);
        //console.log(typeof(message.destinationName))
        if(message.destinationName === "/ZigBeeAtmel/toMQTT"){
            zigbeeTopologyTable = JSON.parse(message.payloadString);
            console.log(zigbeeTopologyTable);
            //topologyDiv.addNode([{"NWK id": "0", "LQI": "0", "deviceType": "0"}]);

            //add wifi node here
            ESP8266_node = []


            for(i=0;i<GlobalTable.length;i++){
                if(GlobalTable[i][1]===2){
                    ESP8266_node.push(GlobalTable[i][0]);
                    zigbeeTopologyTable['nodes'].push({'GBID': GlobalTable[i][0],'RSSI': "0",'NWK id': "",'deviceType': "ESP8266"});
                    zigbeeTopologyTable['links'].push({'from': 0,'to':GlobalTable[i][0]});
                }
            }




            zigbeeTopologyTable['nodes'].push({'GBID': 0,'LQI': "0",'NWK id': "Aggregator",'deviceType': "Aggregator"})
            ZigBeeCoorData = zigbeeTopologyTable['nodes'].filter(function(tt){return tt['deviceType']==='0'})
            var ZigBeeCoorGBID = ZigBeeCoorData.length !== 0 ? ZigBeeCoorData[0]['GBID'] : 0
            zigbeeTopologyTable['links'].push({'from': 0,'to':ZigBeeCoorGBID})

            topologyDiv.updateTopology(zigbeeTopologyTable['nodes'],zigbeeTopologyTable['links']);
        }else if(message.destinationName === "multiProtocolGateway/Demo/toMQTT/GlobalDESC"){
            DESCTable = JSON.parse(message.payloadString);
            console.log(DESCTable);
            //$('#StartQuery').prop('disabled', false);
            //$('#StopQuery').prop('disabled', true);
        }else if(message.destinationName === "multiProtocolGateway/Demo/toMQTT/Report"){
            reportTable = JSON.parse(message.payloadString);
            console.log(reportTable);
            $('#NodeReport').empty();
            reportTable.forEach(function(element, index, array) {
                console.log(element);
                if(Object.keys(element)[1]=="temperature"){
                    var content = "<div id=\""+ element['GBID'][0] +"temperature\"><button type=\"button\" class=\""+element['GBID'][0]+" reportBtn btn btn-info\">";
                    content +="Temperature : ";
                    content += element['temperature'];
                    content += "</button></div>";
                    $('#NodeReport').append(content);
                }else if(Object.keys(element)[1]=="ias"){
                    var content = "<div id=\""+ element['GBID'][0] +"ias\"><button type=\"button\" class=\""+element['GBID'][0]+" reportBtn btn btn-danger\">";
                    content +="IAS : ";
                    content += element['ias'];
                    content += "</button></div>";
                    $('#NodeReport').append(content);
                }else if(Object.keys(element)[1]=="Light"){
                    var content = "<div id=\""+ element['GBID'][0] +"Light\"><button type=\"button\" class=\""+element['GBID'][0]+" reportBtn btn btn-danger\">";
                    content +="LIGHT : ";
                    content += element['Light'];
                    content += "</button></div>";
                    $('#NodeReport').append(content);
                }else if(Object.keys(element)[0]=="On/Off"){
                    var value_temp = (element['On/Off'] == 1 ? "ON" : "OFF");
                    $('.'+element['GBID'][0]+'.onoff.CMDBtn.btn').html(value_temp);
                    console.log(element['GBID'][0]);
                    var Btn_color = (element['On/Off'] == 1 ? element['GBID'][0]+' onoff CMDBtn btn btn-warning' : element['GBID'][0]+' onoff CMDBtn btn btn-default');
                    $('.'+element['GBID'][0]+'.onoff.CMDBtn.btn').attr('class', Btn_color);
                }
            });

            $('.reportBtn').hide();
            $('.'+GBIDNodeClick+'.reportBtn').show();

        }else if(message.destinationName === "multiProtocolGateway/Demo/toMQTT/GlobalId"){
            GlobalTable = JSON.parse(message.payloadString);
            console.log(GlobalTable);
        }

    };



    function sendMessageToCi(message){
        client.send(message);
    };



    topologyDiv = new TopologyGen(nodes,edges);


    //handle event each node
    topologyDiv.getInstanceObj().on("click", function (params) {
        $('#NodeDetailTable').empty();
        $('.reportBtn').hide();
        $('.CMDBtn').hide();
        params.event = "[original event]";
        //console.log(JSON.stringify(params, null, 4));
        GBIDNodeClick = parseInt(params['nodes'][0]);
        var temp_GBID = parseInt(params['nodes'][0]);
        var temp_DESCnode = DESCTable.filter(function(tt){return tt['GBID'][0]===temp_GBID});
        //console.log(temp_DESCnode)
        temp_DESCnode.forEach(function(element, index, array) {
            //console.log(element);
            if(element['GBID'][1]===1){
                //zigbee
                var content = "<div class=\"bs-example\" data-example-id=\"simple-table\">\
								<table class=\"table\" style=\"table-layout: fixed; word-wrap: break-word;\"> <caption>Device Detail</caption>\
								<thead> <tr> <th>TOPIC</th> <th>DETAIL</th> </tr> </thead>\
								<tbody>";
                Object.keys(element).forEach(function(key) {
                    //console.log(key, element[key]);
                    if(key=='GBID'){
                        content += "<tr> <th scope=\"row\">GBID</th> <td>"+ element[key][0] +"</td>  </tr>";
                        content += "<tr> <th scope=\"row\">Device Type Number</th> <td>"+ element[key][1] +"</td>  </tr>";
                        content += "<tr> <th scope=\"row\">Network Address in ZigBee</th> <td>"+ element[key][2] +"</td>  </tr>";
                    }else{
                        content += "<tr> <th scope=\"row\">" + key +"</th> <td>"+ element[key] +"</td>  </tr>";
                    }
                });
                content += "</table></div>";

                $('#NodeDetailTable').append(content);

                $('.'+GBIDNodeClick+'.reportBtn').show();


                var uniqueClusterInArray = element['ClusterIn'].filter(function(item, pos) {
                        return element['ClusterIn'].indexOf(item) == pos;
                    });

                $('.CMDBtn').remove();
                for(i=0;i<uniqueClusterInArray.length;i++){
                    //console.log(i);
                    if(uniqueClusterInArray[i]==="6"){
                        console.log('on/off');



                        content = "<button type=\"button\" class=\""+element['GBID'][0]+" onoff CMDBtn btn btn-warning\">";
                        content += "ON";
                        content += "</button>";
                        $('#ControlNode').append(content);
                        //$('#'+element['GBID'][0]+'temperature '+'.reportBtn').show();
                    }
                }

            }else if(element['GBID'][1]===2){
                //ESP8266
                var content = "<div class=\"bs-example\" data-example-id=\"simple-table\">\
								<table class=\"table\" style=\"table-layout: fixed; word-wrap: break-word;\"> <caption>Device Detail</caption>\
								<thead> <tr> <th>TOPIC</th> <th>DETAIL</th> </tr> </thead>\
								<tbody>";
                Object.keys(element).forEach(function(key) {
                    //console.log(key, element[key]);
                    if(key=='GBID'){
                        content += "<tr> <th scope=\"row\">GBID</th> <td>"+ element[key][0] +"</td>  </tr>";
                        content += "<tr> <th scope=\"row\">Device Type Number</th> <td>"+ element[key][1] +"</td>  </tr>";
                        content += "<tr> <th scope=\"row\">MAC ADDRESS</th> <td>"+ element[key][2] +"</td>  </tr>";
                    }else{
                        content += "<tr> <th scope=\"row\">" + key +"</th> <td>"+ element[key] +"</td>  </tr>";
                    }
                });
                content += "</table></div>";

                $('#NodeDetailTable').append(content);

                $('.'+GBIDNodeClick+'.reportBtn').show();


                var uniqueClusterInArray = element['ClusterIn'].filter(function(item, pos) {
                        return element['ClusterIn'].indexOf(item) == pos;
                    });

                $('.CMDBtn').remove();
                for(i=0;i<uniqueClusterInArray.length;i++){
                    //console.log(i);
                    if(uniqueClusterInArray[i]==="6"){
                        console.log('on/off');



                        content = "<button type=\"button\" class=\""+element['GBID'][0]+" onoff CMDBtn btn btn-warning\">";
                        content += "ON";
                        content += "</button>";
                        $('#ControlNode').append(content);
                        //$('#'+element['GBID'][0]+'temperature '+'.reportBtn').show();
                    }
                }

            }

        });
        //if(temp_DESCnode)
    });



    //add aggregator node
    topologyDiv.getNode().add(
        {id: 'aggregator', label: 'Aggretor'}
    );
    topologyDiv.getEdge().add({
                    from: 'aggregator',
                    to: '0'
                });

    $('#StartQuery').prop('disabled', false);
    $('#StopQuery').prop('disabled', true);

    $( "#StartQuery" ).click(function() {
        $('#StartQuery').prop('disabled', true);
        $('#StopQuery').prop('disabled', false);
        topologyDiv.clearAllData()
        sendCMDToCoreSystem('[{"GBID":"0","CMD":"0002","VALUE":"1"}]','multiProtocolGateway/Demo/fromMQTT/CMD',true)
    });

    $( "#StopQuery" ).click(function() {
        $('#StopQuery').prop('disabled', true);
        $('#StartQuery').prop('disabled', false);
        sendCMDToCoreSystem('[{"GBID":"0","CMD":"0002","VALUE":"0"}]','multiProtocolGateway/Demo/fromMQTT/CMD',true)

    });


    $(document).on('click', '.onoff.CMDBtn' , function() {
        console.log(this);
        temp_GBID = $(this).attr("class").split(" ")[0];
        temp_value = ($(this).html()==='ON' ? '0':'1');
        sendOnOffCMD(temp_GBID,temp_value);
    });




});