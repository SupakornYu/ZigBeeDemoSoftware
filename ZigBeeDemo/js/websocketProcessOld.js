var host = 'ws://localhost:8888/ws';



addDeviceToTable = function(deviceAddr){
	
	if($('#tableDevice .rowDevice#'+deviceAddr).length==0){
	
		$('#tableDevice tbody').append('<tr class="rowDevice" id="'+deviceAddr+'"><td>'+deviceAddr+'</td><td><img src="../../img/bulboff.png" class="lightClick"></td></tr>');
	
	}
	else{
		
		console.log(deviceAddr+" has already included.");		
	}
}

removeDeviceFromTable = function(deviceAddr){
	
	$('#tableDevice .rowDevice#'+deviceAddr).remove();
	
}



$(document).ready(function(){
	
	
	
	
	addDeviceToTable(444);
	
	var ws = new WebSocket(host);
    var $wsStatus = $('.wsStatus');

    ws.onopen = function(){
      $wsStatus.attr("class", 'label label-success');
      $wsStatus.text('open');
	  var messageAuthen = {msType:"authen",deviceType:"userClient"};
	  ws.send(JSON.stringify(messageAuthen));
    };
    ws.onmessage = function(ev){
		
		
		
		
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
		console.log("click light id : "+trId);
		var messageOnOff = {msType:"cmd",messageTo:"combine",networkId:trId,cmd:"on/off",value:"-on"};
		ws.send(JSON.stringify(messageOnOff));
	});
	

	
	
});