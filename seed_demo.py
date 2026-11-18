from todo_agent import add_task
from calendar_agent import add_event

print(add_task("Pay the stationery supplier", "today"))
print(add_task("Call cousin Neha", "tomorrow"))
print(add_task("Order chart paper", "2020-01-01"))      # an old task, so it is overdue
print(add_event("Parent meeting", "today", "11:00", 30))
print(add_event("Supplier visit", "today", "15:00", 60))
