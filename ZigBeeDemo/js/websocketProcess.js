var host = 'ws://localhost:8888/ws';
var availableDevice = [];


addDeviceToTable = function(deviceAddr,defaultValue){
	
	availableDevice.push(deviceAddr);
	
	if($('#tableDevice .rowDevice#'+deviceAddr).length==0){
	
		$('#tableDevice tbody').append('<tr class="rowDevice" id="'+deviceAddr+'"><td>'+deviceAddr+'</td><td><img id="'+defaultValue+'" src="../../img/bulboff.png" class="lightClick"></td></tr>');
	
	}
	else{
		
		console.log(deviceAddr+" has already included.");		
	}
}

removeDeviceFromTable = function(deviceAddr){
	
	$('#tableDevice .rowDevice#'+deviceAddr).remove();
	
}



$(document).ready(function(){
	
	
	
	
	//addDeviceToTable(444,"lightOff");
	
	var ws = new WebSocket(host);
    var $wsStatus = $('.wsStatus');

    ws.onopen = function(){
      $wsStatus.attr("class", 'label label-success');
      $wsStatus.text('open');
	  //var messageAuthen = {msType:"authen",deviceType:"userClient"};
	  //ws.send(JSON.stringify(messageAuthen));
    };
    ws.onmessage = function(ev){
		
		
		messageObj = JSON.parse(ev.data);
		console.log(messageObj);
		
		if(messageObj.cmd==="newDevice"){
			addDeviceToTable(messageObj.addr,"lightOff");
		}else if(messageObj.cmd==="reportLevelControl"){
			if(availableDevice.indexOf(messageObj.addr)===-1){
				addDeviceToTable(messageObj.addr,"lightOff");
			}
		}else if(messageObj.cmd==="reportOnOff"){
			if(availableDevice.indexOf(messageObj.addr)===-1){
				addDeviceToTable(messageObj.addr,"lightOff");
			}
			if(messageObj.value==0){
				$('.rowDevice#'+messageObj.addr+' td img').attr("id","lightOff")
				$('.rowDevice#'+messageObj.addr+' td img').attr("src","../../img/bulboff.png")
			}else if(messageObj.value==1){
				$('.rowDevice#'+messageObj.addr+' td img').attr("id","lightOn")
				$('.rowDevice#'+messageObj.addr+' td img').attr("src","../../img/bulbon.png")
			}
		}
		
      /* $wsStatus.attr("class", 'label label-info');
      $wsStatus.hide();
      $wsStatus.fadeIn("slow");
      $wsStatus.text('recieved message');

      var json = JSON.parse(ev.data);
      $('#' + json.id).hide();
      $('#' + json.id).fadeIn("slow");
      $('#' + json.id).text(json.value);

      var $rowid = $('#row' + json.id);
      if(json.value > 500){
        $rowid.attr("class", "error");
      }
      else if(json.value > 200){
        $rowid.attr("class", "warning");
      }
      else{
        $rowid.attr("class", "");
      } */
    };
    ws.onclose = function(ev){
      $wsStatus.attr("class", 'label label-important');
      $wsStatus.text('closed');
    };
    ws.onerror = function(ev){
      $wsStatus.attr("class", 'label label-warning');
      $wsStatus.text('error occurred');
    };
	
	$('#tableDevice').on('click', '.lightClick', function(){
		var trId = $(this).closest('tr').prop('id');
		var messageOnOff = "";
		console.log("click light id : "+trId);
		//console.log("click light id : "+trId);
		//console.log("src : "+($(this).prop('id')==="lightOff"));
		if($(this).prop('id')==="lightOff"){
			messageOnOff = {cmd:"on/off",addr:trId,value:"on"};
			//you should implements response message from combined board not code like this but not enough time
			$(this).attr("id","lightOn");
			$(this).attr("src","../../img/bulbon.png");
		}else{
			messageOnOff = {cmd:"on/off",addr:trId,value:"off"};
			//you should implements response message from combined board not code like this but not enough time
			$(this).attr("id","lightOff");
			$(this).attr("src","../../img/bulboff.png");
		}
		ws.send(JSON.stringify(messageOnOff));
	});
	

	
	
});