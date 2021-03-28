from app_init import db
import datetime as dt
import enum


class CourierType(enum.Enum):
    foot = 'foot'
    bike = 'bike'
    car = 'car'


couriers_regions_association = db.Table(
    'couriers_regions',
    db.Column('courier_id', db.Integer, db.ForeignKey('courier.courier_id')),
    db.Column('reg_id', db.Integer, db.ForeignKey('courier_to_region.region'))
)


# Courier Class/Model
class Courier(db.Model):
    courier_id = db.Column(db.Integer, primary_key=True)
    courier_type = db.Column(db.Enum(CourierType), nullable=False)
    regions = db.relationship(
        'CourierToRegion', secondary=couriers_regions_association, back_populates='couriers')
    working_hours = db.relationship(
        'CourierToWorkingHours', cascade='delete, delete-orphan', back_populates='courier')
    orders = db.relationship('Order', back_populates='courier')
    rating = db.Column(db.Float)
    earnings = db.Column(db.Integer)
    regions_to_seconds = db.relationship(
        'RegionToSeconds', cascade='delete, delete-orphan', back_populates='courier')
    prev_delivery_end = db.Column(db.Integer)
    salary_coefficient = db.Column(db.Integer)
    assign_time = db.Column(db.String(27))


# Courier to region Class/Model
class CourierToRegion(db.Model):
    couriers = db.relationship(
        'Courier', secondary=couriers_regions_association, back_populates='regions'
    )
    region = db.Column(db.Integer, nullable=False, primary_key=True)


# Courier to working hours Class/Model
class CourierToWorkingHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    working_hours = db.Column(db.String(11), nullable=False)
    courier_id = db.Column(db.Integer, db.ForeignKey(
        'courier.courier_id'), nullable=False)
    courier = db.relationship('Courier', back_populates='working_hours')


# Order Class/Model
class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    courier_id = db.Column(db.Integer, db.ForeignKey('courier.courier_id'))
    courier = db.relationship('Courier', back_populates='orders')
    region = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    delivery_hours = db.relationship(
        'OrderToDeliveryHours', cascade='delete, delete-orphan', back_populates='order')
    completed = db.Column(db.Boolean)


# Order to delivery hours Class/Model
class OrderToDeliveryHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_hours = db.Column(db.String(11), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'order.order_id'), nullable=False)
    order = db.relationship('Order', back_populates='delivery_hours')


# Region to summurised courier deilivery time in seconds Class/Model
class RegionToSeconds(db.Model):
    region = db.Column(db.Integer, primary_key=True)
    courier_id = courier_id = db.Column(db.Integer, db.ForeignKey(
        'courier.courier_id'), nullable=False)
    courier = db.relationship('Courier', back_populates='regions_to_seconds')
    sum_time = db.Column(db.Integer)
    orders_amount = db.Column(db.Integer)
