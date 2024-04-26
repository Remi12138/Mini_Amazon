import psycopg2
from mysocket import *
from ack import ack_list
from checkAck import *
from psycopg2 import OperationalError
from protocal import amazon_ups_pb2 as ups
from connectdb import get_db_connection



def toOrderTruck(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()

    try:
        req_msg = ups.ACommand()
        ordertruck_msg = req_msg.toOrder.add()
        # product_msg = ordertruck_msg.productInfo.add()
        # Fetch users_orderitem, users_product, users_warehouse, and users_order details for the given orderID
        cursor.execute("""
            SELECT p.id, p.description, oi.quantity, w.id, w.x, w.y, o."upsUsername", o.des_x, o.des_y
            FROM users_orderitem oi
            JOIN users_product p ON oi.product_id = p.id
            JOIN users_warehouse w ON p.warehouse_id = w.id
            JOIN users_order o ON oi.order_id_id = o.id
            WHERE oi.order_id_id = %s
        """, (orderID,))
        all_products = cursor.fetchall()
        for product in all_products:
            product_msg = ordertruck_msg.productInfo.add()
            product_msg.productID = product[0]
            product_msg.description = product[1]
            product_msg.count = product[2]
            
        ordertruck_msg.packageID = orderID
        ordertruck_msg.warehouseInfo.warehouseID = all_products[0][3]
        ordertruck_msg.warehouseInfo.x = all_products[0][4]
        ordertruck_msg.warehouseInfo.y = all_products[0][5]
        ordertruck_msg.destinationInfo.x = all_products[0][7]
        ordertruck_msg.destinationInfo.y = all_products[0][8]
        ordertruck_msg.upsUsername = all_products[0][6] if all_products[0][6] is not None else 'user1'
        
        # generate a seq_num
        seqNum = ack_list.add_request()
        ordertruck_msg.seqnum = seqNum
        print("Before send ups: toOrderTruck")
        print("OrderTruck msg: ", req_msg)
        checkAndSendReq(fd, req_msg, seqNum)
        print("(end send)After send ups: toOrderTruck")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
    

def toOrderTruck2(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()

    try:
        req_msg = ups.ACommand()
        ordertruck_msg = req_msg.toOrder.add()
        # product_msg = ordertruck_msg.productInfo.add()
        # Fetch users_orderitem, users_product, users_warehouse, and users_order details for the given orderID
        cursor.execute("""
            SELECT p.id, p.description, oi.quantity, w.id, w.x, w.y, o."upsUsername", o.des_x, o.des_y
            FROM users_orderitem oi
            JOIN users_product p ON oi.product_id = p.id
            JOIN users_warehouse w ON p.warehouse_id = w.id
            JOIN users_order o ON oi.order_id_id = o.id
            WHERE oi.order_id_id = %s
        """, (orderID,))
        all_products = cursor.fetchall()
        for product in all_products:
            product_msg = ordertruck_msg.productInfo.add()
            product_msg.productID = product[0]
            product_msg.description = product[1]
            product_msg.count = product[2]
            
        ordertruck_msg.packageID = orderID
        ordertruck_msg.warehouseInfo.warehouseID = all_products[0][3]
        ordertruck_msg.warehouseInfo.x = all_products[0][4]
        ordertruck_msg.warehouseInfo.y = all_products[0][5]
        ordertruck_msg.destinationInfo.x = all_products[0][7]
        ordertruck_msg.destinationInfo.y = all_products[0][8]
        ordertruck_msg.upsUsername = all_products[0][6] if all_products[0][6] is not None else 'user1'
        
        # generate a seq_num
        seqNum = ack_list.add_request()
        ordertruck_msg.seqnum = seqNum
        print("Before send ups: toOrderTruck")
        sendRequest(fd, req_msg)
        #checkAndSendReq(fd, req_msg, seqNum)
        print("(end send)After send ups: toOrderTruck")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
    
def startDelivery(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:
        # Update the order status to 'delivering' before sending the delivery command
        update_query = 'UPDATE "users_order" SET status = %s WHERE id = %s'
        cursor.execute(update_query, ('delivering', orderID))
        conn.commit()

        # Preparing the message for delivery start
        req_msg = ups.ACommand()
        startDelivery_msg = req_msg.toStart.add()
        startDelivery_msg.packageID = orderID
        
        # Generate a seq_num
        seqNum = ack_list.add_request()
        startDelivery_msg.seqnum = seqNum

        print("Before send ups: startDelivery")
        # Send until receive acks
        checkAndSendReq(fd, req_msg, seqNum)
        print("(end send)After send ups: startDelivery")

        print("Delivery started for order ID:", orderID)

    except psycopg2.Error as e:
        print(f"An error occurred while updating order status or sending start delivery message: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


def delivered(fd, orderID):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:
        # Update the order status to 'delivered'
        update_query = 'UPDATE "users_order" SET status = %s WHERE id = %s'
        cursor.execute(update_query, ('delivered', orderID))
        conn.commit()
        print(f"users_order {orderID} has been marked as delivered.")

    except psycopg2.Error as e:
        # If an error occurs, print an error message and rollback any changes
        print(f"An error occurred while updating the order status to 'delivered': {e}")
        conn.rollback()

    finally:
        # Clean up by closing cursor and connection
        cursor.close()
        conn.close()
  
        
        
# 4.22
def sendName(fd, Name):
    print("enter sendName!")    
    req_msg = ups.ACommand()
    checkName_msg = req_msg.checkUsers.add()
    checkName_msg.upsUsername = Name
    # Generate a seq_num
    seqNum = ack_list.add_request()
    checkName_msg.seqnum = seqNum
    # Send the UPS username to UPS
    checkAndSendReq(fd, req_msg, seqNum)
   
        

def update_des(change_row):
    conn = get_db_connection()
    if not conn:
        return 
    cursor = conn.cursor()
    
    try:
        # Update the order destination 
        sql_query = '''
            UPDATE users_order
            SET des_x = %s, des_y = %s
            WHERE id = %s;
        '''
        # Execute the SQL query
        cursor.execute(sql_query, [change_row.NewDestination.x, change_row.NewDestination.y, change_row.packageID])
        conn.commit()
        print(f"Order ID {change_row.packageID} destination updated to ({change_row.NewDestination.x}, {change_row.NewDestination.y}).")

    except psycopg2.Error as e:
        # If an error occurs, print an error message and rollback any changes
        print(f"An error occurred while change the order destination: {e}")
        conn.rollback()

    finally:
        # Clean up by closing cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def sendEmailErrorUser(adminEmail, adminName, userEmail, userName):
    api_key = '2b3c16d686e729b76eeacb6ce417b7b1'
    api_secret = '6c4b3e2da82b3ffb2d3252fd8742ecda'
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
    'Messages': [
        {
        "From": {
            "Email": adminEmail,
            "Name": adminName,
        },
        "To": [
            {
            "Email": userEmail,
            "Name": userName,
            }
        ],
        "Subject": "MiniAmazon Order Confirmation",
        "TextPart": "Your UPS user name does not exist! Please re-input your UPS name!",
        "CustomID": "AppGettingStartedTest"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())    
