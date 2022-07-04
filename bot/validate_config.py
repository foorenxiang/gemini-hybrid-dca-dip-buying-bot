from bot import config


def validate_config():
    assert config.environment in {"live", "sandbox"}

    assert isinstance(
        config.database, str
    ), f"database must be a string, got {type(config.database)}"

    assert isinstance(
        config.database_connection_string, str
    ), f"database_connection_string must be a string, got {type(config.database_connection_string)}"

    assert (
        config.automatic_stop_limit_price_steps_for_buying_dip
        > config.dca_amount_per_transaction
    )
    for key, value in config.stop_limit_step.items():
        assert value > 0, f"stop_limit_step for {key} must be positive"

    min_dca_amount = 2.5
    assert (
        config.dca_amount_per_transaction > min_dca_amount
    ), f"dca_amount must be greater than {min_dca_amount}"

    for key, value in config.reserved_amount_for_market_orders.items():
        assert (
            value > 0
        ), f"reserved_amount_for_market_orders for {key} must be positive"

    for key, value in config.max_limit_order_price.items():
        assert value > 0, f"max_limit_order_price for {key} must be positive"

    for key, value in config.min_limit_order_price.items():
        assert value > 0, f"min_limit_order_price for {key} must be positive"

    for key, value in config.tkn_pair_min_order_amount.items():
        assert value > 0, f"tkn_pair_min_order_amount for {key} must be positive"

    assert (
        config.hours_to_pass_per_market_order > 0
    ), "hours_to_pass_per_market_order must be positive"

    assert isinstance(
        config.hours_to_pass_per_market_order, (int, float)
    ), "hours_to_pass_per_market_order must be int or float"

    assert (
        config.max_tkn_b_market_price_in_tkn_a > 0
    ), "max_tkn_b_market_price_in_tkn_a must be positive"

    assert isinstance(
        config.max_tkn_b_market_price_in_tkn_a, (int, float)
    ), "max_tkn_b_market_price_in_tkn_a must be int or float"

    assert (
        config.market_order_price_percentage_delta_to_highest_limit_order > 1
    ), "market_order_price_percentage_delta_to_highest_limit_order must be greater than 1"

    assert (
        config.market_order_price_percentage_delta_to_last_trade_price > 1
    ), "market_order_price_percentage_delta_to_last_trade_price must be greater than 1"

    assert (
        config.market_order_aggressiveness_factor > 1
    ), "market_order_aggressiveness_factor must be greater than 1"

    assert (
        config.automatic_stop_limit_price_steps_for_buying_dip > 0
    ), "automatic_stop_limit_price_steps_for_buying_dip must be positive"

    assert isinstance(config.client_order_id, str), "client_order_id must be a string"
    print("Config values validated successfully")
