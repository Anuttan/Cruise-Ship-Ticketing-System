from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import TicketItem, BookTicketItem
from django.contrib import messages
from django.db.models import Q

# Create your views here.
def index(request):
    return render(request, 'index.html')


def ticket_info(request):
    all_ticket_items = TicketItem.objects.all()
    return render(request, 'TicketInfo.html', {'all_items': all_ticket_items})


def search_ticket(request):
    ship_name = request.POST['search_ship_name']
    ship_date = request.POST['search_ship_date']
    ship_capacity = request.POST['search_ship_capacity']
    ship_booked_seats = request.POST['search_ship_booked_seats']
    ship_remained_seats = request.POST['search_ship_remained_seats']
    ship_price = request.POST['search_ship_price']
    depart_city = request.POST['search_depart_city']
    arrive_city = request.POST['search_arrive_city']
    depart_seaport = request.POST['search_depart_seaport']
    arrive_seaport = request.POST['search_arrive_seaport']
    depart_time = request.POST['search_depart_time']
    arrive_time = request.POST['search_arrive_time']
    all_ticket_items = TicketItem.objects.all()
    if ship_name:
        all_ticket_items = all_ticket_items.filter(ship_name=ship_name)
    if ship_date:
        all_ticket_items = all_ticket_items.filter(ship_date=ship_date)
    if ship_capacity:
        all_ticket_items = all_ticket_items.filter(ship_capacity=ship_capacity)
    if ship_booked_seats:
        all_ticket_items = all_ticket_items.filter(ship_booked_seats=ship_booked_seats)
    if ship_remained_seats:
        all_ticket_items = all_ticket_items.filter(ship_remained_seats=ship_remained_seats)
    if ship_price:
        all_ticket_items = all_ticket_items.filter(ship_price=ship_price)
    if depart_city:
        all_ticket_items = all_ticket_items.filter(depart_city=depart_city)
    if arrive_city:
        all_ticket_items = all_ticket_items.filter(arrive_city=arrive_city)
    if depart_seaport:
        all_ticket_items = all_ticket_items.filter(depart_seaport=depart_seaport)
    if arrive_seaport:
        all_ticket_items = all_ticket_items.filter(arrive_seaport=arrive_seaport)
    if depart_time:
        all_ticket_items = all_ticket_items.filter(depart_time=depart_time)
    if arrive_time:
        all_ticket_items = all_ticket_items.filter(arrive_time=arrive_time)
    return render(request, 'TicketInfo.html', {'all_items': all_ticket_items})


@login_required(login_url='login')
def pre_book_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.filter(id=ticket_id)
    if request.method == 'POST':
        return render(request, 'BookTicket.html', {'all_items': ticket_item})
    return HttpResponseRedirect('/ticketInfo/')


@login_required(login_url='login')
def book_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.get(id=ticket_id)
    book_ticket_item = BookTicketItem.objects.filter(user_id=request.user.id, book_status='Booked')
    if ticket_item in book_ticket_item:
        messages.error(request, 'Already Booked')
    else:
        if request.method == 'POST':
            if ticket_item.ship_remained_seats > 0:
                ticket_item.ship_booked_seats += 1
                ticket_item.ship_remained_seats -= 1
                ticket_item.save()
                book_ticket_item = BookTicketItem(user_id=request.user.id, ticket_id=ticket_item,
                                                  book_status='Booked', seat_id=str(ticket_item.ship_booked_seats))
                book_ticket_item.save()
        return HttpResponseRedirect('/myTicketInfo/')


@login_required(login_url='login')
def checkin_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.filter(id=ticket_id, checkinitem__ticket_id=ticket_id).values(
                                            'id', 'ship_name', 'ship_date', 'ship_capacity',
                                            'ship_booked_seats', 'ship_remained_seats',
                                            'ship_price', 'depart_city', 'arrive_city',
                                            'depart_seaport', 'arrive_seaport', 'depart_time',
                                            'arrive_time', 'checkinitem__checkin_windows',
                                            'checkinitem__boarding_port', 'bookticketitem__seat_id')
    if request.method == 'POST':
        return render(request, 'CheckinTicket.html', {'all_items': ticket_item})
    return HttpResponseRedirect('/myTicketInfo/')


@login_required(login_url='login')
def pre_pay_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.filter(id=ticket_id)
    if request.method == 'POST':
        return render(request, 'PayTicket.html', {'all_items': ticket_item})
    return HttpResponseRedirect('/myTicketInfo/')


@login_required(login_url='login')
def pay_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.get(id=ticket_id)
    if request.method == 'POST':
        book_ticket_item = BookTicketItem.objects.filter(user_id=request.user.id, ticket_id=ticket_item,
                                                         book_status='Booked').first()
        if book_ticket_item:
            book_ticket_item.book_status = 'Paid'
            book_ticket_item.save()
    return HttpResponseRedirect('/myTicketInfo/')


@login_required(login_url='login')
def pre_cancel_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.filter(id=ticket_id)
    if request.method == 'POST':
        return render(request, 'CancelTicket.html', {'all_items': ticket_item})
    return HttpResponseRedirect('/myTicketInfo/')


@login_required(login_url='login')
def cancel_ticket(request, ticket_id):
    ticket_item = TicketItem.objects.get(id=ticket_id)
    if request.method == 'POST':
        ticket_item.ship_booked_seats -= 1
        ticket_item.ship_remained_seats += 1
        ticket_item.save()
        book_ticket_item = BookTicketItem.objects.filter(Q(book_status='Booked') | Q(book_status='Paid'),
                                                         user_id=request.user.id, ticket_id=ticket_item,
                                                         ).first()
        book_ticket_item.book_status = 'Cancelled'
        book_ticket_item.save()
    return HttpResponseRedirect('/myTicketInfo/')


@login_required(login_url='login')
def my_ticket_info(request):
    all_ticket_items = TicketItem.objects.filter(Q(bookticketitem__book_status='Booked') |
                                                 Q(bookticketitem__book_status='Paid'),
                                                 bookticketitem__user_id=request.user.id).values(
                                                    'id', 'ship_name', 'ship_date', 'ship_capacity',
                                                    'ship_booked_seats', 'ship_remained_seats',
                                                    'ship_price', 'depart_city', 'arrive_city',
                                                    'depart_seaport', 'arrive_seaport', 'depart_time',
                                                    'arrive_time', 'bookticketitem__book_status')
    return render(request, 'MyTicketInfo.html', {'all_items': all_ticket_items})


@login_required(login_url='login')
def search_my_ticket(request):
    ship_name = request.POST['search_ship_name']
    ship_date = request.POST['search_ship_date']
    ship_capacity = request.POST['search_ship_capacity']
    ship_booked_seats = request.POST['search_ship_booked_seats']
    ship_remained_seats = request.POST['search_ship_remained_seats']
    ship_price = request.POST['search_ship_price']
    depart_city = request.POST['search_depart_city']
    arrive_city = request.POST['search_arrive_city']
    depart_seaport = request.POST['search_depart_seaport']
    arrive_seaport = request.POST['search_arrive_seaport']
    depart_time = request.POST['search_depart_time']
    arrive_time = request.POST['search_arrive_time']
    book_status = request.POST['search_book_status']
    all_ticket_items = TicketItem.objects.filter(Q(bookticketitem__book_status='Booked') |
                                                 Q(bookticketitem__book_status='Paid'),
                                                 bookticketitem__user_id=request.user.id).values(
                                                    'id', 'ship_name', 'ship_date', 'ship_capacity',
                                                    'ship_booked_seats', 'ship_remained_seats',
                                                    'ship_price', 'depart_city', 'arrive_city',
                                                    'depart_seaport', 'arrive_seaport', 'depart_time',
                                                    'arrive_time', 'bookticketitem__book_status')
    if ship_name:
        all_ticket_items = all_ticket_items.filter(ship_name=ship_name)
    if ship_date:
        all_ticket_items = all_ticket_items.filter(ship_date=ship_date)
    if ship_capacity:
        all_ticket_items = all_ticket_items.filter(ship_capacity=ship_capacity)
    if ship_booked_seats:
        all_ticket_items = all_ticket_items.filter(ship_booked_seats=ship_booked_seats)
    if ship_remained_seats:
        all_ticket_items = all_ticket_items.filter(ship_remained_seats=ship_remained_seats)
    if ship_price:
        all_ticket_items = all_ticket_items.filter(ship_price=ship_price)
    if depart_city:
        all_ticket_items = all_ticket_items.filter(depart_city=depart_city)
    if arrive_city:
        all_ticket_items = all_ticket_items.filter(arrive_city=arrive_city)
    if depart_seaport:
        all_ticket_items = all_ticket_items.filter(depart_seaport=depart_seaport)
    if arrive_seaport:
        all_ticket_items = all_ticket_items.filter(arrive_seaport=arrive_seaport)
    if depart_time:
        all_ticket_items = all_ticket_items.filter(depart_time=depart_time)
    if arrive_time:
        all_ticket_items = all_ticket_items.filter(arrive_time=arrive_time)
    if book_status:
        all_ticket_items = all_ticket_items.filter(bookticketitem__book_status=book_status)
    return render(request, 'MyTicketInfo.html', {'all_items': all_ticket_items})
