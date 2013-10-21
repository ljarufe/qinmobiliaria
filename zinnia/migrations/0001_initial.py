# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('zinnia_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['zinnia.Category'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('zinnia', ['Category'])

        # Adding model 'Entry'
        db.create_table('zinnia_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('excerpt', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('featured', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comment_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('pingback_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('start_publication', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('end_publication', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2042, 3, 15, 0, 0))),
            ('login_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('template', self.gf('django.db.models.fields.CharField')(default='zinnia/entry_detail.html', max_length=250)),
        ))
        db.send_create_signal('zinnia', ['Entry'])

        # Adding M2M table for field fotos on 'Entry'
        db.create_table('zinnia_entry_fotos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('foto', models.ForeignKey(orm['common.foto'], null=False))
        ))
        db.create_unique('zinnia_entry_fotos', ['entry_id', 'foto_id'])

        # Adding M2M table for field videos on 'Entry'
        db.create_table('zinnia_entry_videos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('video', models.ForeignKey(orm['common.video'], null=False))
        ))
        db.create_unique('zinnia_entry_videos', ['entry_id', 'video_id'])

        # Adding M2M table for field proyectos on 'Entry'
        db.create_table('zinnia_entry_proyectos', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('proyecto', models.ForeignKey(orm['proyectos.proyecto'], null=False))
        ))
        db.create_unique('zinnia_entry_proyectos', ['entry_id', 'proyecto_id'])

        # Adding M2M table for field categories on 'Entry'
        db.create_table('zinnia_entry_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('category', models.ForeignKey(orm['zinnia.category'], null=False))
        ))
        db.create_unique('zinnia_entry_categories', ['entry_id', 'category_id'])

        # Adding M2M table for field related on 'Entry'
        db.create_table('zinnia_entry_related', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('to_entry', models.ForeignKey(orm['zinnia.entry'], null=False))
        ))
        db.create_unique('zinnia_entry_related', ['from_entry_id', 'to_entry_id'])

        # Adding M2M table for field authors on 'Entry'
        db.create_table('zinnia_entry_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('zinnia_entry_authors', ['entry_id', 'user_id'])

        # Adding M2M table for field sites on 'Entry'
        db.create_table('zinnia_entry_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['zinnia.entry'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('zinnia_entry_sites', ['entry_id', 'site_id'])

    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('zinnia_category')

        # Deleting model 'Entry'
        db.delete_table('zinnia_entry')

        # Removing M2M table for field fotos on 'Entry'
        db.delete_table('zinnia_entry_fotos')

        # Removing M2M table for field videos on 'Entry'
        db.delete_table('zinnia_entry_videos')

        # Removing M2M table for field proyectos on 'Entry'
        db.delete_table('zinnia_entry_proyectos')

        # Removing M2M table for field categories on 'Entry'
        db.delete_table('zinnia_entry_categories')

        # Removing M2M table for field related on 'Entry'
        db.delete_table('zinnia_entry_related')

        # Removing M2M table for field authors on 'Entry'
        db.delete_table('zinnia_entry_authors')

        # Removing M2M table for field sites on 'Entry'
        db.delete_table('zinnia_entry_sites')

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'common.departamento': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'Departamento'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'common.foto': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Foto'},
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imagen': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'common.provincia': {
            'Meta': {'ordering': "['nombre']", 'object_name': 'Provincia'},
            'departamento': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Departamento']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'common.telefono': {
            'Meta': {'object_name': 'Telefono'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'numero': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'tipo_telefono': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.TipoTelefono']"})
        },
        'common.tipotelefono': {
            'Meta': {'object_name': 'TipoTelefono'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'common.video': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Video'},
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'common.viewport': {
            'Meta': {'object_name': 'ViewPort'},
            'high_latitud': ('django.db.models.fields.FloatField', [], {}),
            'high_longitud': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'low_latitud': ('django.db.models.fields.FloatField', [], {}),
            'low_longitud': ('django.db.models.fields.FloatField', [], {}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'proyectos.proyecto': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Proyecto'},
            'area': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'area_construida': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'avance': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'clientes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'proyectos'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['usuarios.Cliente']"}),
            'corredores': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['usuarios.Corredor']", 'null': 'True', 'blank': 'True'}),
            'descripcion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'estado': ('django.db.models.fields.CharField', [], {'default': "u'B'", 'max_length': '1'}),
            'fecha_fin': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fecha_inicio': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'foto_principal': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'fotos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['common.Foto']", 'null': 'True', 'blank': 'True'}),
            'gmaps_image': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduccion': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'latitud': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'logo_watermark': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'longitud': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pdf': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'precio_maximo': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'precio_minimo': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'provincia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Provincia']", 'null': 'True', 'blank': 'True'}),
            'relevancia': ('django.db.models.fields.CharField', [], {'default': "u'3'", 'max_length': '1'}),
            'resumen': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rubro': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['proyectos.Rubro']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "u'nombre_proyecto'", 'max_length': '100'}),
            'tipo_contrato': ('django.db.models.fields.CharField', [], {'default': "u'V'", 'max_length': '1'}),
            'usuarios': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['common.Video']", 'null': 'True', 'blank': 'True'}),
            'web_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'proyectos.rubro': {
            'Meta': {'object_name': 'Rubro'},
            'descripcion': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nombre': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "u'nombre_rubro'", 'max_length': '100'}),
            'texto_email': ('django.db.models.fields.TextField', [], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'usuarios.cliente': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Cliente'},
            'areas_interes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['common.ViewPort']", 'null': 'True', 'blank': 'True'}),
            'clave_activacion': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'corredor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['usuarios.Corredor']", 'null': 'True', 'blank': 'True'}),
            'direccion': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provincia': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['common.Provincia']", 'null': 'True', 'blank': 'True'}),
            'rastrear_proyectos': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'recibir_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rubros': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['proyectos.Rubro']", 'null': 'True', 'blank': 'True'}),
            'telefonos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['common.Telefono']", 'null': 'True', 'blank': 'True'}),
            'tipo': ('django.db.models.fields.CharField', [], {'default': "'Q'", 'max_length': '1'}),
            'usuario': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'usuarios.corredor': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Corredor'},
            'auto_asignar': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'codigo': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usuario': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'zinnia.category': {
            'Meta': {'ordering': "['title']", 'object_name': 'Category'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['zinnia.Category']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'zinnia.entry': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Entry'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'entries'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'entries'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['zinnia.Category']"}),
            'comment_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'end_publication': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2042, 3, 15, 0, 0)'}),
            'excerpt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fotos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['common.Foto']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'pingback_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'proyectos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['proyectos.Proyecto']", 'symmetrical': 'False'}),
            'related': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_rel_+'", 'null': 'True', 'to': "orm['zinnia.Entry']"}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'entries'", 'symmetrical': 'False', 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'start_publication': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'template': ('django.db.models.fields.CharField', [], {'default': "'zinnia/entry_detail.html'", 'max_length': '250'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['common.Video']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['zinnia']