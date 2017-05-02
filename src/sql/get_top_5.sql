SELECT
	p.name,
	p.address,
	pd.distance,
	p.rating,
	p.type,
	p.latitude,
	p.longitude,
	(100-(100*pd.distance/max_distance))*0.7 + (100*p.rating/max_rating)*0.3 as total_score
FROM data.poi p
JOIN data.poi_distance pd
	ON p.id = pd.poi_id,
(SELECT
		max(distance) as max_distance,
		max(rating) as max_rating
	FROM
		data.poi_distance,
		data.poi
	) AS max_values
WHERE pd.address_id = %s
ORDER BY total_score DESC
LIMIT 5