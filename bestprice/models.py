from django.db import models

# Модели отображают информацию о данных, с которыми вы работаете.
# Они содержат поля и поведение ваших данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным

# Цены datep (Дата), store (Место покупки), product, (Товар), cost (Цена), details (Детали)
class Prices(models.Model):
    # Читабельное имя поля (метка, label). Каждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
    # первым аргументом принимает необязательное читабельное название.
    # Если оно не указано, Django самостоятельно создаст его, используя название поля, заменяя подчеркивание на пробел.
    # null - Если True, Django сохранит пустое значение как NULL в базе данных. По умолчанию - False.
    # blank - Если True, поле не обязательно и может быть пустым. По умолчанию - False.
    # Это не то же что и null. null относится к базе данных, blank - к проверке данных.
    # Если поле содержит blank=True, форма позволит передать пустое значение.
    # При blank=False - поле обязательно.    
    datep = models.DateTimeField("Дата")
    store = models.CharField("Место покупки", max_length=128)
    product = models.CharField("Продукт (товар)", max_length=256)
    cost = models.DecimalField("Цена", max_digits=6, decimal_places=2)
    details = models.TextField("Подробности", blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'prices'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['datep']),
            models.Index(fields=['store']),
            models.Index(fields=['product']),
        ]
    
    
