from django.db import models
from django.contrib import admin
import logging
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex
from rest_framework import serializers


logger = logging.getLogger(__name__)


class TenderOwner(models.Model):
    short_name = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    #owner_id = models.IntegerField(blank=True, unique=True)
    #ARMP keeps changing short_name so in order not to miss entries, they can be collected first
    #then re-assigned later
    owner_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ["owner_id"]

    def __str__(self):
        return "{}, {}".format(self.owner_id, self.short_name)


class TenderOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderOwner
        exclude = ('id',)


class ArmpEntry(models.Model):

    owner = models.ForeignKey(TenderOwner, blank=True, null=True)
    title = models.TextField(null=True, blank=True)
    link = models.URLField(verbose_name="primary source")
    publication_type = models.CharField(max_length=20, blank=True, null=True)
    verbose_type = models.CharField(max_length=50, blank=True, null=True)
    publication_datetime = models.DateTimeField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    expiration_time = models.TimeField(blank=True, null=True)
    dao_link = models.URLField(verbose_name="DAO link", blank=True)
    original_link = models.URLField(verbose_name="Original Document link", blank=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    content = models.TextField(null=True, blank=True)
    extra_content = models.TextField(null=True, blank=True)
    projected_cost = models.BigIntegerField(null=True, blank=True)
    final_cost = models.BigIntegerField(null=True, blank=True)

    cost = models.BigIntegerField(null=True, blank=True)

    region = models.CharField(max_length=50, blank=True, null=True)
    ao_id = models.CharField(max_length=50, blank=True, null=True)
    own_id = models.CharField(max_length=50, blank=True, null=True)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        # TODO this works????
        # x=ArmpEntry()
        # x.save()
        # x=ArmpEntry()
        # x.save()

        unique_together = ("owner", "link", "publication_type", "verbose_type")
        indexes = [

            GinIndex(fields=['search_vector']),

        ]
        #ordering = ["-publication_datetime"]

    def __str__(self):
        return "{}, {}".format(self.owner, self.title)

    def save(self, *args, **kwargs):

        if not self.cost:
            if self.final_cost:
                self.cost = self.final_cost
            else:
                self.cost = self.projected_cost

        super(ArmpEntry, self).save(*args, **kwargs)

        #https://blog.lotech.org/postgres-full-text-search-with-django.html
        if 'update_fields' not in kwargs or 'search_vector' not in kwargs['update_fields']:
            #instance = self._meta.default_manager.with_documents().get(pk=self.pk)
            self.search_vector = SearchVector('title', 'content', config='french_unaccent')
            self.save(update_fields=['search_vector'])


class TenderOwnerAdmin(admin.ModelAdmin):

    list_display = ('owner_id', 'short_name', 'full_name')
    search_fields = ('owner_id', 'short_name', 'full_name')


admin.site.register(TenderOwner, TenderOwnerAdmin)


class ArmpEntryAdmin(admin.ModelAdmin):

    list_display = ('owner', 'publication_datetime', 'cost', 'publication_type', 'title', 'link')
    search_fields = ('title', 'content')
    #search_fields = ('search_vector',)
    list_filter = ('owner', 'publication_datetime', 'publication_type')
    #filter_horizontal = ('supervisors', 'committee')
    #raw_id_fields = ('author',)


admin.site.register(ArmpEntry, ArmpEntryAdmin)

#
# with open("tender/owner-short-full-name.csv", "r", encoding="utf-8") as f:
#     ...: c = csv.DictReader(f, fieldnames=list(owner_list[0].keys()))
#     ...: next(c, None)
#     ...:
#     for row in c:
#         ...: print(row)
#     ...: tender = TenderOwner()
#     ...: tender.owner_id = int(row["owner_id"])
#     ...: tender.short_name = row["owner_short"]
#     ...: tender.full_name = row["owner_full"]
#     ...: tender.save()


# from datetime import datetime
#gzt = timezone('Africa/Douala')
#from pytz import timezone
#     ...:
#     ...: for f_name in l:
#     ...:     with open("tender/parsed/"+ f_name, "r", encoding="utf-8") as f:
#     ...:         fieldname = ["owner_id","owner_short","region","type","publication_type","cost","publish_date_time","end_date","end_time","title","deta
#     ...: ils","tf","dao"]
#     ...:         r = csv.DictReader(f, delimiter='\t')
#     ...:         next(r, None)
#     ...:         for row in r:
#     ...:             try:
#     ...:                 tender = ArmpEntry()
#     ...:                 owner = TenderOwner.objects.get(owner_id=row["owner_id"])
#     ...:                 tender.owner=owner
#     ...:                 tender.title = row["title"]
#     ...:                 tender.link = row["details"]
#     ...:                 tender.dao_link = row["dao"]
#     ...:                 tender.publication_datetime = gzt.localize(datetime.strptime(row["publish_date_time"], "%d-%m-%Y %H:%M:%S"))
#     ...:                 a = gzt.localize(datetime.strptime(row['end_date'] + " " + row['end_time'], "%d-%m-%Y %H:%M:%S"))
#     ...:                 tender.expiration_date = a.date()
#     ...:                 tender.expiration_time = a.time()
#     ...:                 if row["cost"]:
#     ...:                     tender.projected_cost = int(row["cost"])
#     ...:                 tender.verbose_type = row["type"]
#     ...:                 tender.publication_type = row["publication_type"]
#     ...:                 tender.region = row['region']
#     ...:                 tender.save()
#     ...:             except Exception as e:
#     ...:                 print(e)



# def clean_extra_space(in_content: str) -> str:
#     out_content = re.sub("[]")