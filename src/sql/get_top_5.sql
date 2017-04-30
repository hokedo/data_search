SELECT
	p.name,
	p.address,
	pd.distance,
	p.rating,
	p.type,
	p.latitude,
	p.longitude
FROM data.poi p
JOIN data.poi_distance pd
	ON p.id = pd.poi_id
WHERE pd.address_id = %s
ORDER BY pd.distance ASC
LIMIT 5