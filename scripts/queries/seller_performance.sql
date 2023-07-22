CREATE TABLE
    IF NOT EXISTS sellers_performance (
        with seller_category_rank as (
                SELECT
                    seller_id,
                    product_category_name,
                    ROW_NUMBER() OVER(
                        PARTITION BY seller_id
                        ORDER BY
                            COUNT(oi.order_id) DESC
                    ) as category_rank
                FROM order_items oi
                    LEFT JOIN products p ON p.product_id = oi.product_id
                GROUP BY 1, 2
            )
        SELECT
            s.seller_id,
            s.seller_state,
            s.seller_city,
            max(date(order_approved_at)) as last_approved_order_dt,
            count(distinct o.order_id) as qty_orders,
            count(
                distinct case
                    when order_status = 'delivered' then o.order_id
                    else null
                end
            ) as delivered_orders,
            count(
                distinct case
                    when order_status like '%cancel%' then o.order_id
                    else null
                end
            ) as canceled_orders,
            count(distinct product_id) as qty_distinct_items_sold,
            avg(price) as avg_item_sold_price,
            count(distinct review_id) as qty_reviews,
            avg(review_score) as avg_review_score,
            CASE
                WHEN category_rank = 1
                AND product_category_name is not null THEN product_category_name
            end as most_sold_category,
            avg(
                date(order_delivered_carrier_date) - date(order_approved_at)
            ) as avg_time_between_aproval_and_sent,
            sum(
                case
                    when o.order_status not like '%cancel%' then oi.price
                end
            ) as seller_sold_amount
        FROM sellers s
            LEFT JOIN order_items oi ON oi.seller_id = s.seller_id
            LEFT JOIN orders o ON o.order_id = oi.order_id
            LEFT JOIN order_reviews r ON r.order_id = o.order_id
            LEFT JOIN seller_category_rank as scr ON s.seller_id = scr.seller_id
        GROUP BY
            1,
            2,
            3,
            most_sold_category
    )