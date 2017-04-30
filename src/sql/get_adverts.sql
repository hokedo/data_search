/*
	get the advert data along with it's coordinates
*/

SELECT
	a.title,
	a.address,
	a.price,
	a.url,
	g.latitude,
	g.longitude,
	g.id AS address_id
FROM data.advert a 
JOIN data.geocoded g 
	ON g.address = a.address
WHERE a.address ~* %s
LIMIT %s