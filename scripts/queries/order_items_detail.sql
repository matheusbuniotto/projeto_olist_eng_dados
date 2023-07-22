
SELECT oi.order_id
     , oi.order_item_id
     , o.order_id
     , o.order_status
     , o.order_approved_at
     , oi.shipping_limit_date
     , o.order_delivered_carrier_date
     , o.order_delivered_customer_date
     , o.order_estimated_delivery_date
     , oi.product_id
     , p.product_category_name
     , p.product_name_lenght
     , p.product_description_lenght
     , p.product_photos_qty
     , p.product_height_cm
     , p.product_width_cm
     , p.product_length_cm
     , p.product_weight_g
     , s.*
     , c.*
     , oi.price
     , oi.freight_value
  FROM order_items oi LEFT JOIN
       products p ON p.product_id = oi.product_id LEFT JOIN
       sellers s ON s.seller_id = oi.seller_id LEFT JOIN
       orders o ON o.order_id = oi.order_id LEFT JOIN
       customers c ON c.customer_id = o.customer_id