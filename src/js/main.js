var results;
var price_slider;

function initMap(result=null) {
	if(result == null){
		result = results[0]
	}
	var center = {
		lat: result.latitude,
		lng: result.longitude
	};
	var map = new google.maps.Map(document.getElementById('map'), {
		zoom: 15,
		center: center
	});
	var infowindow = new google.maps.InfoWindow();

	apartment = new google.maps.Marker({
			position: center,
			label: result.price,
			map: map
		})

	google.maps.event.addListener(apartment, 'click', (function(marker) {
			return function() {
				infowindow.setContent(result.title);
				infowindow.open(map, marker);
			}
		})(apartment));

	for(let poi of result["top_5"]){
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
	}
}

function show_result_info(selected){
	var list_index = parseInt($(selected.target).attr("value"));
	var text_area = $("#result_info #textarea");
	var result = results[list_index];

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
				result.price,
				url.outerHTML,
				poi_info
			].join("<br>");
	text_area.html(text);
}

function populate_result_list(results_list){
	var select_list = $("select#results");
	for(let i=0; i<results_list.length; i++){
		let result = results_list[i];
		let opt = document.createElement("OPTION");
		opt.value = i;
		opt.text = result.title;
		select_list.append(opt);
	}
}

function query(){
	keyword = $("input#input").val();
	$.ajax({
		url: '/?limit=5&q='+keyword,
		data: {},
		type: 'get',
		success: function(data) {
			results = JSON.parse(data);
			populate_result_list(results);
			$("#map").children().remove();
			$("#google_map").remove();
			$("body").append('<script id="google_map" async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCXHPOuU7LiGfqwEmmfKvutVX_rPaSFqNw&callback=initMap"></script>')
		}
	});
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
	$("select#results").click(show_result_info);

	// ui stuff
	create_price_slider();

})