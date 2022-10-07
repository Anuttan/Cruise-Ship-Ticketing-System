from django.db import models

# Create your models here.
class TicketItem(models.Model):
    ship_name = models.TextField()
    ship_date = models.TextField()
    ship_capacity = models.IntegerField()
    ship_booked_seats = models.IntegerField()
    ship_remained_seats = models.IntegerField()
    ship_price = models.TextField()
    depart_city = models.TextField()
    arrive_city = models.TextField()
    depart_seaport = models.TextField()
    arrive_seaport = models.TextField()
    depart_time = models.TextField()
    arrive_time = models.TextField()


class BookTicketItem(models.Model):
    user_id = models.IntegerField()
    ticket_id = models.ForeignKey(TicketItem, on_delete=models.CASCADE)
    book_status = models.TextField()
    seat_id = models.TextField()


class CheckinItem(models.Model):
    ticket_id = models.ForeignKey(TicketItem, on_delete=models.CASCADE)
    checkin_windows = models.TextField()
    boarding_port = models.TextField()
