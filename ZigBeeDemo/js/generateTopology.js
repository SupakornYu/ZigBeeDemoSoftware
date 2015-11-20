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
            }
        }
    };
    var network = new vis.Network(container, data, options);

};

TopologyGen.prototype.addNode = function addNode(objNodeDetailArr) {

    for(var i=0;i<objNodeDetailArr.length;i++){
        try {
            this.nodes.update({
                id: objNodeDetailArr[i]['NWK id'],
                label: objNodeDetailArr[i]['NWK id']
                //label: objNodeDetailArr[i].label
                //group: objNodeDetailArr[i].group
            });
        }
        catch (err) {
            alert(err);
        }
    }
};

TopologyGen.prototype.addEdge = function addEdge(objEdgeDetailArr) {

    for(var i=0;i<objEdgeDetailArr.length;i++){
        try {
            this.edges.update({
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