SELECT 
	p.name
	p.address,
	pd.distance,
	p.rating,
	p.type
FROM data.poi p
JOIN data.poi_distance pd
	ON p.id = pd.poi_id
	AND pd.address_id = %s;
ORDER BY pd.distance DESC
LIMIT 5;