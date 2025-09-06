from django.contrib import admin
from .models import Thread, ThreadParticipant, Message

# Register your models here.
class ThreadParticipantInline(admin.TabularInline): # inline para participantes
    model = ThreadParticipant
    extra = 0

class MessageInline(admin.TabularInline): # inline para mensagens
    model = Message
    extra = 0
    readonly_fields = ('author', 'body', 'created_at')
    fields = ('author', 'body', 'created_at')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin): # admin para threads
    list_display = (
        'id',
        'participants_list',
        'last_message_excerpt',
        'messages_count',
        'updated_at',
        'created_at',
    )
    search_fields = ('participants__username', 'participants__first_name', 'participants__last_name')
    inlines = [ThreadParticipantInline, MessageInline]

    def participants_list(self, obj):
        return ", ".join(obj.participants.values_list('username', flat=True))
    participants_list.short_description = 'Participants'

    def last_message_excerpt(self, obj):
        msg = obj.last_message
        return msg.short_body() if msg else '—'
    last_message_excerpt.short_description = 'Last message'

@admin.register(Message) # admin para mensagens
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'author', 'short_body', 'created_at')
    search_fields = ('body', 'author__username')
    list_select_related = ('thread', 'author')

@admin.register(ThreadParticipant) # admin para participantes
class ThreadParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread', 'user', 'joined_at')
    search_fields = ('user__username',)
    list_select_related = ('thread', 'user')