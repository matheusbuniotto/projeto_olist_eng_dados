if 'extension' not in globals():
    from mage_ai.data_preparation.decorators import extension


@extension('great_expectations')
def validate(validator, *args, **kwargs):
    """
    validator: Great Expectations validator object
    """
    validator.expect_column_values_to_not_be_null(
        column = 'seller_id'
    )
    validator.expect_column_max_to_be_between(
        min=0,
        max=5,
        column='avg_review_score'
    )
 
