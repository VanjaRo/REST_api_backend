from app_init import ma
import models as m
from marshmallow import ValidationError, validate
import services as serv


class RegionToSecondsSchema(ma.SQLAlchemySchema):
    sum_time = ma.Int()
    orders_amount = ma.Int()


class OrderToDeliveryHoursSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = m.OrderToDeliveryHours


class OrderSchema(ma.SQLAlchemySchema):
    class Meta:
        model = m.Order
    order_id = ma.Int()
    weight = ma.Float()
    region = ma.Int()
    courier_id = ma.Int()
    delivery_hours = ma.Pluck(
        OrderToDeliveryHoursSchema, 'delivery_hours', many=True)


# Courier to working hours Schema
class CourierToWorkingHoursSchema(ma.SQLAlchemySchema):
    class Meta:
        model = m.CourierToWorkingHours
    working_hours = ma.Str(required=True)


# Courier to region Schema
class CourierToRegionSchema(ma.SQLAlchemySchema):
    region = ma.Int(required=True)


# Courier post request Schema (for validation)
class CourierPostSchema(ma.Schema):
    courier_id = ma.Int(required=True)
    courier_type = ma.Str(validate=validate.OneOf(
        ['foot', 'bike', 'car']), required=True)
    regions = ma.List(ma.Int, required=True)
    working_hours = ma.List(
        ma.Str, required=True)


# Courier patch request Schema (for validation)
class CourierPatchSchema(ma.Schema):
    courier_type = ma.Str(validate=validate.OneOf(
        ['foot', 'bike', 'car']))
    regions = ma.List(ma.Int)
    working_hours = ma.List(ma.Str)


# Order post request Schema (for validation)
class OrderPostSchema(ma.Schema):
    order_id = ma.Int(required=True)
    weight = ma.Float(required=True)
    region = ma.Int(required=True)
    delivery_hours = ma.List(
        ma.Str, required=True)


# Courier Schema
class CourierSchema(ma.SQLAlchemySchema):
    class Meta:
        model = m.Courier
    courier_id = ma.Int()
    courier_type = ma.Method('get_courier_type')
    regions = ma.Pluck(CourierToRegionSchema, 'region', many=True)
    working_hours = ma.Pluck(
        CourierToWorkingHoursSchema, 'working_hours', many=True)

    def get_courier_type(self, obj):
        return obj.courier_type.value


class CourierOrdersSchema(CourierSchema):
    orders = ma.Pluck(
        OrderSchema, 'weight', many=True)
    assign_time = ma.Str()


# Init schema
courier_orders_schema = CourierOrdersSchema()
couriers_orders_schema = CourierOrdersSchema(many=True)
region_to_seconds_shema = RegionToSecondsSchema()
regions_to_seconds_shema = RegionToSecondsSchema(many=True)
courier_post_schema = CourierPostSchema()
courier_patch_schema = CourierPatchSchema()
oreder_post_schema = OrderPostSchema()
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
courier_schema = CourierSchema()
couriers_schema = CourierSchema(many=True)
courier_to_region_schema = CourierToRegionSchema()
courier_to_regions_schema = CourierToRegionSchema(many=True)
courier_to_working_hours_schema = CourierToWorkingHoursSchema()
