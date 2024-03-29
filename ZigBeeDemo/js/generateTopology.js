/**
 * Created by supak on 17/11/2558.
 */

//this class is for generate topology. It is used in mqttProcess.js
function TopologyGen(nodes,edges){

    this.nodes = new vis.DataSet(nodes);
    this.edges = new vis.DataSet(edges);
    // create a network
    var container = document.getElementById('mynetwork');
    var data = {
        nodes: this.nodes,
        edges: this.edges
    };
    var options = {
        groups: {
            diamonds: {
                color: {background: 'red', border: 'white'},
                shape: 'diamond'
            },
            dotsWithLabel: {
                label: "I'm a dot!",
                shape: 'dot',
                color: 'cyan'
            },
            mints: {color: 'rgb(0,255,140)'},
            icons: {
                shape: 'icon',
                icon: {
                    face: 'FontAwesome',
                    code: '\uf0c0',
                    size: 50,
                    color: 'orange'
                }
            },
            source: {
                color: {border: 'white'}
            },
            ZigBeeCoordinator: {
                color: 'red'
            },
            ZigBeeRouter: {
                color: 'orange'
            },
            ZigBeeEndDevice: {
                color: 'green'
            },
            Aggregator: {
                shape: '',
                color: 'violet'
            },
            ESP8266: {
                color: 'Blue'
            },
            DimmableLightOn: {
                shape: 'image',
                image : '../../img/bulbon.png'
            },
            DimmableLightOff: {
                shape: 'image',
                image : '../../img/bulboff.png'
            },
            SmartthingMultiPurposeSensor: {
                shape: 'image',
                image : '../../img/smartthing_multipurpose_sensor.png'
            },
            AggregatorImage: {
                shape: 'image',
                image : '../../img/Aggregator.jpg'
            },
            ZigBeeCoordinatorImage: {
                shape: 'image',
                image : '../../img/AtmelSamR21.jpg'
            },
            SmartthingSmartPowerOutlet: {
                shape: 'image',
                image : '../../img/SmartThing_SmartPower_Outlet.gif'
            }
        }
    };

    network = new vis.Network(container, data, options);

}

TopologyGen.prototype.updateTopology = function updateTopology(objNodeDetailArr,objEdgeDetailArr){
    var tempNode = this.nodes.get();
    var tempEdge = this.edges.get();
    //1.add all new node and link but not duplicated.
    this.addNodeNotDuplicate(objNodeDetailArr);
    this.addEdgeNotDuplicate(objEdgeDetailArr);

    //2.search for node and link that does not exist in data anymore.
    for(var i=0;i<objNodeDetailArr.length;i++){
        if(this.nodes.get(objNodeDetailArr[i]['GBID'])!==null){
            tempNode = tempNode
               .filter(function (el) {
                        return el['id'] !== objNodeDetailArr[i]['GBID'];
                       });
        }
    }

    for(var i=0;i<objEdgeDetailArr.length;i++){
        if(this.edges.get({
                    filter: function (item) {
                        return item.from === objEdgeDetailArr[i].from && item.to === objEdgeDetailArr[i].to;
                    }
                }).length!==0){
            tempEdge = tempEdge
               .filter(function (el) {
                        return !(el['from'] === objEdgeDetailArr[i]['from'] && el['to'] === objEdgeDetailArr[i]['to']);
                       });
        }
    }

    //3.remove not existing node and link from topology.
    this.removeNode(tempNode);
    this.removeEdge(tempEdge);



};

TopologyGen.prototype.addNodeNotDuplicate = function addNodeNotDuplicate(objNodeDetailArr) {

    for(var i=0;i<objNodeDetailArr.length;i++){
        //check duplicate add
        var groupTemp;
        if(objNodeDetailArr[i]['deviceType']==="0"){
            groupTemp = 'ZigBeeCoordinator';
        }else if(objNodeDetailArr[i]['deviceType']==="1"){
            groupTemp = 'ZigBeeRouter';
        }else if(objNodeDetailArr[i]['deviceType']==="2"){
            groupTemp = 'ZigBeeEndDevice';
        }else if(objNodeDetailArr[i]['deviceType']==="Aggregator"){
            groupTemp = 'Aggregator';
        }else if(objNodeDetailArr[i]['deviceType']==="ESP8266"){
            groupTemp = 'ESP8266';
        }

        if(this.nodes.get(objNodeDetailArr[i]['GBID'])===null) {
            try {
                this.nodes.add({
                    id: objNodeDetailArr[i]['GBID'],
                    label: objNodeDetailArr[i]['GBID'],
                    //label: objNodeDetailArr[i].label
                    group: groupTemp
                });
            }
            catch (err) {
                alert(err);
            }
        }
    }
};

TopologyGen.prototype.addNode = function addNode(objNodeDetailArr) {

    for(var i=0;i<objNodeDetailArr.length;i++){
        //check duplicate add
        try {
            this.nodes.add({
                id: objNodeDetailArr[i]['GBID'],
                label: objNodeDetailArr[i]['GBID']
                //label: objNodeDetailArr[i].label
                //group: objNodeDetailArr[i].group
            });
        }
        catch (err) {
            alert(err);
        }

    }
};

TopologyGen.prototype.removeNode = function removeNode(objNodeDetailArr) {

    for(var i=0;i<objNodeDetailArr.length;i++){
        //check duplicate add
        try {
            this.nodes.remove({
                id: objNodeDetailArr[i]['id']
                //label: objNodeDetailArr[i]['NWK id']
                //label: objNodeDetailArr[i].label
                //group: objNodeDetailArr[i].group
            });
        }
        catch (err) {
            alert(err);
        }

    }
};

TopologyGen.prototype.removeEdge = function removeEdge(objEdgeDetailArr) {

    for(var i=0;i<objEdgeDetailArr.length;i++){
        //check duplicate add
        try {
            this.edges.remove({
                id: objEdgeDetailArr[i]['id']
                //label: objNodeDetailArr[i]['NWK id']
                //label: objNodeDetailArr[i].label
                //group: objNodeDetailArr[i].group
            });
        }
        catch (err) {
            alert(err);
        }

    }
};

TopologyGen.prototype.addEdgeNotDuplicate = function addEdgeNotDuplicate(objEdgeDetailArr) {

    for(var i=0;i<objEdgeDetailArr.length;i++){

        var countList = this.edges.get({
            filter: function (item) {
                return (item.from === objEdgeDetailArr[i].from && item.to === objEdgeDetailArr[i].to) || (item.to === objEdgeDetailArr[i].from && item.from === objEdgeDetailArr[i].to);
            }
        }).length;

        if(countList===0) {
            try {
                this.edges.add({
                    //id: objEdgeDetailArr[i].id,
                    from: objEdgeDetailArr[i].from,
                    to: objEdgeDetailArr[i].to
                });
            }
            catch (err) {
                alert(err);
            }
        }
    }

};

TopologyGen.prototype.addEdge = function addEdge(objEdgeDetailArr) {

    for(var i=0;i<objEdgeDetailArr.length;i++){

            try {
                this.edges.add({
                    //id: objEdgeDetailArr[i].id,
                    from: objEdgeDetailArr[i].from,
                    to: objEdgeDetailArr[i].to
                });
            }
            catch (err) {
                alert(err);
            }

    }

};

TopologyGen.prototype.getEdge = function getEdge() {
    return this.edges;
};

TopologyGen.prototype.getNode = function getNode() {
    return this.nodes;
};

TopologyGen.prototype.clearAllData = function clearAllData() {

    this.nodes.clear();
    this.edges.clear();

};

TopologyGen.prototype.getInstanceObj = function getInstanceObj() {

    return network

};

TopologyGen.prototype.setGroupToNode = function setGroupToNode(id,shape,group) {

    this.getNode().update({ id: id , shape:shape , group:group })

};