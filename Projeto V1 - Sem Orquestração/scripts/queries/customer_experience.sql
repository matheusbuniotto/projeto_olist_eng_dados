-- Active: 1684981587971@@127.0.0.1@3306@lake

SELECT
c.customer_id,
count(distinct review_id) as qty_reviews,
avg(review_score) as avg_review_score,
max(order_approved_at) as last_order_date,
count(DISTINCT o.order_id) as qty_orders,
sum(price) as ltv
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
left join order_items oi ON o.order_id = oi.order_id
GROUP BY 1
ORDER BY qty_orders desc