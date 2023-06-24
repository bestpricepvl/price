"""
Центральным моментом любого веб-приложения является обработка запроса, который отправляет пользователь.
В Django за обработку запроса отвечают представления или views.
По сути представления представляют функции обработки, которые принимают данные запроса в виде объекта request
и генерируют некоторый результат, который затем отправляется пользователю.
По умолчанию представления размещаются в приложении в файле views.py
"""
from django.http import HttpResponse # Класс HttpResponse из пакета django.http, который позволяет отправить текстовое содержимое.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .forms import UserRegistrationForm

from datetime import datetime

import datetime

from django.core import serializers
from django.http import JsonResponse
import json

from .models import Prices
from .forms import PricesForm

import csv
import xlwt
from io import BytesIO

from .serializers import PricesSerializer

from rest_framework import viewsets
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny


""" Групповые ограничения в представлениях (группа должна сущестовать) """
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')


""" Простой декоратор который позволяет узнать время выполнения функции """
import functools
import time

def view_function_timer(prefix=''):

    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            try:
                t0 = time.time()
                return func(*args, **kwargs)
            finally:
                t1 = time.time()
                print(
                    'View Function',
                    '({})'.format(prefix) if prefix else '',
                    func.__name__,
                    args[1:],
                    'Took',
                    '{:.2f}ms'.format(1000 * (t1 - t0)),
                    args[0].build_absolute_uri(),
                )
        return inner

    return decorator

def benchmark(func):
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end-start))
        return return_value
    return wrapper

# Засечка длительности запроса
#@view_function_timer()
@benchmark
def duration(request):
    prices = Prices.objects.all().order_by('product', 'cost')
    return render(request, "about.html")

""" Фукнция обработки запроса""" 
# В функции index() получаем все данные с помощью метода Prices.objects.all() и передаем их в шаблон index.html.
def index(request):
    prices = Prices.objects.all().order_by('product', 'cost')
    return render(request, "index.html", {"prices": prices})

class PricesViewSet(viewsets.ModelViewSet):
    queryset = Prices.objects.all()
    serializer_class = PricesSerializer
    permission_classes = [AllowAny]
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

# О приложении....
def about(request):
    return render(request, "about.html")

# Контакты
def contact(request):
    return render(request, "contact.html")

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Manager")
def create(request):
    if request.method == "POST":
        prices = Prices()
        prices.datep = request.POST.get("datep")
        prices.store = request.POST.get("store")
        prices.product = request.POST.get("product")
        prices.cost = request.POST.get("cost")
        prices.details = request.POST.get("details")
        prices.save()
        return HttpResponseRedirect("/")
    else:        
        pricesform = PricesForm(request.FILES)
        return render(request, "create.html", {"form": pricesform})
# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
# И вначале по этому идентификатору мы пытаемся найти объект с помощью метода Prices.objects.get(id=id).
# Поскольку в случае отсутствия объекта мы можем столкнуться с исключением Prices.DoesNotExist,
# то соответственно нам надо обработать подобное исключение, если вдруг будет передан несуществующий идентификатор.
# И если объект не будет найден, то пользователю возващается ошибка 404 через вызов return HttpResponseNotFound().
# Если объект найден, то обработка делится на две ветви.
# Если запрос POST, то есть если пользователь отправил новые изменненые данные для объекта, то сохраняем эти данные в бд и выполняем переадресацию на корень веб-сайта.
# Если запрос GET, то отображаем пользователю страницу edit.html с формой для редактирования объекта.
@login_required
@group_required("Manager")
def edit(request, id):
    try:
        prices = Prices.objects.get(id=id) 
        if request.method == "POST":
            prices.datep = request.POST.get("datep")
            prices.store = request.POST.get("store")
            prices.product = request.POST.get("product")
            prices.cost = request.POST.get("cost")
            prices.details = request.POST.get("details")
            prices.save()
            return HttpResponseRedirect("/")
        else:
            # Загрузка начальных данных
            pricesform = PricesForm(initial={'datep': prices.datep.strftime('%Y-%m-%d'), 'store': prices.store,'product': prices.product,'cost': prices.cost,'details': prices.details, })
            return render(request, "edit.html", {"form": pricesform})
    except Prices.DoesNotExist:
        return HttpResponseNotFound("<h2>Prices not found</h2>")
     
# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Manager")
def delete(request, id):
    try:
        prices = Prices.objects.get(id=id)
        prices.delete()
        return HttpResponseRedirect("/")
    except Person.DoesNotExist:
        return HttpResponseNotFound("<h2>Prices not found</h2>")

# Регистрационная форма
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})

def about(request):
    return render(request, "about.html")
 
def contact(request):
    return render(request, "contact.html")

# Запросы JSON 
def json(request, action):
    # Получить условия фильтрации
    id = request.GET.get("id", None)
    datep = request.GET.get("datep", None)
    store = request.GET.get("store", None)
    product = request.GET.get("product", None)
    cost = request.GET.get("cost", None)
    details = request.GET.get("details", None)
    # Словарь для условий
    conditions = dict()
    # Определения действия
    if action == "select":
        # Заполнение словаря для условия отбора
        if id is not None:
            conditions['id'] = id
        if datep is not None:
            conditions['datep'] = datep
        if store is not None:
            conditions['store'] = store
        if product is not None:
            conditions['product'] = product
        if cost is not None:
            conditions['cost'] = cost
        if details is not None:
            conditions['details'] = details
        print(action)
        print(conditions)
        # Фильтрация записей
        prices = Prices.objects.filter(**conditions)
        jsondata = serializers.serialize('json', prices)
        return HttpResponse(jsondata, content_type='application/json')
        # Grabs a QuerySet of dicts
        #qs = Prices.objects.all().values()
        # Convert the QuerySet to a List
        #list_of_dicts = list(qs)
        # Convert List of Dicts to JSON
        #data = json.dumps(list_of_dicts)
        #return HttpResponse(data, content_type="application/json")
    elif action == "like":
        # Заполнение словаря для условия отбора
        if id is not None:
            conditions['id'] = id
        if datep is not None:
            conditions['datep__icontains'] = datep
        if store is not None:
            conditions['store__icontains'] = store
        if product is not None:
            conditions['product__icontains'] = product
        if cost is not None:
            conditions['cost__icontains'] = cost
        if details is not None:
            conditions['details__icontains'] = details
        print(action)
        print(conditions)
        # Фильтрация записей
        prices = Prices.objects.filter(**conditions)
        jsondata = serializers.serialize('json', prices)
        return HttpResponse(jsondata, content_type='application/json')
    elif action == "store":
        # Список магазинов без дубликатов       
        prices = Prices.objects.distinct('store')
        jsondata = serializers.serialize('json', prices, fields=('store'))
        return HttpResponse(jsondata, content_type='application/json')
    elif action == "product":
        # Список магазинов без дубликатов       
        prices = Prices.objects.distinct('product')
        jsondata = serializers.serialize('json', prices, fields=('product'))
        return HttpResponse(jsondata, content_type='application/json')
    elif action == "insert":
        # Добавление новой записи
        if ((datep is not None) and (store is not None) and (product is not None) and (cost is not None)):
            prices = Prices()
            prices.datep = datep
            prices.store = store
            prices.product = product
            prices.cost = cost
            if details is not None:
                if details != 'None':
                    if details != '':                    
                        prices.details = details
            prices.save()
        return HttpResponseRedirect("/")
    elif action == "edit":
        # Изменение записи
        if id is not None:
            prices = Prices.objects.get(id=id)
            if datep is not None:
                prices.datep = datep
            if store is not None:
                prices.store = store
            if product is not None:
                prices.product = product
            if cost is not None:
                prices.cost = cost
            if details is not None:
                prices.details = details
            prices.save()
        return HttpResponseRedirect("/")    
    elif action == "delete":
        # Удаление записи
        if id is not None:
            prices = Prices.objects.get(id=id)
            prices.delete()
        return HttpResponseRedirect("/")    
    else:
        return HttpResponseRedirect("/")

"""
package com.example.bestprice;

import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLSession;
import com.google.gson.Gson;

class Product {
    public int pk;
    public String model;
    public Fields fields;
    public Product(){
    }
    class Fields {
        String datep;
        String store;
        String product;
        String cost;
        String details;
        public Fields(String datep, String store, String product, String cost, String details){
            this.datep = datep;
            this.store = store;
            this.product = product;
            this.cost = cost;
            this.details = details;
        }
    }
}


public class JSONData extends AsyncTask<String, Integer, ArrayList> {

    private final String TAG = "BestPrice";
    private final String KEY = "b6g54h6s1sf65g4wer14";      // Ключ
    HttpsURLConnection urlConnection;
    String server_name = "https://bestpricepvl.herokuapp.com/json/";
    String post_url = "";
    String answer = "";
    ArrayList getData;
    URL url;

    @Override
    protected void onPreExecute() {
        super.onPreExecute();
        Log.i(TAG, "onPreExecute");
    }

    @Override
    protected ArrayList doInBackground(String... params) {
        try {
            getData = new ArrayList<Map<String, String>>();

            // соберем линк для передачи новой строки
            //post_url = server_name + params[0] + "&key=" + KEY;
            post_url = server_name + params[0] ;
            Log.i(TAG, "post_url:\n" + post_url.toString());
            url = new URL(post_url);
            urlConnection = (HttpsURLConnection) url.openConnection();
            InputStream is = new BufferedInputStream(urlConnection.getInputStream());
            BufferedReader br = new BufferedReader(
                    new InputStreamReader(is, "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String bfr_st = null;
            while ((bfr_st = br.readLine()) != null) {
                sb.append(bfr_st);
            }
            answer = sb.toString();
            is.close(); // закроем поток
            br.close(); // закроем буфер
            // запишем ответ в БД ---------------------------------->
            if (answer != null && !answer.trim().equals("")) {
                Gson gson = new Gson();
                Product[] productArray = gson.fromJson(answer, Product[].class);
                for(Product product : productArray) {
                    Map<String, String> datanum = new HashMap<String, String>();
                    datanum.put("pk", String.valueOf(product.pk));
                    datanum.put("datep", String.valueOf(product.fields.datep));
                    datanum.put("store", String.valueOf(product.fields.store));
                    datanum.put("product", String.valueOf(product.fields.product));
                    datanum.put("cost", String.valueOf(product.fields.cost));
                    getData.add(datanum);
                }
                //Log.i(TAG, getData.get(0).toString());
            }
            else {
                // если ответ сервера пустой
                Log.i(TAG,"Ответ не содержит JSON!");
            }
        }
        catch (Exception ex) {
            Log.i(TAG,  "Ошибка: " + ex.toString());
        }
        finally {
            // закроем соединение
            urlConnection.disconnect();
            Log.i(TAG, "disconnect");
        }
        return getData;
    }
    @Override
    protected void onPostExecute(ArrayList res) {;
        super.onPostExecute(res);
        Log.i(TAG, "onPostExecute");
    }


}


public void showData(String filter)
    {
        try {
            // Включаем прогрессбар
            progressBar.setVisibility(View.VISIBLE);
            // Вывод записей запроса query в Адаптер
            JSONData jd = new JSONData();
            if (filter.equals("")) {
                jd.execute("select/");
            }
            else {
                //jd.execute("like?store=" + filter + "&product=" + filter);
                jd.execute("like?product=" + filter);
            }

            SimpleAdapter adapter = new SimpleAdapter(getApplicationContext(), jd.get(),
                    R.layout.list_view_prices, new String[]{ "pk", "store", "product","cost"},
                    new int[]{R.id.tvId, R.id.tvStore, R.id.tvProduct, R.id.tvCost});
            listData.setAdapter(adapter);


            // Выключаем прогрессбар
            progressBar.setVisibility(View.GONE);
        }
        catch (Exception ex){
            // Вывод сообщения об ошибке
            Log.i(TAG, "Error " + ex.toString());
        }
    }


    try
                        {
                            if (Id==0){
                                // Преобразование даты в формат
                                String ymd = tvPurchase_date.getText().toString();
                                // Новая запись
                                JSONData jd = new JSONData();
                                jd.execute("insert/" +
                                        "?datep=" + ymd.substring(6) + "-" + ymd.substring(3,5) + "-" + ymd.substring(0,2) +
                                        "&store="  + URLEncoder.encode(actvStore.getText().toString(), "UTF-8") +
                                        "&product=" + URLEncoder.encode(actvProduct.getText().toString(), "UTF-8") +
                                        "&cost=" + URLEncoder.encode(etCost.getText().toString(), "UTF-8") +
                                        "&details=" + URLEncoder.encode(etDetails.getText().toString(), "UTF-8") );
                                //Log.i(TAG, jd.get().toString());
                            }
                            else {
                                // Изменени записи
                                // Преобразование даты в формат
                                String ymd = tvPurchase_date.getText().toString();
                                // Новая запись
                                JSONData jd = new JSONData();
                                jd.execute("edit/" +
                                        "?datep=" + ymd.substring(6) + "-" + ymd.substring(3,5) + "-" + ymd.substring(0,2) +
                                        "&store="  + URLEncoder.encode(actvStore.getText().toString(), "UTF-8") +
                                        "&product=" + URLEncoder.encode(actvProduct.getText().toString(), "UTF-8") +
                                        "&cost=" + URLEncoder.encode(etCost.getText().toString(), "UTF-8") +
                                        "&details=" + URLEncoder.encode(etDetails.getText().toString(), "UTF-8") +
                                        "&id=" + Long.toString(Id) );
                                //Log.i(TAG, jd.get().toString());
                            }
                        } catch (Exception ex) {
                            //Log.i(TAG, ex.toString());
                            Toast.makeText(getApplicationContext(), ex.toString(), Toast.LENGTH_LONG).show();
                        }
"""
# Экспорт в csv
def export_prices_csv(request):    
    response = HttpResponse(content_type='text/csv')
    response.write(u'\ufeff'.encode('utf8'))
    response['Content-Disposition'] = 'attachment; filename="prices.csv"'
    writer = csv.writer(response)
    writer.writerow(['datep', 'store', 'product', 'cost', 'details'])
    pcices = Prices.objects.all().values_list('datep', 'store', 'product', 'cost', 'details')
    for pcice in pcices:
        writer.writerow(pcice)
    return response

# Экспорт в Excel
def export_prices_excel(request): 
    # Create a HttpResponse object and set its content_type header value to Microsoft excel.
    response = HttpResponse(content_type='application/vnd.ms-excel') 
    # Set HTTP response Content-Disposition header value. Tell web server client the attached file name is students.xls.
    response['Content-Disposition'] = 'attachment;filename=prices.xls' 
    # Create a new Workbook file.
    work_book = xlwt.Workbook(encoding = 'utf-8') 
    # Create a new worksheet in the above workbook.
    work_sheet = work_book.add_sheet(u'Prices Info')
    # Maintain some worksheet styles，style_head_row, style_data_row, style_green, style_red
    # This style will be applied to worksheet head row.
    style_head_row = xlwt.easyxf("""    
        align:
          wrap off,
          vert center,
          horiz center;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        font:
          name Arial,
          colour_index white,
          bold on,
          height 0xA0;
        pattern:
          pattern solid,
          fore-colour 0x19;
        """
    )
    # Define worksheet data row style. 
    style_data_row = xlwt.easyxf("""
        align:
          wrap on,
          vert center,
          horiz left;
        font:
          name Arial,
          bold off,
          height 0XA0;
        borders:
          left THIN,
          right THIN,
          top THIN,
          bottom THIN;
        """
    )
    # Set data row date string format.
    style_data_row.num_format_str = 'dd/mm/yyyy'
    # Define a green color style.
    style_green = xlwt.easyxf(" pattern: fore-colour 0x11, pattern solid;")
    # Define a red color style.
    style_red = xlwt.easyxf(" pattern: fore-colour 0x0A, pattern solid;")
    # Generate worksheet head row data.
    work_sheet.write(0,0, 'datep', style_head_row) 
    work_sheet.write(0,1, 'store', style_head_row) 
    work_sheet.write(0,2, 'product', style_head_row) 
    work_sheet.write(0,3, 'cost', style_head_row) 
    work_sheet.write(0,4, 'details', style_head_row) 
    # Generate worksheet data row data.
    row = 1 
    for prices in Prices.objects.all():
        work_sheet.write(row,0, prices.datep.strftime('%d.%m.%Y'), style_data_row)
        work_sheet.write(row,1, prices.store, style_data_row)
        work_sheet.write(row,2, prices.product, style_data_row)
        work_sheet.write(row,3, '{:.0f}'.format(prices.cost), style_data_row)
        work_sheet.write(row,4, prices.details, style_data_row)
        row=row + 1 
    # Create a StringIO object.
    output = BytesIO()
    
    # Save the workbook data to the above StringIO object.
    work_book.save(output)
    # Reposition to the beginning of the StringIO object.
    output.seek(0)
    # Write the StringIO object's value to HTTP response to send the excel file to the web server client.
    response.write(output.getvalue()) 
    return response
