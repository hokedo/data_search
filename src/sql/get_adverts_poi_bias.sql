/*
	get the adverts which are nearest the given poi location
*/

SELECT
	a.title,
	a.address,
	a.price,
	a.currency,
	a.url,
	g.latitude,
	g.longitude,
	g.id AS address_id,
	(100-(100*a.price/max_price)+100-(100*pd.distance/max_distance))/2 AS total_score
FROM data.advert a
JOIN data.geocoded g
	ON g.address = a.address
JOIN data.poi_distance pd
	ON g.id = pd.address_id
JOIN data.poi p
	ON p.id = pd.poi_id,
	(SELECT
		MAX(distance) AS max_distance
	FROM data.poi_distance
	) AS max_pd,
	(SELECT
		MAX(price) AS max_price
	FROM data.advert
	) AS max_advert
WHERE a.address ~* %s
	AND a.price >= %s
	AND a.price <= %s
	AND p.id = %s
ORDER BY total_score ASC
LIMIT %s