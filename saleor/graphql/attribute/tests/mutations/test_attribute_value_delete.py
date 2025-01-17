from unittest import mock

import graphene
import pytest
from django.utils.functional import SimpleLazyObject
from freezegun import freeze_time

from .....attribute.utils import associate_attribute_values_to_instance
from .....webhook.event_types import WebhookEventAsyncType
from .....webhook.payloads import generate_meta, generate_requestor

ATTRIBUTE_VALUE_DELETE_MUTATION = """
    mutation AttributeValueDelete($id: ID!) {
        attributeValueDelete(id: $id) {
            attributeValue {
                name
                slug
            }
        }
    }
"""


def test_delete_attribute_value(
    staff_api_client,
    color_attribute,
    pink_attribute_value,
    permission_manage_product_types_and_attributes,
):
    # given
    value = color_attribute.values.get(name="Red")
    query = ATTRIBUTE_VALUE_DELETE_MUTATION
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"id": node_id}

    # when
    staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_types_and_attributes]
    )

    # then
    with pytest.raises(value._meta.model.DoesNotExist):
        value.refresh_from_db()


@freeze_time("2022-05-12 12:00:00")
@mock.patch("saleor.plugins.webhook.plugin.get_webhooks_for_event")
@mock.patch("saleor.plugins.webhook.plugin.trigger_webhooks_async")
def test_delete_attribute_value_trigger_webhooks(
    mocked_webhook_trigger,
    mocked_get_webhooks_for_event,
    any_webhook,
    staff_api_client,
    color_attribute,
    pink_attribute_value,
    permission_manage_product_types_and_attributes,
    settings,
):
    # given
    mocked_get_webhooks_for_event.return_value = [any_webhook]
    settings.PLUGINS = ["saleor.plugins.webhook.plugin.WebhookPlugin"]

    value = color_attribute.values.get(name="Red")
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"id": node_id}

    # when
    staff_api_client.post_graphql(
        ATTRIBUTE_VALUE_DELETE_MUTATION,
        variables,
        permissions=[permission_manage_product_types_and_attributes],
    )

    # then
    mocked_webhook_trigger.assert_called_once_with(
        {
            "id": graphene.Node.to_global_id("Attribute", color_attribute.id),
            "name": color_attribute.name,
            "slug": color_attribute.slug,
            "meta": generate_meta(
                requestor_data=generate_requestor(
                    SimpleLazyObject(lambda: staff_api_client.user)
                )
            ),
        },
        WebhookEventAsyncType.ATTRIBUTE_UPDATED,
        [any_webhook],
        color_attribute,
        SimpleLazyObject(lambda: staff_api_client.user),
    )


def test_delete_file_attribute_value(
    staff_api_client,
    file_attribute,
    permission_manage_product_types_and_attributes,
):
    # given
    value = file_attribute.values.first()
    query = ATTRIBUTE_VALUE_DELETE_MUTATION
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"id": node_id}

    # when
    staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_types_and_attributes]
    )

    # then
    with pytest.raises(value._meta.model.DoesNotExist):
        value.refresh_from_db()


def test_delete_attribute_value_product_search_document_updated(
    staff_api_client,
    color_attribute,
    permission_manage_product_types_and_attributes,
    product,
):
    # given
    attribute = color_attribute
    name = "Red"
    value = color_attribute.values.get(name=name)

    product_type = product.product_type
    product_type.product_attributes.add(attribute)

    associate_attribute_values_to_instance(product, attribute, value)

    query = ATTRIBUTE_VALUE_DELETE_MUTATION
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"id": node_id}

    # when
    staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_types_and_attributes]
    )

    # then
    with pytest.raises(value._meta.model.DoesNotExist):
        value.refresh_from_db()


def test_delete_attribute_value_product_search_document_updated_variant_attribute(
    staff_api_client,
    color_attribute,
    permission_manage_product_types_and_attributes,
    variant,
):
    # given
    name = "Red"
    attribute = color_attribute
    value = color_attribute.values.get(name=name)

    product = variant.product
    product_type = product.product_type
    product_type.variant_attributes.add(attribute)

    associate_attribute_values_to_instance(variant, attribute, value)

    query = ATTRIBUTE_VALUE_DELETE_MUTATION
    node_id = graphene.Node.to_global_id("AttributeValue", value.id)
    variables = {"id": node_id}

    # when
    staff_api_client.post_graphql(
        query, variables, permissions=[permission_manage_product_types_and_attributes]
    )

    # then
    with pytest.raises(value._meta.model.DoesNotExist):
        value.refresh_from_db()
