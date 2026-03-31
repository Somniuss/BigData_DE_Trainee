WITH actor_children_count AS (
    SELECT a.actor_id, a.first_name, a.last_name,
           COUNT(fa.film_id) AS film_count
    FROM actor a
    JOIN film_actor fa ON a.actor_id = fa.actor_id
    JOIN film_category fc ON fa.film_id = fc.film_id
    JOIN category c ON fc.category_id = c.category_id
    WHERE c.name = 'Children'
    GROUP BY a.actor_id, a.first_name, a.last_name
)
SELECT actor_id, first_name, last_name, film_count
FROM actor_children_count
WHERE film_count >= (
    SELECT MIN(film_count)
    FROM (
        SELECT film_count
        FROM actor_children_count
        ORDER BY film_count DESC
        LIMIT 3
    ) top3
)
ORDER BY film_count DESC;
