from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

PERMISSIONS_ACTIVES = [
    "add_bill",
    #"change_bill",
    #"delete_bill",
    "view_bill",
    "add_count",
    "change_count",
    "delete_count",
    "view_count",
    "add_platform",
    "change_platform",
    "delete_platform",
    "view_platform",
    "add_profile",
    "change_profile",
    "delete_profile",
    "view_profile",
    "add_promotion",
    "change_promotion",
    "delete_promotion",
    "view_promotion",
    "add_sale",
    "change_sale",
    "delete_sale",
    "view_sale",
    "add_promotionsale",
    "change_promotionsale",
    "delete_promotionsale",
    "view_promotionsale",
    "add_promotionplatform",
    "change_promotionplatform",
    "delete_promotionplatform",
    "view_promotionplatform",
    "add_price",
    "change_price",
    "delete_price",
    "view_price",
    "add_customer",
    "change_customer",
    "delete_customer",
    "view_customer",
    "add_action",
    "change_action",
    "delete_action",
    "view_actionv"
]
