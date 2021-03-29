from flask import request, jsonify
import schemas as shem
import models as m
import app_init
import services
from marshmallow import ValidationError
import datetime
import os


# Init app
app = app_init.create_app()

# Create and init Migrate
migrate = app_init.migrate
migrate.init_app(app)

# Create and init db
db = app_init.db


# Add products
@app.route('/couriers', methods=['POST'])
def add_couriers():
    data = request.json['data']
    couriers_ids_list = []
    err_couriers_ids_list = []
    flag = False
    for courier in data:
        validated = shem.courier_post_schema.validate(courier)
        if len(validated) != 0:
            err_couriers_ids_list.append({'id': courier['courier_id']})
            flag = True
            continue
        if flag:
            continue
        courier_id = courier['courier_id']
        courier_type = courier['courier_type']
        regions = courier['regions']
        working_hours = courier['working_hours']

        new_courier = m.Courier(
            courier_id=courier_id, courier_type=courier_type)
        db.session.add(new_courier)

        # Create effective validation of duplicates
        for region_req_num in regions:
            region_req = db.session.query(
                m.CourierToRegion).get(region_req_num)
            if not region_req:
                region_req = m.CourierToRegion(region=region_req_num)
                db.session.add(region_req)
            region_req.couriers.append(new_courier)

        for working_hours_req in working_hours:
            working_hours_req = services.hours_to_seconds(working_hours_req)
            working_hour_to_upload = m.CourierToWorkingHours(
                working_hours=working_hours_req, courier=new_courier)
            db.session.add(working_hour_to_upload)
        new_courier_id_dict = {'id': courier_id}
        couriers_ids_list.append(new_courier_id_dict)
        db.session.commit()

    if len(err_couriers_ids_list) != 0:
        return jsonify({"validation_error": {'couriers': err_couriers_ids_list}}), 400
    return jsonify({'couriers': couriers_ids_list}), 201


@app.route('/courier/<int:courier_id>', methods=['GET'])
def get_courier(courier_id):
    courier_req = db.session.query(m.Courier).get(courier_id)
    courier_dump = shem.courier_schema.dump(courier_req)
    salary_coefficient = courier_req.salary_coefficient
    if salary_coefficient == None:
        salary_coefficient = 0
    delivered = 0
    min_mean_time = None
    regions_to_seconds_dump = shem.regions_to_seconds_shema.dump(
        courier_req.regions_to_seconds)

    for region in regions_to_seconds_dump:
        mean_time = region['sum_time'] / region['orders_amount']
        delivered += region['orders_amount']
        if min_mean_time == None or mean_time < min_mean_time:
            min_mean_time = mean_time
    for el in range(len(courier_dump['working_hours'])):
        courier_dump['working_hours'][el] = services.seconds_to_hours(
            courier_dump['working_hours'][el])
    earnings = delivered * 500 * salary_coefficient
    if min_mean_time != None:
        rating = (60*60 - min(min_mean_time, 60*60))/(60*60) * 5
        courier_dump['rating'] = rating
    courier_dump['earnings'] = earnings

    return jsonify(courier_dump), 200


@app.route('/courier/<int:courier_id>', methods=['PATCH'])
def patch_couriers(courier_id):
    courier = m.Courier.query.get(courier_id)
    fields = request.json
    validated = shem.courier_patch_schema.validate(fields)
    if len(validated) != 0:
        print(validated)
        return {}, 400
    if 'regions' in fields:
        regions = fields['regions']
        regions_to_patch = []
        for region_num in regions:
            actual_region = db.session.query(m.CourierToRegion).get(region_num)
            if not actual_region:
                actual_region = m.CourierToRegion(region=region_num)
                actual_region.couriers.append(courier)
                db.session.add(actual_region)
            regions_to_patch.append(actual_region)
        courier.regions = regions_to_patch
    if 'courier_type' in fields:
        courier_type = fields['courier_type']
        courier.courier_type = courier_type
    if 'working_hours' in fields:
        working_hours = fields['working_hours']
        working_hours_to_patch = []
        for working_hour in working_hours:
            actual_working_hour = db.session.query(m.CourierToWorkingHours).filter(
                m.CourierToWorkingHours.working_hours == working_hour, m.CourierToWorkingHours.courier_id == courier.courier_id).all()
            if not actual_working_hour:
                working_hour = services.hours_to_seconds(working_hour)
                actual_working_hour = m.CourierToWorkingHours(
                    working_hours=working_hour, courier=courier)
                db.session.add(actual_working_hour)
            working_hours_to_patch.append(actual_working_hour)
        courier.working_hours = working_hours_to_patch

    courier_dump = shem.courier_schema.dump(courier)
    for el in range(len(courier_dump['working_hours'])):
        courier_dump['working_hours'][el] = services.seconds_to_hours(
            courier_dump['working_hours'][el])
    db.session.commit()
    return jsonify(courier_dump), 200


@app.route('/orders', methods=['POST'])
def post_orders():
    data = request.json['data']
    orders_ids_list = []
    err_orders_ids_list = []
    flag = False
    for order in data:
        validated = shem.oreder_post_schema.validate(order)
        if len(validated) != 0:
            err_orders_ids_list.append({"id": order['order_id']})
            print(validated)
            flag = True
            continue
        if flag:
            continue
        order_id = order['order_id']
        weight = order['weight']
        region = order['region']
        delivery_hours = order['delivery_hours']

        new_order = m.Order(
            order_id=order_id, weight=weight, region=region, completed=False)
        db.session.add(new_order)

        for delivery_hours_req in delivery_hours:
            delivery_hours_req = services.hours_to_seconds(delivery_hours_req)
            delivery_hours_to_upload = m.OrderToDeliveryHours(
                delivery_hours=delivery_hours_req, order=new_order)
            db.session.add(delivery_hours_to_upload)

        orders_ids_list.append({"id": order_id})
        db.session.commit()
    if len(err_orders_ids_list) != 0:
        return jsonify({"validation_error": {'orders': err_orders_ids_list}}), 400
    return jsonify({'orders': orders_ids_list}), 201


@app.route('/orders/assign', methods=['POST'])
def assign_orders():
    courier_id = request.json['courier_id']
    courier_req = db.session.query(m.Courier).get(courier_id)
    if not courier_req:
        return {}, 400
    courier_dump = shem.courier_orders_schema.dump(courier_req)
    working_hours = courier_dump['working_hours']
    if len(working_hours) == 0:
        return {}, 200
    taken_orders = courier_dump['orders']
    free_weight = services.courier_type_mapping[courier_dump['courier_type']][0] - sum(
        taken_orders)
    regions_list = courier_dump['regions']
    if len(regions_list) == 0:
        return {}, 200
    orders_assigned_ids_list = []
    available_orders = db.session.query(m.Order).filter(
        db.and_(m.Order.region.in_(regions_list), m.Order.courier_id.is_(None), m.Order.completed == False)).order_by(m.Order.weight).all()
    available_orders_dump = shem.orders_schema.dump(available_orders)

    for av_ord in range(len(available_orders)):
        order = available_orders_dump[av_ord]
        if services.order_in_working_hours(working_hours, order['delivery_hours']):
            if free_weight >= order['weight']:
                available_orders[av_ord].courier = courier_req
                free_weight -= order['weight']

    old_assign_time = courier_dump['assign_time']
    new_assign_time = datetime.datetime.utcnow().isoformat() + 'Z'
    assign_time = new_assign_time
    if old_assign_time != None:
        old_assign_time_sec = services.rfc_to_seconds(old_assign_time)
        new_assign_time_sec = services.rfc_to_seconds(new_assign_time)
        if services.time_within_period(old_assign_time_sec, new_assign_time_sec, courier_dump['working_hours']):
            assign_time = old_assign_time

    assigned_orders_list = []
    assigned_orders = shem.orders_schema.dump(courier_req.orders)
    for assigned_order in assigned_orders:
        assigned_orders_list.append({'id': assigned_order['order_id']})

    if assign_time == new_assign_time and len(assigned_orders_list) > 0:
        courier_req.prev_delivery_end = services.rfc_to_seconds(
            new_assign_time)
        courier_req.assign_time = new_assign_time
        courier_req.salary_coefficient = services.courier_type_mapping[
            courier_dump['courier_type']][1]
        db.session.commit()
    elif len(assigned_orders_list) == 0:
        return {}, 200

    return jsonify({'orders': assigned_orders_list, 'assign_time': assign_time}), 200


@app.route('/orders/complete', methods=['POST'])
def complete_order():
    courier_id = request.json['courier_id']
    courier_req = db.session.query(m.Courier).get(courier_id)

    order_id = request.json['order_id']
    order_req = db.session.query(m.Order).get(order_id)

    complete_time = request.json['complete_time']
    complete_time = services.rfc_to_seconds(complete_time)

    if not order_req or not order_req.courier_id or not order_req in courier_req.orders:
        return {}, 400

    order_req.courier = None
    order_req.completed = True

    seconds_passed = complete_time - courier_req.prev_delivery_end
    region_seconds_req = db.session.query(
        m.RegionToSeconds).get(order_req.region)
    if not region_seconds_req:
        region_seconds_req = m.RegionToSeconds(
            region=order_req.region, sum_time=0, orders_amount=0, courier=courier_req)

        db.session.add(region_seconds_req)
    region_seconds_req.sum_time += seconds_passed
    region_seconds_req.orders_amount += 1

    courier_req.prev_delivery_end = complete_time

    db.session.commit()

    return {'order_id': order_req.order_id}, 200


    # Run server
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
