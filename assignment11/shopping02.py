import time
import asyncio
from asyncio import Queue
from random import randrange

# we first implement the Customer and Product classes, 
# representing customers and products that need to be checked out. 
# The Product class has a checkout_time attribute, 
# which represents the time required for checking out the product.
class Product:
    def __init__(self, product_name: str, checkout_time: float):
        self.product_name = product_name
        self.checkout_time = checkout_time

class Customer:
    def __init__(self, customer_id: int, products: list[Product]):
        self.customer_id = customer_id
        self.products = products

async def checkout_customer(queue: Queue, cashier_number: int):
    customer_count = 0  
    total_time = 0  
    while not queue.empty():   
        customer: Customer = await queue.get()
        
        customer_start_time = time.perf_counter()
        print(f"The Cashier_{cashier_number}"
              f" will checkout Customer_{customer.customer_id}") 

        for product in customer.products:
            print(f"The cashier_{cashier_number}"
                  f" will checkout Customer_{customer.customer_id}'s"
                  f" product_{product.product_name}"
                  f" in {product.checkout_time} secs")
            
            await asyncio.sleep(product.checkout_time)

        
        print(f" The cashier_{cashier_number}"
              f" finish checkout Customer_{customer.customer_id}"
              f" in {round(time.perf_counter() - customer_start_time, ndigits = 2)} secs")
        
        checkout_duration = round(time.perf_counter() - customer_start_time, ndigits=2)
        customer_count += 1
        total_time += checkout_duration 
        queue.task_done()
        

    return customer_count, total_time
    

# we implement the generate_customer method as a factory method for producing customers.
#
# We first define a product series and the required checkout time for each product. 
# Then, we place 0 to 4 products in each customer’s shopping cart.
def generate_customer(customer_id: int) -> Customer:
    all_products = [Product('beef', 1),
                    Product('banana', .4),
                    Product('sausage', .4),
                    Product('diapers', .2)]
    return Customer(customer_id, all_products)

# we implement the customer_generation method as a producer. 
# This method generates several customer instances regularly 
# and puts them in the queue. If the queue is full, the put method will wait.
async def customer_generation(queue: Queue, customers: int):
    customer_count = 0
    while True:
        customers = [generate_customer(the_id)
                     for the_id in range(customer_count, customer_count + customers)]
        
        for customer in customers:
            print("waiting to put customer in line....")
            await queue.put(customer)
            print("Customer put in line....")
        
        customer_count = customer_count + len(customers)
        await asyncio.sleep(.001)
        return customer_count


# Finally, we use the main method to initialize the queue, 
# producer, and consumer, and start all concurrent tasks.
async def main():
    CUSTOMER = 10
    QUEUE = 3
    CASHIER = 5
    customer_queue = Queue(QUEUE)
    customer_start_time = time.perf_counter()
    customer_producer = asyncio.create_task(customer_generation(customer_queue, CUSTOMER))
    cashiers = [checkout_customer(customer_queue, i) for i in range(CASHIER)]
    results = await asyncio.gather(customer_producer, *cashiers)
    print("---------------------")
    for i, (customer_count, total_time) in enumerate(results[1:]):  
        print(f"The Cashier_{i} take {customer_count} customers total {round(total_time, 2)} secs")
    
    print(f"The supermarket process finish"
          f"{customer_producer.result()} customers"
            f" in {round(time.perf_counter() - customer_start_time, ndigits= 2)} secs")
    
if __name__ == "__main__":
    asyncio.run(main())