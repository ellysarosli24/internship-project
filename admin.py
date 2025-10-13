from django.contrib import admin
from .models import Video, Service, Payment, TeamMember, GalleryImage, BlogCategory, BlogPost, Kursus, Peserta
from django.utils.html import format_html
from django.utils.text import slugify
from django.http import HttpResponseRedirect
from django.utils import timezone

@admin.register(Video)
class TutorialVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_url', 'created_at')
    readonly_fields = ('get_youtube_id',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')  # Fields to display in the table
    list_filter = ('category',)  # Filter by category
    search_fields = ('name', 'category')  # Search functionality
    list_editable = ('price',)  # Allow editing price directly in the list view

@admin.register(Payment)  # Optional: Register Payment if you want to manage it in admin
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('service', 'amount', 'is_success', 'created_at', 'customer_email')
    list_filter = ('is_success', 'service__category')  # Filter by payment status or service category
    search_fields = ('customer_email', 'service__name')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'is_active', 'order']
    list_filter = ['is_active', 'position']
    search_fields = ['name', 'position', 'bio']
    list_editable = ['is_active', 'order']
    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'bio')
        }),
        ('Media', {
            'fields': ('photo',)
        }),
        ('Settings', {
            'fields': ('is_active', 'order'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'name')
    

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'title', 'is_active', 'order', 'upload_date']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'upload_date']
    search_fields = ['title', 'description']
    readonly_fields = ['upload_date']
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'description')
        }),
        ('Settings', {
            'fields': ('is_active', 'order'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('upload_date',),
            'classes': ('collapse',)
        })
    )
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail.short_description = 'Thumbnail'


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'published_date', 'is_published', 'has_image']
    list_filter = ['categories', 'is_published', 'published_date']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['categories']
    
    # Custom method untuk check jika ada gambar
    def has_image(self, obj):
        return bool(obj.featured_image)
    has_image.boolean = True
    has_image.short_description = 'Ada Gambar'

admin.site.register(Kursus)
admin.site.register(Peserta)

@admin.action(description='Export selected courses to Excel')
def export_selected_kursus(modeladmin, request, queryset):
    from .management.commands.export_kursus import Command
    command = Command()
    filename = f"kursus_export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    command.handle(filename=filename)
    return HttpResponseRedirect(f'/download/{filename}')

class KursusAdmin(admin.ModelAdmin):
    actions = [export_selected_kursus]