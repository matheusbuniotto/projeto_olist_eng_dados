CREATE TABLE IF NOT EXISTS paid_orders AS (
    SELECT
        o.order_id,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        s.*,
        c.customer_unique_id,
        c.customer_zip_code_prefix,
        c.customer_city,
        c.customer_state,
        op.products_on_order,
        op.distinct_products_on_order,
        op.itens_price,
        op.order_freight_value,
        p.payment_installments,
        p.payment_sequential,
        p.payment_type,
        p.payment_value
    FROM (
        SELECT
            order_id,
            seller_id,
            SUM(price) AS itens_price,
            SUM(freight_value) AS order_freight_value,
            COUNT(product_id) AS products_on_order,
            COUNT(DISTINCT product_id) AS distinct_products_on_order
        FROM order_items
        GROUP BY 1, 2
    ) op
    LEFT JOIN orders o USING (order_id)
    LEFT JOIN sellers s USING (seller_id)
    LEFT JOIN customers c USING (customer_id)
    LEFT JOIN order_payments p USING (order_id)
    WHERE p.order_id IS NOT NULL
);

CREATE TABLE IF NOT EXISTS sellers_performance AS (
    WITH seller_category_rank AS (
        SELECT
            seller_id,
            product_category_name,
            ROW_NUMBER() OVER (
                PARTITION BY seller_id
                ORDER BY COUNT(oi.order_id) DESC
            ) AS category_rank
        FROM order_items oi
        LEFT JOIN products p ON p.product_id = oi.product_id
        GROUP BY 1, 2
    )
    SELECT
        s.seller_id,
        s.seller_state,
        s.seller_city,
        COUNT(DISTINCT o.order_id) AS qty_orders,
        COUNT(DISTINCT CASE WHEN order_status = 'delivered' THEN o.order_id ELSE NULL END) AS delivered_orders,
        COUNT(DISTINCT CASE WHEN order_status LIKE '%cancel%' THEN o.order_id ELSE NULL END) AS canceled_orders,
        COUNT(DISTINCT product_id) AS qty_distinct_items_sold,
        AVG(price) AS avg_item_sold_price,
        COUNT(DISTINCT review_id) AS qty_reviews,
        AVG(review_score) AS avg_review_score,
        CASE WHEN category_rank = 1 AND product_category_name IS NOT NULL THEN product_category_name END AS most_sold_category,
        SUM(CASE WHEN o.order_status NOT LIKE '%cancel%' THEN oi.price END) AS seller_sold_amount
    FROM sellers s
    LEFT JOIN order_items oi ON oi.seller_id = s.seller_id
    LEFT JOIN orders o ON o.order_id = oi.order_id
    LEFT JOIN order_reviews r ON r.order_id = o.order_id
    LEFT JOIN seller_category_rank AS scr ON s.seller_id = scr.seller_id
    GROUP BY 1, 2, 3, most_sold_category
);

CREATE TABLE IF NOT EXISTS customer_experience AS (
    SELECT
        c.customer_id,
        COUNT(DISTINCT review_id) AS qty_reviews,
        AVG(review_score) AS avg_review_score,
        MAX(order_approved_at) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS qty_orders,
        SUM(price) AS ltv
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY 1
    ORDER BY qty_orders DESC
);

CREATE TABLE IF NOT EXISTS order_items_detailed AS (
    SELECT
        oi.order_id,
        oi.order_item_id,
        o.order_status,
        o.order_approved_at,
        oi.shipping_limit_date,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        oi.product_id,
        p.product_category_name,
        p.product_name_lenght,
        p.product_description_lenght,
        p.product_photos_qty,
        p.product_height_cm,
        p.product_width_cm,
        p.product_length_cm,
        p.product_weight_g,
        s.*,
        c.*,
        oi.price,
        oi.freight_value
    FROM order_items oi
    LEFT JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN sellers s ON s.seller_id = oi.seller_id
    LEFT JOIN orders o ON o.order_id = oi.order_id
    LEFT JOIN customers c ON c.customer_id = o.customer_id
);
