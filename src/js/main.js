var results;
var price_slider;

function initMap() {
	var center = {
		lat: results[0].latitude,
		lng: results[0].longitude
	};
	var map = new google.maps.Map(document.getElementById('map'), {
		zoom: 15,
		center: center
	});
	var infowindow = new google.maps.InfoWindow();

	apartment = new google.maps.Marker({
			position: center,
			label: results[0].title,
			map: map
		})

	google.maps.event.addListener(apartment, 'click', (function(marker) {
			return function() {
				infowindow.setContent(results[0].title);
				infowindow.open(map, marker);
			}
		})(apartment));

	for(let poi of results[0]["top_5"]){
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

function query(){
	keyword = $("input#input").val();
	$.ajax({
		url: '/?limit=1&q='+keyword,
		data: {},
		type: 'get',
		success: function(data) {
			results = JSON.parse(data);
			$("#map").children().remove();
			$("#google_map").remove();
			$("body").append('<script id="google_map" async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCXHPOuU7LiGfqwEmmfKvutVX_rPaSFqNw&callback=initMap"></script>')
		}
	});
}

function create_price_slider(){
	var slider = document.getElementById('slider');

	price_slider = noUiSlider.create(slider, {
		start: [0, 1000],
		connect: true,
		range: {
			'min': 0,
			'max': 1000
		}
	});
}

$(document).ready(function(){
	// main

	// event listeners
	$("button#search").click(query);

	// ui stuff
	create_price_slider();

})