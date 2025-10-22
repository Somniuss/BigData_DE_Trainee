WITH rental_hours AS (
    SELECT 
        CASE 
            WHEN ci.city LIKE 'A%' THEN 'Cities starting with A'
            WHEN ci.city LIKE '%-%' THEN 'Cities with -'
        END AS city_group,
        ca.name AS category_name,
        SUM(f.rental_duration) AS total_rental_hours
    FROM city ci
    JOIN address a ON ci.city_id = a.city_id
    JOIN customer cu ON a.address_id = cu.address_id
    JOIN rental r ON cu.customer_id = r.customer_id
    JOIN inventory i ON r.inventory_id = i.inventory_id
    JOIN film f ON i.film_id = f.film_id
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category ca ON fc.category_id = ca.category_id
    WHERE ci.city LIKE 'A%' OR ci.city LIKE '%-%'
    GROUP BY city_group, ca.name
),
max_hours AS (
    SELECT 
        city_group,
        MAX(total_rental_hours) AS max_rental_hours
    FROM rental_hours
    GROUP BY city_group
)
SELECT rh.city_group, rh.category_name, rh.total_rental_hours
FROM rental_hours rh
JOIN max_hours mh
    ON rh.city_group = mh.city_group 
   AND rh.total_rental_hours = mh.max_rental_hours;
