SELECT 
    ci.city,
    SUM(CASE WHEN cu.active = 1 THEN 1 ELSE 0 END) AS active_count,
    SUM(CASE WHEN cu.active = 0 THEN 1 ELSE 0 END) AS inactive_count
FROM customer cu
JOIN address a ON cu.address_id = a.address_id
JOIN city ci ON a.city_id = ci.city_id
GROUP BY ci.city
ORDER BY inactive_count DESC;
