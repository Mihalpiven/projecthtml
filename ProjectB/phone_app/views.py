from ctypes.wintypes import tagSIZE
from django.shortcuts import render
from .models import Contacts, Applications, Appusers
from django.db import connection


def index(request):
    return render(request, 'index.html')

def dictfetchall(cursor):
    # Return all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def query_results_view(request):
    print("Query Results View Accessed")
    results = {}

    # Query 1
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT AU2.aName, ROUND(CAST(AVG(1.0 * AU2.rating) AS FLOAT), 2) AS grade
            FROM AppUsers AU2
            WHERE AU2.aName IN (SELECT aName FROM HaifaApp)
              AND AU2.aName IN (
                  SELECT AU3.aName
                  FROM AppUsers AU3
                  GROUP BY AU3.aName
                  HAVING COUNT(*) > 10
              )
            GROUP BY AU2.aName
            ORDER BY grade DESC;
        """)
        query1_results = dictfetchall(cursor)
        results['query1'] = query1_results

    # Query 2
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT C1.cName AS name, C1.phone AS phone, ILAC.leadAppCount AS apps_num
            FROM Contacts C1
            INNER JOIN InstalledLeadAppsCount ILAC ON C1.cName = ILAC.cName
            WHERE C1.city = 'Haifa'
            ORDER BY ILAC.leadAppCount DESC, C1.cName;
        """)
        query2_results = dictfetchall(cursor)
        results['query2'] = query2_results

    # Query 3
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT IC1.city AS city, IC1.aName AS name, IC1.count AS installations_num
            FROM InstallationCount IC1
            WHERE IC1.count = (SELECT MAX(count)
                               FROM InstallationCount IC2
                               WHERE IC1.city = IC2.city
                               GROUP BY IC2.city)
            ORDER BY IC1.city, IC1.aName;
        """)
        query3_results = dictfetchall(cursor)
        results['query3'] = query3_results

    return render(request, 'query_results.html', {'results': results})
'''

def query_results_view(request):
    """
    Render the new page.
    """
    query1_res = query1(request)
    query2_res = query2(request)
    query3_res = query3(request)

    results = {
        'query1': query1_res,
        'query2': query2_res,
        'query3': query3_res,
    }
    return render(request, 'query_results.html', results)
    
    '''

def add_new_app_view(request):
    message = None
    existing_apps = Applications.objects.values_list('aname', flat=True).distinct()
    categories = Applications.objects.values_list('acategory', flat=True).distinct()

    if request.method == 'POST' and request.POST:
        app_name = request.POST.get('app_name', '')
        app_category = request.POST.get('app_category', '')
        app_size = request.POST.get('app_size', '')
        if app_name in Applications.objects.values_list('aname', flat=True).distinct():
            message = f"The app '{app_name}' already exists in the system."

        try:
            app_size = int(app_size)
            if app_size < 100 or app_size > 200:
                message = f"The app size '{app_size}' is out of range."
        except ValueError as e:
            message = f"The app size '{app_size}' must be a number."
        else:
            #bc of the if beforehand we only enter the else if there is no such app already in the system
            new_app = Applications(aname=app_name, acategory=app_category, asize=app_size, isinstalled=False)
            new_app.save()

    context = {
        'categories': categories,
        'existing_apps': existing_apps,
        'message': message,
    }

    return render(request, 'add_new_app.html', context)


def install_app_view(request):
    message = None
    available_space = 1800  # Total available space
    installed_apps = Applications.objects.filter(isinstalled=True).distinct()
    uninstalled_apps = Applications.objects.filter(isinstalled=False).distinct()

    # Calculate the remaining available space
    for app in installed_apps:
        available_space -= int(app.asize)

    if request.method == 'POST' and request.POST:
        app_name = request.POST.get('uninstalled_apps')  # Get the selected app name
        app = Applications.objects.filter(aname=app_name).first() #first is used to get the first app

        if app:  # Ensure the app exists and is uninstalled
            if app.asize > available_space:
                message = f"The app size '{app.asize}' MB exceeds the available space."
            else:
                app.isinstalled = True
                app.save()  # Save changes to the database
                available_space -= app.asize
                message = f"'{app.aname}' has been successfully installed."
        else:
            message = "The selected app could not be found or is already installed."
    uninstalled_apps = Applications.objects.filter(isinstalled=False).distinct()
    context = {
        'uninstalled_apps': uninstalled_apps,  # Pass queryset to the template
        'available_space': available_space,  # Pass available space to the template
        'message': message,  # Pass any message to the template
    }

    return render(request, 'install_app.html',context)


def delete_app_view(request):
    """
    Render the new page.
    """
    message = None
    total_size = 1800
    available_space = 1800  # Total available space
    installed_apps = Applications.objects.filter(isinstalled=True).distinct()


    # Calculate the remaining available space
    for app in installed_apps:
        available_space -= int(app.asize)

    if request.method == 'POST' and request.POST:
        app_name = request.POST.get('installed_apps')  # Get the selected app name
        app = Applications.objects.filter(aname=app_name).first() #first is used to get the first app

        if app:# Ensure the app exists and is uninstalled
            if app.asize > total_size:
                message = f"The app size '{app.asize}' MB exceeds the total size."
            else:
                app.isinstalled = False
                app.save()  # Save changes to the database
                available_space += app.asize
                message = f"'{app.aname}' has been successfully uninstalled."
        else:
            message = "The selected app could not be found or is already uninstalled."

    installed_apps = Applications.objects.filter(isinstalled=True).distinct()

    context = {
         'installed_apps': installed_apps,  # Pass queryset to the template
        'available_space': available_space,  # Pass available space to the template
        'message': message,  # Pass any message to the template
    }
    return render(request, 'delete_app.html',context)
