""" Business logic for the dealicious router."""
import logging
import re

import fastapi
from fastapi import status
import python_picnic_api

from src.core.config import get_settings

logger = logging.getLogger(get_settings().LOGGER_CONTROLLERS_NAME)


def _get_shopping_cart_if_available(pc_session: python_picnic_api.PicnicAPI) -> list:
    """Return the shopping cart if everything is available.

    Args:
        pc_session: The picnic session

    Returns:
        The shopping cart.

    Raises:
        400: If the shopping cart contains unavailable products.

    """
    logger.debug("Getting shopping cart.")
    shopping_cart = [data["items"][0] for data in pc_session.get_cart()["items"]]
    _check_availability_product(shopping_cart)

    return shopping_cart


def _check_availability_product(shopping_cart: list[dict]) -> None:
    """Check if there are unavailable products in the cart.

    Args:
        shopping_cart: The shopping cart.

    Returns:
        None

    Raises:
        400: If there are unavailable products in the cart.

    """
    logger.debug("Checking availability of products in cart.")
    unavailable_products = [
        product["name"]
        for product in shopping_cart
        if "UNAVAILABLE" in str(product["decorators"])
    ]
    if unavailable_products:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unavailable products in cart: {unavailable_products}.",
        )


def _find_last_number_below(given_number: int, num_list: list[int]) -> tuple[int, int]:
    """Return the last number that is below the given number.

    Args:
        given_number: The given number.
        num_list: The list of numbers to check.

    Returns:
        The last number that is below the given number.

    """
    last_number = 0
    last_index = 0
    for index, num in enumerate(num_list):
        if num <= given_number:
            last_number = num
            last_index = index

    return last_index, last_number


def _return_info_discount_product(
    product: dict,
    search_results: list[dict],
) -> tuple[list[int], list[dict]]:
    """Return a list with indexes and info of the products that can be combined.

    Args:
        product: The product to add.
        search_results: The search results.

    Returns:
        A list with indexes and info of the products that can be combined.
    """
    num_list = []
    use_ful_list = []
    equal_product_info = [
        result for result in search_results if result["id"] == product["id"]
    ][0]
    for result in search_results:
        if (
            result["type"] == "SINGLE_ARTICLE"
            and product["unit_quantity"] in result["unit_quantity"]
            and product["unit_quantity"] != result["unit_quantity"]
            and str(product["name"]) == str(result["name"])
            and len(result["decorators"]) == len(equal_product_info["decorators"])
        ):
            num_list.append(int(result["unit_quantity"][0]))
            use_ful_list.append(result)

    return num_list, use_ful_list


def _add_to_cart(
    pc_session: python_picnic_api.PicnicAPI,
    product: dict,
    original_quantity: int,
    num_list: list[int],
    use_ful_list: list[dict],
) -> None:
    """Add a product to the cart while also removing the difference.

    Args:
        pc_session: The picnic session.
        product: The product to add.
        quantity: The quantity of the product to add.
        num_list: The list of numbers that can be combined.
        use_ful_list: The list of products that can be combined.

    Returns:
        None

    """
    difference = original_quantity
    while difference > 1:
        last_index, last_number = _find_last_number_below(difference, num_list)
        difference = difference - last_number
        pc_session.remove_product(product["id"], count=last_number)
        pc_session.add_product(use_ful_list[last_index]["id"], count=1)


def _extract_integers(promo_text: str) -> int:
    """Extracts integers from a string.

    Args:
        promo_text: The promo text.

    Returns:
        The sum of the extracted integers.

    """
    positive_integers_list = re.findall(r"\b\d+\b", promo_text)

    return sum(int(num) for num in positive_integers_list)


def post_combine(
    pc_session: python_picnic_api.PicnicAPI,
) -> None:
    """Combines products in the shopping cart to achieve discount.

    Args:
        pc_session: The picnic session.

    Returns:
        None

    """
    logger.info("Combining discounts.")
    shopping_cart = _get_shopping_cart_if_available(pc_session)

    for product in shopping_cart:
        name = product["name"]
        original_quantity = product["decorators"][0]["quantity"]
        if original_quantity == 1:
            logger.debug(f"Skipping {name} because it has a quantity of 1.")
            continue

        logger.debug(f"Combining discounts for {name}.")
        search_results = pc_session.search(name)[0]["items"]
        num_list, use_ful_list = _return_info_discount_product(product, search_results)
        if not num_list:
            logger.debug(f"No discounts found for {name}.")
            continue

        _add_to_cart(
            pc_session=pc_session,
            product=product,
            original_quantity=original_quantity,
            num_list=num_list,
            use_ful_list=use_ful_list,
        )


def get_promo(
    pc_session: python_picnic_api.PicnicAPI,
) -> list[dict]:
    """Searches for promo discount possibilities.

    Args:
        pc_session: The picnic session.

    Returns:
        A list with all the promo possibilities.

    """
    logger.info("Searching for promo discount.")
    shopping_cart = _get_shopping_cart_if_available(pc_session)

    promo_products = []
    for product in shopping_cart:
        original_product = pc_session.search(product["name"])[0]["items"][0]
        if "PROMO" in str(original_product["decorators"]):
            logger.debug(f"Found promo discount for {original_product['name']}.")
            product_info = {
                "name": product["name"],
                "id": product["id"],
                "quantity": product["decorators"][0]["quantity"],
            }
            for decorator in original_product["decorators"]:
                if decorator["type"] == "PROMO":
                    product_info["promo_text"] = decorator["text"]
            promo_products.append(product_info)

    return promo_products


def post_promo(
    promo_input: list[dict],
    pc_session: python_picnic_api.PicnicAPI,
) -> None:
    """Applies promo discount.

    Args:
        promo_input: The promo input.
        pc_session: The picnic session.

    Returns:
        None

    """
    logger.info("Applying promo discount.")
    for product in promo_input:
        logger.debug(f"Applying promo discount for {product['name']}.")
        total_quantity = _extract_integers(product["promo_text"])
        pc_session.add_product(
            product["id"],
            count=(total_quantity - product["quantity"]),
        )
