from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django_tables2 import RequestConfig


from contacts.tables import ContactTable
from contacts.models import Category, Contact
from contacts.forms import CategoryFormSet

# SMS script
from atex.atxscript import Sender


class IndexView(View):
    def get(self, request):
        # Collect statistics
        # Total Contacts
        t_contacts = Contact.objects.all().count()

        # Total Categories
        t_categories = Category.objects.all().count()

        # Grab all the categories from db
        cat_queryset = Category.objects.all()

        # Grab contacts list of the first category
        first_category = Category.objects.all()[0]
        contact_list_table = ContactTable(first_category.contact_set.all())
        RequestConfig(request).configure(contact_list_table)

        context = {
            'contact_list_table': contact_list_table,
            'categories': cat_queryset,
            't_categories': t_categories,
            't_contacts': t_contacts
        }
        return render(request, 'contacts/index.html', context)


class ContactListView(View):
    def post(self, request):
        # Get selected category
        selected_cat = request.POST['category']

        category = Category.objects.get(pk=selected_cat)

        contact_list_table = ContactTable(category.contact_set.all())
        RequestConfig(request).configure(contact_list_table)

        # Get Category list
        cat_queryset = Category.objects.all()
        cat_queryset = cat_queryset.exclude(pk=selected_cat)

        # Get selected category name
        active_cat = Category.objects.get(pk=selected_cat)

        # Create a context dictionary
        context = {
            'contact_list_table': contact_list_table,
            'categories': cat_queryset,
            'active_cat': active_cat
        }
        return render(request, 'contacts/index.html', context)


class CategoryListView(ListView):
    model = Category
    template_name = 'contacts/category.html'


class CategoryDetailVew(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'contacts/category_detail.html'


class AddCategoryView(View):

    def get(self, request):
        formset = CategoryFormSet()
        return render(request, 'contacts/add_category.html', {'formset': formset})

    def post(self, request):
        formset = CategoryFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save()
            for instance in instances:
                instance.save()
            # Query for cats
            category_list = Category.objects.all()
            context = {
                'msg': 'Changes Saved Successful',
                'category_list': category_list
            }
            return render(request, 'contacts/category.html', context)

        else:
            msg = "errors"

        return render(request, 'contacts/add_category.html', {'formset': formset, 'msg': msg})


class AddContactView(View):
    def get(self, request):
        category_list = Category.objects.all()
        context = {
            'category_list': category_list
        }
        return render(request, 'contacts/add_contact.html', context)

    def post(self, request):
        category_id = request.POST['category']

        try:
            # Check if category exists
            category = Category.objects.get(pk=category_id)

            name = request.POST['name']
            phone = request.POST['phone']

            # Save to datebase
            contact = Contact(name=name, phone=phone, category=category)
            contact.save()

            return redirect('category-detail', category_id)

        except Category.DoesNotExist:
            context = {
                'error': 'Category Does Not Exist'
            }
            return render(request, 'contacts/add_contact.html', context)


class SendSMSView(View):
    def post(self, request):
        pks = request.POST.getlist('selection')
        selected_contacts = Contact.objects.filter(pk__in=pks)

        # Grab the message
        message = request.POST['message']

        # Empty Recipients List
        recipients = ''

        for contact_name in selected_contacts:
            phone_number = Contact.objects.get(name=contact_name).phone

            # //TODO: sendmessage script goes here
            number = str(phone_number)
            number = "0"+number
            recipients = recipients + number
            recipients = recipients + ','

            # sender.sendsms(phone_number, message)
            # sender = Sender()
        # Remove last coma
        recipients = recipients[:-1]
        print(recipients)
        # Grab all the categories from db
        cat_queryset = Category.objects.all()

        # Grab contacts list of the first category
        first_category = Category.objects.all()[0]
        contact_list_table = ContactTable(first_category.contact_set.all())
        RequestConfig(request).configure(contact_list_table)

        context = {
            'contact_list_table': contact_list_table,
            'categories': cat_queryset
        }
        return render(request, 'contacts/index.html', context)


class HistoryView(View):
    def get(self, request):
        return render(request, 'contacts/history.html')
