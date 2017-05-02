var results;
var pois;
var price_slider;
var map;
var infowindow;
var map_markers = [];

function initMap(result=null) {
	map = new google.maps.Map(document.getElementById('map'), {
		center: {
			lat: 46.7833856, // Cluj Coordinates
			lng: 23.6165124
		},
		zoom: 12
	});
	infowindow = new google.maps.InfoWindow();

	//update_map_markers(result);
}

function update_map_markers(result){
	// reset already existing markers
	// in case there are any
	for(let marker of map_markers){
		marker.setMap(null);
	}

	var center = {
		lat: result.latitude,
		lng: result.longitude
	};
	map.setCenter(center);
	map.setZoom(13);
	if(result.hasOwnProperty('price')){
		var label = result.price.toString() + " " + result.currency;
	}
	else{
		var label = result.title;
	}
	apartment = new google.maps.Marker({
			position: center,
			label: label,
			map: map
		})
	map_markers = [apartment];

	google.maps.event.addListener(apartment, 'click', (function(marker) {
			return function() {
				infowindow.setContent(result.title);
				infowindow.open(map, marker);
			}
		})(apartment));

	for(let poi of result["top_5"] || []){
		let marker = new google.maps.Marker({
			position: {
				lat: poi.latitude,
				lng: poi.longitude
			},
			label: poi.name,
			map: map
		})
		google.maps.event.addListener(marker, 'click', (function(marker) {
			return function() {
				infowindow.setContent(poi.name);
				infowindow.open(map, marker);
			}
		})(marker));
		map_markers.push(marker);
	}
}

function show_result_info(){
	var list_index = parseInt($("#results option:selected").attr("value"));
	var text_area = $("#result_info #textarea");
	var result = results[list_index];

	update_map_markers(result);

	var url = document.createElement("a");
	url.href = result.url;
	url.text = result.url;

	var poi_info = "<br><b>Top 5 Points of interest</b><br>";
	for(let poi of result.top_5){
		let name = "<b>Name:</b> " + poi.name;
		let address = "<b>Address:</b> " + poi.address;
		let type = "<b>Type:</b> " + poi.type;
		let rating = "<b>Rating:</b> " + poi.rating;
		poi_info += [name, address, type, rating, "<hr>"].join("<br>")
	}

	var text = [
				result.title,
				result.address,
				result.price + " " + result.currency,
				url.outerHTML,
				poi_info
			].join("<br>");
	text_area.html(text);
}

function populate_result_list(results_list){
	// remove any items that are in the
	// list before adding new items
	$("select#results").children().remove();
	var select_list = $("select#results");
	for(let i=0; i<results_list.length; i++){
		let result = results_list[i];
		let opt = document.createElement("OPTION");
		opt.value = i;
		opt.text = result.title;
		select_list.append(opt);
	}
}

function populate_poi_list(poi_list){
	var select_list = $("select#pois");
	for(let poi of poi_list){
		let opt = document.createElement("OPTION");
		opt.value = poi.id;
		opt.text = poi.title;
		select_list.append(opt);
	}
}

function query(){
	var keyword = $("input#input").val();
	var interest_poi_id = $("#pois option:selected").attr("value") || '-1';
	var price_range = price_slider.noUiSlider.get();
	var price_min = price_range[0];
	var price_max = price_range[1];
	$.ajax({
		url: '/?limit=5&q='+keyword+'&price_min='+price_min+'&price_max='+price_max+'&poi_id='+interest_poi_id,
		type: 'get',
		success: function(data) {
			results = JSON.parse(data);
			populate_result_list(results);
		}
	});
}

function get_pois(){
	$.ajax({
		url: '/?all_pois=true',
		type: 'get',
		success: function(data){
			pois = JSON.parse(data);
			populate_poi_list(pois);
		}
	}
	)
}

function set_poi_marker(){
	var selected_id = parseInt($("#pois option:selected").attr("value"));
	for(let poi of pois){
		if(poi.id == selected_id){
			update_map_markers(poi);
		}
	}
}

function create_price_slider(){
	var slider = document.getElementById('slider');
	var input0 = document.getElementById('input-with-keypress-0');
	var input1 = document.getElementById('input-with-keypress-1');
	var inputs = [input0, input1];
	price_slider = slider;

	noUiSlider.create(slider, {
		start: [100, 800],
		connect: true,
		//direction: 'rtl',
		tooltips: [true, wNumb({ decimals: 1 })],
		range: {
			'min': 0,
			'max': 1000
		}
	});

	slider.noUiSlider.on('update', function( values, handle ) {
		inputs[handle].value = values[handle];
	});

	function setSliderHandle(i, value) {
		var r = [null,null];
		r[i] = value;
		slider.noUiSlider.set(r);
	}
	// Listen to keydown events on the input field.
	inputs.forEach(function(input, handle) {

		input.addEventListener('change', function(){
			setSliderHandle(handle, this.value);
		});

		input.addEventListener('keydown', function( e ) {
			var values = slider.noUiSlider.get();
			var value = Number(values[handle]);
			// [[handle0_down, handle0_up], [handle1_down, handle1_up]]
			var steps = slider.noUiSlider.steps();
			// [down, up]
			var step = steps[handle];
			var position;
			// 13 is enter,
			// 38 is key up,
			// 40 is key down.
			switch ( e.which ) {
				case 13:
					setSliderHandle(handle, this.value);
					break;
				case 38:
					// Get step to go increase slider value (up)
					position = step[1];
					// false = no step is set
					if ( position === false ) {
						position = 1;
					}
					// null = edge of slider
					if ( position !== null ) {
						setSliderHandle(handle, value + position);
					}
					break;
				case 40:
					position = step[0];
					if ( position === false ) {
						position = 1;
					}
					if ( position !== null ) {
						setSliderHandle(handle, value - position);
					}
					break;
			}
		});
	});
}

$(document).ready(function(){
	// main

	// event listeners
	$("button#search").click(query);
	$("select#results").change(show_result_info);
	$("select#pois").change(set_poi_marker);

	// ui stuff
	create_price_slider();
	get_pois();

})