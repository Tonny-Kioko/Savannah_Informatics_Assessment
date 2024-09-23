import africastalking
import os
from core.models import Customer, Order

from decouple import config

username = config('MY_USERNAME')
api_key = config('API_KEY')
sender = config('SENDER')


africastalking.initialize(username, api_key)
sms = africastalking.SMS

class SendSms:
  def sending(self, order, customer):    
    
    recipients = [customer.phone_number]


    message = f"Hi {customer.email}, your order {order.order_number} totalling KES {order.amount} has been created successfully!"
    sms_sender = sender

    try:
      response = sms.send(message, recipients, sms_sender)
      print(response)
    except Exception as e:
      print(f"Order Placement Services, we have a problem: {e}")
